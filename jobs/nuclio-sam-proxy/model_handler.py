"""Nuclio handler for SAM proxy — CVAT interactor protocol.

Translates CVAT interactor format to SAM server API,
converts SAM binary masks to CVAT polygon format.
Routes directly to SAM GPU server on OnyxCortex.
"""

import json
import logging
import os

import cv2
import numpy as np
import requests

SAM_GPU_URL = os.environ.get("SAM_GPU_URL", "http://10.0.0.26:9470")
SAM_MODEL_NAME = os.environ.get("SAM_MODEL_NAME", "vit_b")
TIMEOUT = 60.0

logger = logging.getLogger(__name__)

# Track which model was last switched to avoid redundant calls
_last_switched_model = None


def init_context(context):
    """Initialize handler context."""
    context.logger.info(f"SAM Nuclio proxy -> {SAM_GPU_URL} (model: {SAM_MODEL_NAME})")


def _ensure_model():
    """Switch SAM model if needed (idempotent)."""
    global _last_switched_model
    if _last_switched_model == SAM_MODEL_NAME:
        return
    try:
        resp = requests.post(
            f"{SAM_GPU_URL}/switch-model",
            json={"model": SAM_MODEL_NAME},
            timeout=30.0,
        )
        if resp.status_code == 200:
            _last_switched_model = SAM_MODEL_NAME
            logger.info(f"SAM model switched to {SAM_MODEL_NAME}")
    except Exception as e:
        logger.warning(f"Model switch failed: {e}")


def _cvat_to_sam(cvat_data):
    """Translate CVAT interactor fields to SAM server fields.

    CVAT sends: image, pos_points, neg_points, obj_bbox
    SAM expects: image_base64, points, negative_points, box
    """
    sam_request = {
        "image_base64": cvat_data.get("image", ""),
    }

    pos_points = cvat_data.get("pos_points", [])
    if pos_points:
        sam_request["points"] = [[int(p[0]), int(p[1])] for p in pos_points]

    neg_points = cvat_data.get("neg_points", [])
    if neg_points:
        sam_request["negative_points"] = [[int(p[0]), int(p[1])] for p in neg_points]

    # CVAT obj_bbox is [x, y, w, h], SAM box is [x1, y1, x2, y2]
    bbox = cvat_data.get("obj_bbox")
    if bbox and len(bbox) == 4:
        x, y, w, h = bbox
        sam_request["box"] = [int(x), int(y), int(x + w), int(y + h)]

    return sam_request


def _mask_to_polygon(mask_2d):
    """Convert binary mask array to polygon coordinates for CVAT.

    Args:
        mask_2d: 2D list/array of 0s and 1s (H x W).

    Returns:
        List of [x, y] coordinate pairs forming the polygon.
    """
    mask_uint8 = np.array(mask_2d, dtype=np.uint8)
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    if not contours:
        return []

    # Take the largest contour
    largest = max(contours, key=cv2.contourArea)

    # Flatten to [[x1,y1],[x2,y2],...] format with integer coords
    polygon = [[int(pt[0]), int(pt[1])] for pt in largest.reshape(-1, 2)]
    return polygon


def handler(context, event):
    """CVAT interactor handler: receive points, return polygon mask.

    CVAT calls this with image + interaction points.
    We forward to SAM server, convert the mask to polygon, return to CVAT.
    """
    try:
        # Parse CVAT request
        if isinstance(event.body, bytes):
            cvat_data = json.loads(event.body.decode())
        elif isinstance(event.body, str):
            cvat_data = json.loads(event.body)
        elif isinstance(event.body, dict):
            cvat_data = event.body
        else:
            cvat_data = json.loads(str(event.body))

        context.logger.info(
            f"CVAT request: pos_points={len(cvat_data.get('pos_points', []))}, "
            f"neg_points={len(cvat_data.get('neg_points', []))}"
        )

        # Ensure correct model is active
        _ensure_model()

        # Translate CVAT format to SAM format
        sam_request = _cvat_to_sam(cvat_data)

        # Call SAM server
        resp = requests.post(
            f"{SAM_GPU_URL}/api/interact",
            json=sam_request,
            timeout=TIMEOUT,
        )

        if resp.status_code != 200:
            context.logger.error(f"SAM error: {resp.status_code} - {resp.text[:200]}")
            return context.Response(
                body=json.dumps({"error": f"SAM returned {resp.status_code}"}),
                headers={"Content-Type": "application/json"},
                content_type="application/json",
                status_code=resp.status_code,
            )

        result = resp.json()

        # Convert SAM mask to CVAT polygon
        masks = result.get("masks", [])
        if not masks:
            context.logger.warning("SAM returned no masks")
            return context.Response(
                body=json.dumps([]),
                headers={"Content-Type": "application/json"},
                content_type="application/json",
                status_code=200,
            )

        # SAM returns masks[0] as the best mask (multimask_output=False)
        polygon = _mask_to_polygon(masks[0])

        context.logger.info(f"Polygon: {len(polygon)} points")

        # CVAT frontend expects a flat list [x1, y1, x2, y2, ...]
        flat_points = []
        for pt in polygon:
            flat_points.extend([pt[0], pt[1]])

        # Return as single shape in CVAT annotation format
        response = {
            "shapes": [
                {
                    "type": "polygon",
                    "points": flat_points,
                }
            ]
        }

        return context.Response(
            body=json.dumps(response),
            headers={"Content-Type": "application/json"},
            content_type="application/json",
            status_code=200,
        )

    except requests.exceptions.Timeout:
        context.logger.error(f"SAM timeout after {TIMEOUT}s")
        return context.Response(
            body=json.dumps({"error": "SAM timeout"}),
            headers={"Content-Type": "application/json"},
            content_type="application/json",
            status_code=504,
        )

    except requests.exceptions.ConnectionError as e:
        context.logger.error(f"SAM unreachable: {e}")
        return context.Response(
            body=json.dumps({"error": f"SAM unreachable at {SAM_GPU_URL}"}),
            headers={"Content-Type": "application/json"},
            content_type="application/json",
            status_code=503,
        )

    except Exception as e:
        context.logger.error(f"Handler error: {e}", exc_info=True)
        return context.Response(
            body=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
            content_type="application/json",
            status_code=500,
        )
