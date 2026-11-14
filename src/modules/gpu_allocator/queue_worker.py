"""Background worker — syncs Ray job status, cleans zombies, drains queue.

Runs as an asyncio task in the FastAPI lifespan. Polls every 10 seconds.
"""

import asyncio
import logging

from src.modules.gpu_allocator import allocator, state
from src.modules.jobs import service as jobs_service

logger = logging.getLogger(__name__)

POLL_INTERVAL_S = 10
_RAY_TERMINAL = {"SUCCEEDED", "FAILED", "STOPPED"}


async def sync_ray_status() -> list[str]:
    """Check Ray status for all assigned GPUs, release finished/zombie jobs.

    Returns:
        List of job_ids that were released.
    """
    assigned = await state.get_assigned_slots()
    released: list[str] = []

    for slot in assigned:
        job_id = slot.assigned_job_id
        if not job_id:
            continue
        try:
            result = await jobs_service.get_job_status(job_id)
            ray_status = result.get("status", "UNKNOWN")
            if ray_status in _RAY_TERMINAL:
                logger.info("Job %s finished (%s), releasing GPU %s", job_id, ray_status, slot.gpu_id)
                await allocator.release_job(job_id)
                released.append(job_id)
        except RuntimeError:
            # Ray 404 or unreachable — zombie job, kill orphan processes
            logger.warning("Zombie: job %s not in Ray, releasing GPU %s + killing orphans", job_id, slot.gpu_id)
            await allocator.release_job(job_id, kill_orphans=True)
            released.append(job_id)

    return released


async def _worker_loop(stop_event: asyncio.Event) -> None:
    """Main worker loop — sync, cleanup, drain."""
    logger.info("GPU queue worker started (poll every %ds)", POLL_INTERVAL_S)
    while not stop_event.is_set():
        try:
            released = await sync_ray_status()
            if released:
                drained = await allocator.drain_queue()
                if drained:
                    logger.info("Queue drain: %d job(s) submitted", drained)
            else:
                # Even without releases, check queue in case GPU freed by manual release
                queue = await state.get_queue()
                if queue:
                    free_gpu = await state.get_free_gpu()
                    if free_gpu:
                        await allocator.drain_queue()
        except Exception as e:
            logger.error("Queue worker error: %s", e)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL_S)
            break
        except TimeoutError:
            pass

    logger.info("GPU queue worker stopped")


_worker_task: asyncio.Task[None] | None = None
_stop_event: asyncio.Event | None = None


async def start_worker() -> None:
    """Start the background queue worker."""
    global _worker_task, _stop_event  # noqa: PLW0603
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop(_stop_event))


async def stop_worker() -> None:
    """Stop the background queue worker gracefully."""
    global _worker_task, _stop_event  # noqa: PLW0603
    if _stop_event:
        _stop_event.set()
    if _worker_task:
        try:
            await asyncio.wait_for(_worker_task, timeout=15.0)
        except TimeoutError:
            _worker_task.cancel()
        _worker_task = None
    _stop_event = None
