"""GPU allocator — core logic for exclusive GPU assignment and job queuing.

Central entry point: submit_or_queue() replaces direct Ray submission.
Routing: bone jobs → Cortex (priority 1), overflow → Tensor (priority 2).
"""

import logging
from typing import Any

from src.modules.gpu_allocator import state
from src.modules.gpu_allocator.models import AllocationResult
from src.modules.jobs import service as jobs_service

logger = logging.getLogger(__name__)


async def submit_or_queue(
    name: str,
    entrypoint: str,
    runtime_env: dict[str, Any] | None = None,
    submit_kwargs: dict[str, Any] | None = None,
) -> AllocationResult:
    """Submit a job to Ray if a GPU is free, otherwise queue it.

    Routing logic:
    - Jobs with 'bone' in name → prefer Cortex (bone_training label, priority 1)
    - Other jobs → prefer Tensor
    - Fallback to any free GPU regardless of preference

    Args:
        name: Job name.
        entrypoint: Command to run.
        runtime_env: Ray runtime environment.
        submit_kwargs: Ray submission parameters.

    Returns:
        AllocationResult indicating allocation or queue status.
    """
    runtime_env = runtime_env or {}
    submit_kwargs = submit_kwargs or {}

    # Bone jobs prefer Cortex (priority 1), others prefer Tensor
    prefer_cortex = "bone" in name.lower()
    gpu = await state.get_free_gpu(prefer_cortex=prefer_cortex)

    if gpu is None:
        queue_id = await state.enqueue_job(name, entrypoint, runtime_env, submit_kwargs)
        position = await state.get_queue_position(queue_id)
        logger.info("No free GPU — job '%s' queued (position %d)", name, position)
        return AllocationResult(
            allocated=False,
            queued=True,
            queue_id=queue_id,
            queue_position=position,
            message=f"All GPUs busy. Queued at position {position}.",
        )

    # Submit to Ray
    try:
        result = await jobs_service.submit_job(
            name=name,
            entrypoint=entrypoint,
            runtime_env=runtime_env,
            submit_kwargs=submit_kwargs,
        )
        ray_job_id = result["job_id"]
    except RuntimeError:
        raise

    # Assign GPU to the job
    assigned = await state.assign_gpu(gpu.gpu_id, ray_job_id)
    if not assigned:
        logger.warning(
            "GPU %s taken during submission (race). Job %s submitted but untracked.",
            gpu.gpu_id,
            ray_job_id,
        )

    logger.info("Job '%s' → GPU %s (%s), ray_job=%s", name, gpu.gpu_id, gpu.gpu_type, ray_job_id)
    return AllocationResult(
        allocated=True,
        gpu_id=gpu.gpu_id,
        job_id=ray_job_id,
        message=f"Allocated GPU {gpu.gpu_id} ({gpu.gpu_type})",
    )


async def release_job(job_id: str) -> str | None:
    """Release the GPU assigned to a finished/dead job.

    Args:
        job_id: Ray job ID.

    Returns:
        The gpu_id that was freed, or None.
    """
    return await state.release_gpu_by_job(job_id)


async def drain_queue() -> int:
    """Submit queued jobs while GPUs are available.

    Returns:
        Number of jobs submitted from queue.
    """
    submitted = 0
    while True:
        job = await state.dequeue_next()
        if job is None:
            break

        prefer_cortex = "bone" in job.name.lower()
        gpu = await state.get_free_gpu(prefer_cortex=prefer_cortex)
        if gpu is None:
            break

        try:
            result = await jobs_service.submit_job(
                name=job.name,
                entrypoint=job.entrypoint,
                runtime_env=job.runtime_env,
                submit_kwargs=job.submit_kwargs,
            )
            await state.assign_gpu(gpu.gpu_id, result["job_id"])
            logger.info("Queue drain: '%s' → GPU %s, ray_job=%s", job.name, gpu.gpu_id, result["job_id"])
            submitted += 1
        except Exception as e:
            logger.error("Queue drain failed for '%s': %s", job.name, e)
            break
    return submitted


async def get_cluster_status() -> dict[str, Any]:
    """Get full GPU allocator status for admin endpoint.

    Returns:
        Dict with slots, queue, and summary stats.
    """
    slots = await state.get_all_slots()
    queue = await state.get_queue()
    free = sum(1 for s in slots if s.assigned_job_id is None)
    busy = sum(1 for s in slots if s.assigned_job_id is not None)
    return {
        "gpu_slots": [s.model_dump() for s in slots],
        "queue": [q.model_dump() for q in queue],
        "summary": {"total_gpus": len(slots), "free": free, "busy": busy, "queued_jobs": len(queue)},
    }
