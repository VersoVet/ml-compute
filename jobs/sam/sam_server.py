#!/usr/bin/env python3
"""SAM (Segment Anything Model) FastAPI Server — Multi-model support.

Runs as a Docker container with exclusive GPU allocation on OnyxCortex.
Supports runtime model switching between vit_b, vit_l, vit_h, and MedSAM.
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
from fastapi import FastAPI, HTTPException, Request
from PIL import Image
from pydantic import BaseModel

try:
    from segment_anything import SamPredictor, sam_model_registry
except ImportError:
    raise ImportError("segment_anything package not found. Install: pip install segment-anything")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sam-server")

# Environment configuration
MODELS_DIR = os.environ.get("MODELS_DIR", "/models")
SAM_MODEL_NAME = os.environ.get("SAM_MODEL", "vit_b")
SAM_PORT = int(os.environ.get("SAM_PORT", "9470"))
SAM_HOST = os.environ.get("SAM_HOST", "0.0.0.0")

# Model registry: name -> (checkpoint filename, sam_model_registry key)
MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "vit_b": {"checkpoint": "sam_vit_b_01ec64.pth", "model_type": "vit_b"},
    "vit_l": {"checkpoint": "sam_vit_l_0b3195.pth", "model_type": "vit_l"},
    "vit_h": {"checkpoint": "sam_vit_h_4b8939.pth", "model_type": "vit_h"},
    "medsam": {"checkpoint": "medsam_vit_b.pth", "model_type": "vit_b"},
}

app = FastAPI(
    title="SAM Inference Server",
    description="Segment Anything Model REST API — Multi-model",
    version="2.0.0",
)

# Global state
sam_predictor: SamPredictor | None = None
device: str | None = None
active_model: str | None = None
model_lock = asyncio.Lock()


def _get_checkpoint_path(model_name: str) -> str | None:
    """Get checkpoint path for a model, return None if not found."""
    entry = MODEL_REGISTRY.get(model_name)
    if not entry:
        return None
    path = os.path.join(MODELS_DIR, entry["checkpoint"])
    return path if os.path.exists(path) else None


def _load_model(model_name: str) -> None:
    """Load a SAM model onto GPU (blocking, call from async with lock).

    Safe: only unloads the current model AFTER the new one loads successfully.
    If loading fails, the previous model remains active.
    """
    global sam_predictor, active_model

    entry = MODEL_REGISTRY.get(model_name)
    if not entry:
        raise ValueError(f"Unknown model: {model_name}")

    checkpoint = _get_checkpoint_path(model_name)
    if not checkpoint:
        raise FileNotFoundError(
            f"Checkpoint not found: {os.path.join(MODELS_DIR, entry['checkpoint'])}"
        )

    # Load new model FIRST (before unloading old one)
    logger.info("Loading SAM model %s (type=%s)...", model_name, entry["model_type"])
    try:
        new_model = sam_model_registry[entry["model_type"]](checkpoint=checkpoint)
    except Exception as e:
        logger.error("Failed to load %s, keeping %s active: %s", model_name, active_model, e)
        raise

    # New model loaded successfully — now unload old and swap
    if sam_predictor is not None:
        sam_predictor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Unloaded previous model %s", active_model)

    new_model.to(device=device)
    sam_predictor = SamPredictor(new_model)
    active_model = model_name
    logger.info("✓ SAM model %s loaded successfully", model_name)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize SAM model on startup."""
    global device

    if torch.cuda.is_available():
        device = "cuda"
        logger.info("✓ CUDA available. GPU: %s", torch.cuda.get_device_name(0))
    else:
        device = "cpu"
        logger.warning("⚠ CUDA not available. Using CPU (slow)")

    _load_model(SAM_MODEL_NAME)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    global sam_predictor
    if sam_predictor:
        sam_predictor = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("✓ SAM Server shut down")


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    if sam_predictor is None:
        raise HTTPException(status_code=503, detail="SAM model loading")
    return {
        "status": "ok",
        "model": active_model,
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
    }


@app.get("/ready")
async def ready() -> dict[str, Any]:
    """Readiness check."""
    if sam_predictor is None:
        return {"status": "not_ready"}
    return {"status": "ready", "model": active_model, "device": device}


@app.get("/info")
async def info() -> dict[str, Any]:
    """Get server information."""
    return {
        "service": "SAM Inference Server",
        "version": "2.0.0",
        "model": active_model,
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "vram_available_gb": (
            round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
            if device == "cuda"
            else None
        ),
        "models_dir": MODELS_DIR,
    }


@app.get("/models")
async def list_models() -> dict[str, Any]:
    """List available SAM models (only those with checkpoint on disk)."""
    models = []
    for name, entry in MODEL_REGISTRY.items():
        checkpoint_path = os.path.join(MODELS_DIR, entry["checkpoint"])
        exists = os.path.exists(checkpoint_path)
        models.append({
            "name": name,
            "model_type": entry["model_type"],
            "checkpoint": entry["checkpoint"],
            "available": exists,
            "active": name == active_model,
        })
    return {"models": models, "active": active_model}


class SwitchModelRequest(BaseModel):
    """Request to switch SAM model."""

    model: str


@app.post("/switch-model")
async def switch_model(request: SwitchModelRequest) -> dict[str, Any]:
    """Switch the active SAM model at runtime.

    Unloads current model, frees GPU memory, loads the new one.
    Takes 5-15 seconds depending on model size.
    """
    if request.model == active_model:
        return {"status": "ok", "model": active_model, "message": "Already active"}

    if request.model not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model}. Available: {list(MODEL_REGISTRY.keys())}",
        )

    checkpoint = _get_checkpoint_path(request.model)
    if not checkpoint:
        raise HTTPException(
            status_code=404,
            detail=f"Checkpoint not found for {request.model}",
        )

    async with model_lock:
        try:
            _load_model(request.model)
            return {"status": "ok", "model": active_model}
        except Exception as e:
            logger.error("Failed to switch model: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Switch failed: {e}")


# --- Segmentation endpoints (unchanged API) ---


class SegmentationRequest(BaseModel):
    """Segmentation request model."""

    image_base64: str
    points: list[list[int]] | None = None
    negative_points: list[list[int]] | None = None
    box: list[int] | None = None


class SegmentationResponse(BaseModel):
    """Segmentation response model."""

    status: str
    masks: Any | None = None
    iou_predictions: Any | None = None
    detail: str | None = None


async def _segment_impl(request: SegmentationRequest) -> SegmentationResponse:
    """Internal segmentation implementation."""
    if sam_predictor is None:
        raise HTTPException(status_code=503, detail="SAM model not loaded")

    if model_lock.locked():
        raise HTTPException(status_code=503, detail="Model switch in progress")

    try:
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image_array = np.array(image)

        sam_predictor.set_image(image_array)

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

        masks_list = masks.astype(int).tolist() if masks is not None else None
        iou_list = iou_predictions.tolist() if iou_predictions is not None else None

        return SegmentationResponse(
            status="success",
            masks=masks_list,
            iou_predictions=iou_list,
        )

    except Exception as e:
        logger.error("Segmentation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {e}")


@app.post("/segment")
async def segment(request: SegmentationRequest) -> SegmentationResponse:
    """Segment image using SAM via /segment endpoint."""
    return await _segment_impl(request)


@app.post("/api/interact")
async def interact(request: SegmentationRequest) -> SegmentationResponse:
    """Segment image — /api/interact alias for compatibility."""
    return await _segment_impl(request)


@app.post("/api/embed")
async def embed(request: Request) -> dict[str, str | list[int]]:
    """Get image embeddings for CVAT AI Tool integration."""
    if sam_predictor is None:
        raise HTTPException(status_code=503, detail="SAM not initialized")

    if model_lock.locked():
        raise HTTPException(status_code=503, detail="Model switch in progress")

    try:
        data = await request.json()
        buf = io.BytesIO(base64.b64decode(data["image"]))
        image = Image.open(buf).convert("RGB")
        sam_predictor.set_image(np.array(image))
        features = sam_predictor.get_image_embedding()
        feat_np = features.cpu().numpy() if features.is_cuda else features.numpy()
        return {
            "blob": base64.b64encode(feat_np.tobytes()).decode(),
            "shape": list(feat_np.shape),
        }
    except Exception as e:
        logger.error("Embedding failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host=SAM_HOST, port=SAM_PORT, log_level="info")
