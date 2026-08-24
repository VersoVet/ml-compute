"""FastAPI routes for Nomad job orchestration."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.modules.nomad.models import NomadJobRequest
from src.modules.nomad.service import NomadManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global Nomad manager instance
nomad_manager: NomadManager | None = None


def set_nomad_manager(manager: NomadManager) -> None:
    """Set the global Nomad manager instance.

    Args:
        manager: NomadManager instance.
    """
    global nomad_manager
    nomad_manager = manager


@router.get("/status", tags=["nomad"])
async def get_nomad_status() -> dict[str, Any]:
    """Get Nomad cluster status.

    Returns:
        Cluster status with nodes and jobs metrics.
    """
    if not nomad_manager:
        raise HTTPException(status_code=503, detail="Nomad manager not initialized")

    status = await nomad_manager.get_cluster_status()
    return status.model_dump()


@router.post("/jobs/submit", tags=["nomad"])
async def submit_nomad_job(request: NomadJobRequest) -> dict[str, Any]:
    """Submit a job to Nomad cluster.

    Args:
        request: Job specification.

    Returns:
        Submission result with job and evaluation IDs.

    Raises:
        HTTPException: If submission fails or Nomad unavailable.
    """
    if not nomad_manager:
        raise HTTPException(status_code=503, detail="Nomad manager not initialized")

    try:
        result = await nomad_manager.submit_job(request)
        return result
    except Exception as e:
        logger.error(f"Job submission failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs/{job_id}", tags=["nomad"])
async def get_job_status(job_id: str) -> dict[str, Any]:
    """Get job status and allocations.

    Args:
        job_id: Job name.

    Returns:
        Job status with allocations.
    """
    if not nomad_manager:
        raise HTTPException(status_code=503, detail="Nomad manager not initialized")

    status = await nomad_manager.get_job_status(job_id)
    return status.model_dump()


@router.post("/jobs/{job_id}/stop", tags=["nomad"])
async def stop_nomad_job(job_id: str) -> dict[str, Any]:
    """Stop a running job.

    Args:
        job_id: Job name.

    Returns:
        Status of stop operation.
    """
    if not nomad_manager:
        raise HTTPException(status_code=503, detail="Nomad manager not initialized")

    success = await nomad_manager.stop_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to stop job {job_id}")

    return {"status": "stopped", "job_id": job_id}


@router.get("/gpu-status", tags=["nomad"])
async def get_gpu_status() -> list[dict[str, Any]]:
    """Get GPU status on all Nomad nodes.

    Returns:
        List of GPU status per node.
    """
    if not nomad_manager:
        raise HTTPException(status_code=503, detail="Nomad manager not initialized")

    statuses = await nomad_manager.get_gpu_status()
    return [s.model_dump() for s in statuses]
