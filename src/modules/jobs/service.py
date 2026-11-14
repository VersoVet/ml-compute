"""Ray Jobs API service layer."""

import asyncio
import logging
import os
from typing import Any

from src.config import CONFIG

logger = logging.getLogger(__name__)

RAY_DASHBOARD_URL = os.environ.get("RAY_DASHBOARD_URL", CONFIG["endpoints"]["ray_dashboard"])


async def submit_job(
    name: str,
    entrypoint: str,
    runtime_env: dict[str, Any] | None = None,
    submit_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Submit a job to Ray cluster.

    Args:
        name: Job name.
        entrypoint: Command to run.
        runtime_env: Ray runtime environment config.
        submit_kwargs: Ray submission parameters (ignored for Ray 2.35.0).

    Returns:
        Job submission response dict with job_id, status, timestamp.

    Raises:
        RuntimeError: If Ray is not initialized or submission fails.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        # Map submit_kwargs to JobSubmissionClient parameters
        kwargs = submit_kwargs or {}
        entrypoint_num_gpus = kwargs.pop("num_gpus", None)
        entrypoint_num_cpus = kwargs.pop("num_cpus", None)
        entrypoint_memory = kwargs.pop("memory", None)

        # Default: training jobs always require GPU to avoid CPU scheduling on head
        if entrypoint_num_gpus is None and entrypoint_num_cpus is None:
            entrypoint_num_gpus = 1
            logger.info(f"Job {name}: defaulting to num_gpus=1 (force GPU worker)")

        # Filter remaining kwargs to only supported ones
        supported_kwargs = {}
        for key in kwargs:
            if key in ("submission_id", "entrypoint_resources"):
                supported_kwargs[key] = kwargs[key]

        job_id = client.submit_job(
            entrypoint=entrypoint,
            job_id=None,
            runtime_env=runtime_env or {},
            metadata={"name": name},
            entrypoint_num_gpus=entrypoint_num_gpus,
            entrypoint_num_cpus=entrypoint_num_cpus,
            entrypoint_memory=entrypoint_memory,
            **supported_kwargs,
        )

        logger.info(f"Job {job_id} submitted: {name}")

        return {
            "job_id": job_id,
            "status": "SUBMITTED",
            "name": name,
            "submission_time": None,
        }
    except Exception as e:
        logger.error(f"Failed to submit job {name}: {e}")
        raise RuntimeError(f"Job submission failed: {e}")


async def get_job_status(job_id: str) -> dict[str, Any]:
    """Get job status from Ray.

    Args:
        job_id: Ray job ID.

    Returns:
        Job status dict (status, logs, timestamps).

    Raises:
        RuntimeError: If job not found or Ray error.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        # Ray 2.35.0 API methods are synchronous
        status = client.get_job_status(job_id)
        logs = client.get_job_logs(job_id)

        return {
            "job_id": job_id,
            "status": status.value if hasattr(status, "value") else str(status),
            "logs_tail": logs[-2000:] if logs else "",
        }
    except Exception as e:
        logger.error(f"Failed to get status for job {job_id}: {e}")
        raise RuntimeError(f"Failed to get job status: {e}")


async def list_jobs(status: str | None = None, limit: int = 100) -> dict[str, Any]:
    """List jobs from Ray cluster.

    Args:
        status: Filter by status (SUBMITTED, RUNNING, SUCCEEDED, FAILED).
        limit: Max results.

    Returns:
        Dict with jobs list and total count.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        jobs = client.list_jobs()

        if status:
            jobs = [j for j in jobs if str(j.status) == status]

        return {
            "jobs": jobs[:limit],
            "total": len(jobs),
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        # Return empty list on error
        return {"jobs": [], "total": 0}


async def delete_job(job_id: str, worker_ip: str | None = None) -> dict[str, str]:
    """Stop a Ray job and kill orphan processes on the worker.

    Args:
        job_id: Ray job ID.
        worker_ip: Worker node IP to clean up orphan processes.

    Returns:
        Status dict.

    Raises:
        RuntimeError: If job not found or stop fails.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        client.stop_job(job_id)
        logger.info(f"Job {job_id} stopped via Ray")

        # Kill orphan processes on the worker node
        if worker_ip:
            await asyncio.sleep(2)
            await _kill_orphan_processes(worker_ip, job_id)

        return {"job_id": job_id, "status": "STOPPED"}
    except Exception as e:
        logger.error(f"Failed to stop job {job_id}: {e}")
        raise RuntimeError(f"Failed to stop job: {e}")


async def _kill_orphan_processes(worker_ip: str, job_id: str) -> None:
    """Kill orphan training processes on a worker node via SSH.

    Args:
        worker_ip: Worker node IP address.
        job_id: Ray job ID (for logging).
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "ssh",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "BatchMode=yes",
            f"onyx@{worker_ip}",
            "pkill -9 -f train_rotation; pkill -9 -f train_boneseg; pkill -9 -f train_multitask; pkill -9 -f train_yolo; pkill -9 -f train_efficientnet; echo done",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.wait(), timeout=10.0)
        logger.info("Orphan processes killed on %s (job %s)", worker_ip, job_id)
    except Exception as e:
        logger.warning("Failed to kill orphans on %s: %s", worker_ip, e)
