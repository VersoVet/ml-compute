#!/usr/bin/env python3
"""MedSAM2 Temporal Propagation Server.

Runs on OnyxCortex GPU. Provides:
- Single-frame segmentation (2D, like SAM but medical-tuned)
- Temporal propagation (seed mask on 1 frame → propagate to all frames)

Designed for bone annotation: annotate 1 frame of a 930-frame
fluoroscopy series, propagate the bone contour to all others.
"""

import asyncio
import base64
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("medsam2-server")

# Configuration
CHECKPOINT_PATH = os.environ.get("MEDSAM2_CHECKPOINT", "/models/MedSAM2_latest.pt")
SAM2_CONFIG = os.environ.get("SAM2_CONFIG", "configs/sam2.1/sam2.1_hiera_t.yaml")
PORT = int(os.environ.get("MEDSAM2_PORT", "9473"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(
    title="MedSAM2 Temporal Propagation Server",
    description="Bone segmentation with temporal propagation for fluoroscopy series",
    version="1.0.0",
)

# Global state
predictor = None
model_loaded = False


@app.on_event("startup")
async def startup() -> None:
    """Load MedSAM2 model."""
    global predictor, model_loaded

    logger.info("Loading MedSAM2 (device=%s)...", DEVICE)

    if not os.path.exists(CHECKPOINT_PATH):
        logger.error("Checkpoint not found: %s", CHECKPOINT_PATH)
        return

    try:
        from sam2.build_sam import build_sam2_video_predictor

        predictor = build_sam2_video_predictor(
            config_file=SAM2_CONFIG,
            ckpt_path=CHECKPOINT_PATH,
        )
        model_loaded = True
        logger.info("✓ MedSAM2 loaded (checkpoint=%s)", CHECKPOINT_PATH)
    except Exception as e:
        logger.error("Failed to load MedSAM2: %s", e, exc_info=True)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check."""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="MedSAM2 not loaded")
    return {
        "status": "ok",
        "model": "MedSAM2_latest",
        "device": DEVICE,
        "gpu": torch.cuda.get_device_name(0) if DEVICE == "cuda" else None,
    }


@app.get("/ready")
async def ready() -> dict[str, Any]:
    """Readiness probe."""
    return {"status": "ready" if model_loaded else "not_ready"}


class PropagateRequest(BaseModel):
    """Request for temporal propagation.

    Provide frames as base64 PNGs and a seed mask on one frame.
    MedSAM2 will propagate the mask to all other frames.
    """

    frames: list[str]  # List of base64-encoded PNG frames (ordered)
    seed_frame_idx: int  # Index of the frame with the initial mask
    seed_mask: str  # Base64-encoded binary mask (PNG, same size as frame)
    score_threshold: float = 0.0  # Logit threshold for mask binarization


class PropagateResponse(BaseModel):
    """Response with propagated masks."""

    status: str
    frame_count: int
    masks: list[str]  # Base64 PNG masks for each frame


@app.post("/propagate")
async def propagate(request: PropagateRequest) -> PropagateResponse:
    """Propagate a seed mask across all frames in a series.

    This is the core endpoint for bone annotation: provide a series
    of fluoroscopy frames and a mask on one frame, get masks for all.
    """
    if not model_loaded:
        raise HTTPException(status_code=503, detail="MedSAM2 not loaded")

    if not request.frames:
        raise HTTPException(status_code=400, detail="No frames provided")

    if request.seed_frame_idx >= len(request.frames):
        raise HTTPException(status_code=400, detail="seed_frame_idx out of range")

    try:
        # Create temp directory with frames as JPEG files (SAM2 video predictor expects a dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir) / "frames"
            frame_dir.mkdir()

            # Decode and save frames
            for i, frame_b64 in enumerate(request.frames):
                img_bytes = base64.b64decode(frame_b64)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                img.save(frame_dir / f"{i:06d}.jpg")

            # Decode seed mask
            mask_bytes = base64.b64decode(request.seed_mask)
            mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")
            seed_mask = (np.array(mask_img) > 128).astype(np.uint8)

            # Run propagation
            masks = await asyncio.to_thread(
                _propagate_sync,
                str(frame_dir),
                request.seed_frame_idx,
                seed_mask,
                request.score_threshold,
                len(request.frames),
            )

            # Encode result masks as base64 PNG
            result_masks = []
            for mask in masks:
                mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
                buf = io.BytesIO()
                mask_pil.save(buf, format="PNG")
                result_masks.append(base64.b64encode(buf.getvalue()).decode())

            return PropagateResponse(
                status="success",
                frame_count=len(result_masks),
                masks=result_masks,
            )

    except Exception as e:
        logger.error("Propagation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Propagation failed: {e}")


def _propagate_sync(
    frame_dir: str,
    seed_frame_idx: int,
    seed_mask: np.ndarray,
    score_threshold: float,
    num_frames: int,
) -> list[np.ndarray]:
    """Run MedSAM2 propagation synchronously (called from async via to_thread)."""
    # Initialize video state
    inference_state = predictor.init_state(video_path=frame_dir, async_loading_frames=False)

    # Add seed mask
    predictor.add_new_mask(
        inference_state=inference_state,
        frame_idx=seed_frame_idx,
        obj_id=1,
        mask=seed_mask,
    )

    # Propagate
    video_segments: dict[int, np.ndarray] = {}
    for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
        # Take first object mask, threshold
        mask = (out_mask_logits[0] > score_threshold).cpu().numpy().squeeze()
        video_segments[out_frame_idx] = mask

    # Ensure we have all frames (fill missing with empty mask)
    h, w = seed_mask.shape
    result = []
    for i in range(num_frames):
        if i in video_segments:
            result.append(video_segments[i])
        else:
            result.append(np.zeros((h, w), dtype=np.uint8))

    # Reset state for next call
    predictor.reset_state(inference_state)

    return result


class SegmentRequest(BaseModel):
    """Single-frame segmentation request (2D, no propagation)."""

    image: str  # Base64 PNG
    points: list[list[int]] | None = None  # [[x, y], ...] positive points
    negative_points: list[list[int]] | None = None
    box: list[int] | None = None  # [x1, y1, x2, y2]


@app.post("/segment")
async def segment_single(request: SegmentRequest) -> dict[str, Any]:
    """Single-frame segmentation (2D) using MedSAM2.

    Similar to SAM /segment but with medical-tuned weights.
    """
    if not model_loaded:
        raise HTTPException(status_code=503, detail="MedSAM2 not loaded")

    try:
        # Decode image
        img_bytes = base64.b64decode(request.image)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_array = np.array(img)

        # For single-frame, use SAM2's image predictor mode
        # Create a single-frame "video"
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir)
            img.save(frame_dir / "000000.jpg")

            inference_state = predictor.init_state(
                video_path=str(frame_dir), async_loading_frames=False
            )

            # Add point/box prompts
            if request.points:
                points = np.array(request.points, dtype=np.float32)
                labels = np.ones(len(request.points), dtype=np.int32)
                if request.negative_points:
                    neg = np.array(request.negative_points, dtype=np.float32)
                    points = np.vstack([points, neg])
                    labels = np.hstack([labels, np.zeros(len(request.negative_points), dtype=np.int32)])

                predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=0,
                    obj_id=1,
                    points=points,
                    labels=labels,
                    box=np.array(request.box) if request.box else None,
                )
            elif request.box:
                predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=0,
                    obj_id=1,
                    box=np.array(request.box),
                )

            # Get mask
            for _, _, logits in predictor.propagate_in_video(inference_state):
                mask = (logits[0] > 0.0).cpu().numpy().squeeze()
                break

            predictor.reset_state(inference_state)

            # Encode mask
            mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
            buf = io.BytesIO()
            mask_pil.save(buf, format="PNG")
            mask_b64 = base64.b64encode(buf.getvalue()).decode()

            return {
                "status": "success",
                "mask": mask_b64,
                "mask_area": int(mask.sum()),
                "image_shape": list(img_array.shape[:2]),
            }

    except Exception as e:
        logger.error("Segmentation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
