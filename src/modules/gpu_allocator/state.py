"""GPU allocator state — PostgreSQL queries for gpu_slots and job_queue."""

import json
import logging
from typing import Any

from src.modules.gpu_allocator.db import get_pool
from src.modules.gpu_allocator.models import GPUSlot, QueuedJob

logger = logging.getLogger(__name__)


def _row_to_slot(row: Any) -> GPUSlot:
    """Convert asyncpg Record to GPUSlot."""
    return GPUSlot(
        gpu_id=row["gpu_id"],
        node=row["node"],
        node_ip=row["node_ip"],
        gpu_type=row["gpu_type"],
        vram_mb=row["vram_mb"],
        assigned_job_id=row["assigned_job_id"],
        assigned_at=row["assigned_at"],
    )


def _row_to_queued(row: Any) -> QueuedJob:
    """Convert asyncpg Record to QueuedJob."""
    rt = row["runtime_env"]
    sk = row["submit_kwargs"]
    return QueuedJob(
        queue_id=row["queue_id"],
        name=row["name"],
        entrypoint=row["entrypoint"],
        runtime_env=rt if isinstance(rt, dict) else json.loads(rt or "{}"),
        submit_kwargs=sk if isinstance(sk, dict) else json.loads(sk or "{}"),
        queued_at=row["queued_at"],
        status=row["status"],
    )


async def get_free_gpu(prefer_cortex: bool = False) -> GPUSlot | None:
    """Find a free GPU slot with priority-based routing.

    Args:
        prefer_cortex: If True, prefer Cortex (bone jobs). Otherwise prefer Tensor.

    Returns:
        Free GPUSlot or None if all busy.
    """
    # Cortex-preferred: cortex first (priority 1), then tensor
    # Tensor-preferred: tensor first, then cortex
    if prefer_cortex:
        order = "CASE WHEN node LIKE '%cortex%' THEN 0 ELSE 1 END, gpu_id"
    else:
        order = "CASE WHEN node LIKE '%tensor%' THEN 0 ELSE 1 END, gpu_id"

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""SELECT * FROM ml_compute.gpu_slots
               WHERE assigned_job_id IS NULL
               ORDER BY {order}
               LIMIT 1""",
        )
    return _row_to_slot(row) if row else None


async def assign_gpu(gpu_id: str, job_id: str) -> bool:
    """Assign a GPU to a job atomically.

    Args:
        gpu_id: GPU slot identifier.
        job_id: Ray job ID.

    Returns:
        True if assigned, False if already taken (race condition).
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE ml_compute.gpu_slots
               SET assigned_job_id = $1, assigned_at = NOW()
               WHERE gpu_id = $2 AND assigned_job_id IS NULL""",
            job_id,
            gpu_id,
        )
    assigned = result.endswith("1")
    if assigned:
        logger.info("GPU %s assigned to job %s", gpu_id, job_id)
    return assigned


async def release_gpu_by_job(job_id: str) -> str | None:
    """Release a GPU by its assigned job ID.

    Args:
        job_id: Ray job ID to release.

    Returns:
        The gpu_id that was freed, or None if not found.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE ml_compute.gpu_slots
               SET assigned_job_id = NULL, assigned_at = NULL
               WHERE assigned_job_id = $1
               RETURNING gpu_id, node""",
            job_id,
        )
    if row:
        logger.info("GPU %s released (job %s finished)", row["gpu_id"], job_id)
        return row["gpu_id"]
    return None


async def get_gpu_node(gpu_id: str) -> str | None:
    """Get the node name for a GPU slot.

    Args:
        gpu_id: GPU slot identifier.

    Returns:
        Node name or None.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT node FROM ml_compute.gpu_slots WHERE gpu_id = $1",
            gpu_id,
        )
    return row["node"] if row else None


async def enqueue_job(
    name: str,
    entrypoint: str,
    runtime_env: dict[str, Any],
    submit_kwargs: dict[str, Any],
) -> int:
    """Add a job to the GPU queue.

    Returns:
        Queue entry ID.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO ml_compute.job_queue (name, entrypoint, runtime_env, submit_kwargs)
               VALUES ($1, $2, $3::jsonb, $4::jsonb)
               RETURNING queue_id""",
            name,
            entrypoint,
            json.dumps(runtime_env),
            json.dumps(submit_kwargs),
        )
    queue_id: int = row["queue_id"]
    logger.info("Job '%s' queued (queue_id=%d)", name, queue_id)
    return queue_id


async def dequeue_next() -> QueuedJob | None:
    """Dequeue the next pending job (FIFO, atomic).

    Returns:
        QueuedJob or None if queue empty.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """SELECT * FROM ml_compute.job_queue
                   WHERE status = 'queued'
                   ORDER BY queued_at
                   LIMIT 1
                   FOR UPDATE SKIP LOCKED""",
            )
            if not row:
                return None
            await conn.execute(
                "UPDATE ml_compute.job_queue SET status = 'submitted' WHERE queue_id = $1",
                row["queue_id"],
            )
    return _row_to_queued(row)


async def cancel_queued(queue_id: int) -> bool:
    """Cancel a queued job.

    Returns:
        True if cancelled, False if not found or already submitted.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE ml_compute.job_queue SET status = 'cancelled'
               WHERE queue_id = $1 AND status = 'queued'""",
            queue_id,
        )
    return result.endswith("1")


async def get_queue_position(queue_id: int) -> int:
    """Get position of a job in the queue (1-based).

    Returns:
        Position or 0 if not in queue.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT COUNT(*) + 1 AS pos FROM ml_compute.job_queue
               WHERE status = 'queued' AND queued_at < (
                   SELECT queued_at FROM ml_compute.job_queue WHERE queue_id = $1
               )""",
            queue_id,
        )
    return row["pos"] if row else 0


async def get_all_slots() -> list[GPUSlot]:
    """Get all GPU slots with their assignment status."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM ml_compute.gpu_slots ORDER BY gpu_id")
    return [_row_to_slot(r) for r in rows]


async def get_queue() -> list[QueuedJob]:
    """Get all queued (pending) jobs."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM ml_compute.job_queue WHERE status = 'queued' ORDER BY queued_at",
        )
    return [_row_to_queued(r) for r in rows]


async def get_assigned_slots() -> list[GPUSlot]:
    """Get GPU slots that have a job assigned."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM ml_compute.gpu_slots WHERE assigned_job_id IS NOT NULL",
        )
    return [_row_to_slot(r) for r in rows]
