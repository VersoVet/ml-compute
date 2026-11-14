"""Admin routes for GPU allocator — status, manual release, queue management."""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.modules.gpu_allocator import allocator, state

router = APIRouter()


@router.get("/status", tags=["gpu-allocator"])
async def get_allocator_status() -> dict[str, Any]:
    """Get full GPU allocator status (slots, queue, summary).

    Returns:
        Dict with gpu_slots, queue, and summary stats.
    """
    return await allocator.get_cluster_status()


@router.post("/release/{job_id}", tags=["gpu-allocator"])
async def manual_release(job_id: str) -> dict[str, str]:
    """Manually release a GPU assigned to a job (admin escape hatch).

    Args:
        job_id: Ray job ID to release.

    Returns:
        Release confirmation with freed gpu_id.

    Raises:
        HTTPException: If job not found in GPU slots.
    """
    gpu_id = await allocator.release_job(job_id, kill_orphans=True)
    if gpu_id is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not assigned to any GPU")
    return {"released": gpu_id, "job_id": job_id, "message": f"GPU {gpu_id} freed + orphans killed"}


@router.delete("/queue/{queue_id}", tags=["gpu-allocator"])
async def cancel_queued_job(queue_id: int) -> dict[str, str]:
    """Cancel a queued job.

    Args:
        queue_id: Queue entry ID to cancel.

    Returns:
        Cancellation confirmation.

    Raises:
        HTTPException: If queue entry not found or already submitted.
    """
    cancelled = await state.cancel_queued(queue_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail=f"Queue entry {queue_id} not found or already submitted")
    return {"cancelled": queue_id, "message": "Job removed from queue"}
