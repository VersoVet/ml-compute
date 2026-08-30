"""Nuclio handler for SAM/MedSAM proxy — CVAT interactor v2 protocol.

CVAT interactor v2 sends image + prompt points and expects
``{"shapes": [{"type": "mask", "points": <rle>, ...}]}``.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

SAM_GPU_URL = os.environ.get("SAM_GPU_URL", "http://10.0.0.26:9470")
SAM_MODEL_NAME = os.environ.get("SAM_MODEL_NAME", "medsam")

_last_model: str | None = None
logger = logging.getLogger(__name__)


def init_context(context: Any) -> None:
    """Initialize handler context."""
    context.logger.info("SAM proxy -> %s (model: %s)", SAM_GPU_URL, SAM_MODEL_NAME)


def handler(context: Any, event: Any) -> Any:
    """Route CVAT requests to SAM GPU embed or interact endpoints."""
    data = _parse_body(event.body)
    _ensure_model(context)

    pos_points = _normalize_points(data.get("pos_points"))
    neg_points = _normalize_points(data.get("neg_points"))
    box = _normalize_box(data.get("obj_bbox"))

    context.logger.info(
        "Request: pos=%d neg=%d box=%s",
        len(pos_points or []),
        len(neg_points or []),
        box,
    )

    if pos_points or neg_points or box:
        return _handle_interact(context, data, pos_points, neg_points, box)

    return _handle_embed(context, data)


def _parse_body(body: Any) -> dict[str, Any]:
    """Parse Nuclio event body to a dict."""
    if isinstance(body, bytes):
        return json.loads(body.decode())
    if isinstance(body, str):
        return json.loads(body)
    if isinstance(body, dict):
        return body
    return json.loads(str(body))


def _ensure_model(context: Any) -> None:
    """Switch SAM model on GPU if needed."""
    global _last_model
    if _last_model == SAM_MODEL_NAME:
        return
    try:
        resp = requests.post(
            f"{SAM_GPU_URL}/switch-model",
            json={"model": SAM_MODEL_NAME},
            timeout=30,
        )
        if resp.status_code == 200:
            _last_model = SAM_MODEL_NAME
            context.logger.info("Model switched to %s", SAM_MODEL_NAME)
    except Exception as exc:
        context.logger.warning("Model switch failed: %s", exc)


def _handle_embed(context: Any, data: dict[str, Any]) -> Any:
    """Forward embed request — returns {blob, shape}."""
    try:
        resp = requests.post(
            f"{SAM_GPU_URL}/api/embed",
            json={"image": data["image"]},
            timeout=60,
        )
        context.logger.info("SAM embed: HTTP %s", resp.status_code)
        return context.Response(
            body=resp.text,
            headers={},
            content_type="application/json",
            status_code=resp.status_code,
        )
    except requests.exceptions.Timeout:
        context.logger.error("SAM embed timeout")
        return _error_response(context, "SAM timeout", 504)
    except Exception as exc:
        context.logger.error("SAM embed failed: %s", exc)
        return _error_response(context, str(exc), 503)


def _handle_interact(
    context: Any,
    data: dict[str, Any],
    pos_points: list[list[int]] | None,
    neg_points: list[list[int]] | None,
    box: list[int] | None,
) -> Any:
    """Run SAM segmentation and return CVAT v2 mask shapes."""
    payload: dict[str, Any] = {
        "image_base64": data["image"],
        "points": pos_points,
        "negative_points": neg_points,
        "box": box,
    }

    try:
        resp = requests.post(
            f"{SAM_GPU_URL}/api/interact",
            json=payload,
            timeout=60,
        )
        context.logger.info("SAM interact: HTTP %s", resp.status_code)
        if resp.status_code != 200:
            return _error_response(context, resp.text[:200], resp.status_code)

        result = resp.json()
        if result.get("status") != "success":
            detail = result.get("detail", "SAM interact failed")
            context.logger.error("SAM interact error: %s", detail)
            return _json_response(context, {"shapes": []}, 200)

        mask = _extract_mask(result.get("masks"))
        if mask is None or not any(any(row) for row in mask):
            context.logger.warning("SAM returned empty mask")
            return _json_response(context, {"shapes": []}, 200)

        rle = mask_to_rle(mask)
        if len(rle) < 6:
            context.logger.warning("RLE too short: %s", rle)
            return _json_response(context, {"shapes": []}, 200)

        context.logger.info("Mask RLE len=%d, fg_pixels=%d", len(rle), sum(sum(row) for row in mask))
        return _json_response(
            context,
            {
                "shapes": [
                    {
                        "type": "mask",
                        "points": rle,
                        "attributes": [],
                        "occluded": False,
                        "rotation": 0,
                        "group": 0,
                        "source": "auto",
                    }
                ]
            },
            200,
        )
    except requests.exceptions.Timeout:
        context.logger.error("SAM interact timeout")
        return _error_response(context, "SAM timeout", 504)
    except Exception as exc:
        context.logger.error("SAM interact failed: %s", exc)
        return _error_response(context, str(exc), 503)


def _normalize_points(points: Any) -> list[list[int]] | None:
    """Convert CVAT points to SAM [[x, y], ...] format."""
    if not points:
        return None

    normalized: list[list[int]] = []

    if isinstance(points, (list, tuple)) and len(points) >= 2:
        if isinstance(points[0], (int, float)) and isinstance(points[1], (int, float)):
            if not isinstance(points[0], (list, tuple)):
                return [[int(points[0]), int(points[1])]]

    for point in points:
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            normalized.append([int(point[0]), int(point[1])])

    return normalized or None


def _normalize_box(obj_bbox: Any) -> list[int] | None:
    """Convert CVAT bbox to SAM [x1, y1, x2, y2] format."""
    if not obj_bbox:
        return None
    if (
        len(obj_bbox) == 4
        and not isinstance(obj_bbox[0], (list, tuple))
    ):
        x1, y1, x2, y2 = (int(v) for v in obj_bbox)
        if x2 > x1 and y2 > y1:
            return [x1, y1, x2, y2]
        return None
    if len(obj_bbox) >= 2 and isinstance(obj_bbox[0], (list, tuple)):
        xs = [p[0] for p in obj_bbox]
        ys = [p[1] for p in obj_bbox]
        x1, x2 = int(min(xs)), int(max(xs))
        y1, y2 = int(min(ys)), int(max(ys))
        if x2 > x1 and y2 > y1:
            return [x1, y1, x2, y2]
    return None


def _extract_mask(masks: Any) -> list[list[int]] | None:
    """Pick the first 2D mask from SAM response."""
    if not masks:
        return None
    mask = masks[0] if isinstance(masks, list) else masks
    if isinstance(mask, list) and mask and isinstance(mask[0], list):
        if isinstance(mask[0][0], list):
            return [[1 if cell else 0 for cell in row] for row in mask[0]]
        return [[1 if cell else 0 for cell in row] for row in mask]
    return None


def mask_to_rle(mask: list[list[int]]) -> list[int]:
    """Encode binary mask as CVAT RLE (IOG interactor algorithm)."""
    height = len(mask)
    width = len(mask[0]) if height else 0
    pixels = [1 if cell else 0 for row in mask for cell in row]
    if not pixels:
        return []

    changes = [index for index in range(1, len(pixels)) if pixels[index] != pixels[index - 1]]
    boundaries = [0, *changes, len(pixels)]
    rle = [boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1)]

    if pixels[0] == 1:
        rle.insert(0, 0)

    rle.extend([0, 0, width - 1, height - 1])
    return rle


def _json_response(context: Any, payload: dict[str, Any], status_code: int) -> Any:
    """Build a JSON Nuclio response."""
    return context.Response(
        body=json.dumps(payload),
        headers={},
        content_type="application/json",
        status_code=status_code,
    )


def _error_response(context: Any, message: str, status_code: int) -> Any:
    """Build an error JSON response."""
    return _json_response(context, {"error": message}, status_code)
