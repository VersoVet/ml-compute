"""FastAPI routes for compute backends."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.modules.compute_backends.models import (
    BackendInfo,
    ComputeJobRequest,
    ComputeJobResponse,
)
from src.modules.compute_backends.service import BackendManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global backend manager
backend_manager: BackendManager | None = None


def set_backend_manager(manager: BackendManager) -> None:
    """Set the global backend manager instance.

    Args:
        manager: BackendManager instance.
    """
    global backend_manager
    backend_manager = manager


def _mgr() -> BackendManager:
    """Get the backend manager or raise 503.

    Returns:
        Active BackendManager.

    Raises:
        HTTPException: If manager not initialized.
    """
    if not backend_manager:
        raise HTTPException(status_code=503, detail="Backend manager not initialized")
    return backend_manager


@router.get("/backends", tags=["compute"])
async def list_backends() -> list[BackendInfo]:
    """List all compute backends with availability and GPU info.

    Returns:
        List of backend capabilities.
    """
    return await _mgr().list_backends()


@router.post("/compute/submit", tags=["compute"])
async def submit_compute_job(request: ComputeJobRequest) -> ComputeJobResponse:
    """Submit a job to the specified or auto-selected backend.

    Args:
        request: Job specification with optional backend selection.

    Returns:
        Job response with ID, backend used, and initial status.
    """
    try:
        return await _mgr().submit_job(request)
    except Exception as e:
        logger.error(f"Job submission failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compute/{job_id}", tags=["compute"])
async def get_compute_status(job_id: str) -> ComputeJobResponse:
    """Get job status from the backend that executed it.

    Args:
        job_id: Job identifier.

    Returns:
        Current job status.
    """
    return await _mgr().get_status(job_id)


@router.get("/compute/{job_id}/logs", tags=["compute"])
async def get_compute_logs(job_id: str) -> dict[str, Any]:
    """Get job execution logs.

    Args:
        job_id: Job identifier.

    Returns:
        Log output.
    """
    logs = await _mgr().get_logs(job_id)
    return {"job_id": job_id, "logs": logs}


@router.post("/compute/{job_id}/stop", tags=["compute"])
async def stop_compute_job(job_id: str) -> dict[str, Any]:
    """Stop a running job.

    Args:
        job_id: Job identifier.

    Returns:
        Stop result.
    """
    success = await _mgr().stop_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to stop job {job_id}")
    return {"status": "stopped", "job_id": job_id}
