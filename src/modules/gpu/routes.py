"""FastAPI routes for GPU management on OnyxCortex."""

from fastapi import APIRouter

from src.modules.gpu.models import (
    GPUAcquireResponse,
    GPUReleaseResponse,
    GPUStatusResponse,
)
from src.modules.gpu import service

router = APIRouter()


@router.get("/status", response_model=GPUStatusResponse)
async def gpu_status() -> GPUStatusResponse:
    """Get current GPU status on OnyxCortex.

    Returns:
        GPU memory usage, mode, and container states.
    """
    return await service.get_gpu_status()


@router.post("/acquire", response_model=GPUAcquireResponse)
async def gpu_acquire() -> GPUAcquireResponse:
    """Acquire GPU for training by stopping SAM/MedSAM2 containers.

    Stops inference containers on OnyxCortex to free ~6 Go VRAM
    for training jobs (U-Net, YOLO, EfficientNet).

    Returns:
        Acquisition result with freed memory.
    """
    return await service.acquire_gpu()


@router.post("/release", response_model=GPUReleaseResponse)
async def gpu_release() -> GPUReleaseResponse:
    """Release GPU back to inference mode.

    Restarts SAM and MedSAM2 containers on OnyxCortex
    for CVAT annotation workflows.

    Returns:
        Release result with restarted containers.
    """
    return await service.release_gpu()
