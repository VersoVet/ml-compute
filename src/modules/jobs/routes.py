"""FastAPI routes for Ray Jobs API."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.models import JobResponse, JobSubmitRequest
from src.modules.gpu_allocator import allocator
from src.modules.jobs import service

logger = logging.getLogger(__name__)
router = APIRouter()

# OnyxClient for status publishing (imported at module level for visibility)
_onyx = None


def set_onyx(client: Any) -> None:
    """Set the global OnyxClient instance.

    Args:
        client: OnyxClient instance from main.py.
    """
    global _onyx
    _onyx = client


@router.post("", response_model=JobResponse, status_code=202)
async def submit_job(request: JobSubmitRequest) -> JobResponse:
    """Submit a new ML training or inference job to Ray.

    Args:
        request: Job submission request.

    Returns:
        JobResponse with job_id and initial status.

    Raises:
        HTTPException: If submission fails.
    """
    try:
        # Signal that job submission is in progress
        if _onyx:
            try:
                _onyx.publish_status("WORKING")
            except Exception as e:
                logger.debug(f"Failed to signal WORKING status: {e}")

        result = await allocator.submit_or_queue(
            name=request.name,
            entrypoint=request.entrypoint,
            runtime_env=request.runtime_env,
            submit_kwargs=request.submit_kwargs,
        )

        if result.allocated:
            return JobResponse(
                job_id=result.job_id or "",
                status="SUBMITTED",
                name=request.name,
                submission_time=None,
            )
        return JobResponse(
            job_id=f"queued-{result.queue_id}",
            status="QUEUED",
            name=request.name,
            queue_position=result.queue_position,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", tags=["jobs"])
async def list_jobs(
    status: str | None = Query(None, description="Filter by job status"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
) -> dict[str, Any]:
    """List Ray jobs with optional filtering.

    Args:
        status: Optional status filter.
        limit: Maximum results.

    Returns:
        Dict with jobs list and total count.
    """
    result = await service.list_jobs(status=status, limit=limit)

    return {
        "jobs": [
            {
                "job_id": str(j.submission_id) if hasattr(j, "submission_id") else str(j),
                "status": str(j.status) if hasattr(j, "status") else "UNKNOWN",
                "name": getattr(j, "metadata", {}).get("name", "unnamed"),
                "submission_time": None,
            }
            for j in result["jobs"]
        ],
        "total": result["total"],
    }


@router.get("/{job_id}", response_model=JobResponse, tags=["jobs"])
async def get_job_status(job_id: str) -> JobResponse:
    """Get status for a job (Ray job or queued job).

    Handles both real Ray job IDs and queued-X IDs from the GPU allocator.

    Args:
        job_id: Ray job ID or queued-{queue_id}.

    Returns:
        JobResponse with status and logs.

    Raises:
        HTTPException: If job not found.
    """
    # Handle queued-X IDs from the GPU allocator
    if job_id.startswith("queued-"):
        try:
            queue_id = int(job_id.split("-", 1)[1])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail=f"Invalid queued job ID: {job_id}")

        info = await allocator.resolve_queued_job(queue_id)
        status = info.get("status", "UNKNOWN")
        real_job_id = info.get("ray_job_id", job_id)

        return JobResponse(
            job_id=real_job_id if real_job_id != job_id else job_id,
            status=status,
            name=info.get("name", f"queued-{queue_id}"),
            queue_position=info.get("queue_position"),
        )

    # Regular Ray job ID
    try:
        result = await service.get_job_status(job_id)

        return JobResponse(
            job_id=result["job_id"],
            status=result["status"],
            name=f"job-{job_id[:8]}",
            submission_time=None,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{job_id}", status_code=204, tags=["jobs"])
async def delete_job(job_id: str) -> None:
    """Stop a job and kill orphan processes on the worker.

    Args:
        job_id: Ray job ID to stop.

    Raises:
        HTTPException: If job not found or stop fails.
    """
    try:
        # Get worker IP from GPU allocator before stopping
        from src.modules.gpu_allocator import state as gpu_state

        worker_ip: str | None = None
        slots = await gpu_state.get_assigned_slots()
        for slot in slots:
            if slot.assigned_job_id == job_id:
                worker_ip = slot.node_ip
                break

        await service.delete_job(job_id, worker_ip=worker_ip)

        # Release the GPU slot
        await allocator.release_job(job_id)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
