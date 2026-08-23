#!/usr/bin/env python3
"""SAM (Segment Anything Model) FastAPI Server.

Runs as a Nomad job with exclusive GPU allocation.
Provides REST API for segmentation requests.
"""

import asyncio
import base64
import io
import logging
import os
from typing import Any

import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# SAM imports
try:
    from segment_anything import SamPredictor, sam_model_registry
except ImportError:
    raise ImportError("segment_anything package not found. Install: pip install segment-anything")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sam-server")

# Environment configuration
SAM_MODEL_NAME = os.environ.get("SAM_MODEL", "vit_b")
SAM_MODEL_PATH = os.environ.get("SAM_CHECKPOINT_PATH", "/models/sam_vit_b.pth")
SAM_PORT = int(os.environ.get("SAM_PORT", "9470"))
SAM_HOST = os.environ.get("SAM_HOST", "0.0.0.0")
CUDA_VISIBLE_DEVICES = os.environ.get("CUDA_VISIBLE_DEVICES", "0")

# Initialize FastAPI app
app = FastAPI(
    title="SAM Inference Server",
    description="Segment Anything Model REST API",
    version="1.0.0",
)

# Global state
sam_predictor: SamPredictor | None = None
device: str | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize SAM model on startup."""
    global sam_predictor, device

    logger.info(f"Starting SAM Server (model={SAM_MODEL_NAME})...")

    # Determine device
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"✓ CUDA available. GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"  Visible devices: {CUDA_VISIBLE_DEVICES}")
    else:
        device = "cpu"
        logger.warning("⚠ CUDA not available. Using CPU (slow)")

    try:
        # Load SAM model
        logger.info(f"Loading SAM model: {SAM_MODEL_NAME}...")

        if os.path.exists(SAM_MODEL_PATH):
            # Use local checkpoint
            logger.info(f"Using local checkpoint: {SAM_MODEL_PATH}")
            sam_model = sam_model_registry[SAM_MODEL_NAME](checkpoint=SAM_MODEL_PATH)
        else:
            # Download from URL (first time only)
            logger.info(f"Downloading {SAM_MODEL_NAME} checkpoint...")
            sam_model = sam_model_registry[SAM_MODEL_NAME](checkpoint=None)

        # Move to device
        sam_model.to(device=device)
        sam_predictor = SamPredictor(sam_model)

        logger.info("✓ SAM model loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load SAM model: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global sam_predictor
    if sam_predictor:
        logger.info("Unloading SAM model...")
        sam_predictor = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("✓ SAM Server shut down")


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    if sam_predictor is None:
        return {"status": "loading", "gpu": device}
    return {
        "status": "ok",
        "model": SAM_MODEL_NAME,
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
    }


@app.get("/ready")
async def ready() -> dict[str, Any]:
    """Readiness check for Nomad."""
    if sam_predictor is None:
        return {"status": "not_ready"}
    return {
        "status": "ready",
        "model": SAM_MODEL_NAME,
        "device": device,
    }


class SegmentationRequest(BaseModel):
    """Segmentation request model."""

    image_base64: str  # Base64-encoded image (PNG, JPG)
    points: list[list[int]] | None = None  # [[x, y], ...] positive points
    negative_points: list[list[int]] | None = None  # [[x, y], ...] negative points
    box: list[int] | None = None  # [x1, y1, x2, y2] bounding box


class SegmentationResponse(BaseModel):
    """Segmentation response model."""

    status: str
    masks: list[list[int]] | None = None  # RLE encoded masks
    iou_predictions: list[float] | None = None


@app.post("/segment")
async def segment(request: SegmentationRequest) -> SegmentationResponse:
    """Segment image using SAM.

    Args:
        request: SegmentationRequest with image and prompts

    Returns:
        SegmentationResponse with masks and IoU predictions
    """
    if sam_predictor is None:
        raise HTTPException(status_code=503, detail="SAM model not loaded")

    try:
        # Decode image from base64
        image_data = base64.b64decode(request.image_base64)
        image_array = np.array(io.BytesIO(image_data))

        # TODO: Proper image decoding (PIL)
        # For now, this is a placeholder

        # Set image in SAM
        sam_predictor.set_image(image_array)

        # Prepare prompts
        points_array = None
        labels_array = None

        if request.points:
            points_array = np.array(request.points, dtype=np.float32)
            labels_array = np.ones(len(request.points), dtype=np.int32)

        if request.negative_points:
            neg_points = np.array(request.negative_points, dtype=np.float32)
            neg_labels = np.zeros(len(request.negative_points), dtype=np.int32)
            if points_array is not None:
                points_array = np.vstack([points_array, neg_points])
                labels_array = np.hstack([labels_array, neg_labels])
            else:
                points_array = neg_points
                labels_array = neg_labels

        # Run segmentation
        if points_array is not None:
            masks, iou_predictions, _ = sam_predictor.predict(
                point_coords=points_array,
                point_labels=labels_array,
                box=np.array(request.box) if request.box else None,
                multimask_output=False,
            )
        else:
            return SegmentationResponse(
                status="error",
                detail="No prompts provided (points or box required)",
            )

        return SegmentationResponse(
            status="success",
            masks=masks.tolist() if masks is not None else None,
            iou_predictions=iou_predictions.tolist() if iou_predictions is not None else None,
        )

    except Exception as e:
        logger.error(f"Segmentation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@app.get("/info")
async def info() -> dict[str, Any]:
    """Get server information."""
    return {
        "service": "SAM Inference Server",
        "model": SAM_MODEL_NAME,
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "vram_available_gb": (
            round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
            if device == "cuda"
            else None
        ),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=SAM_HOST,
        port=SAM_PORT,
        log_level="info",
    )
