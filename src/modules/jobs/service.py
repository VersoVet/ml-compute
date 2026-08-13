"""Ray Jobs API service layer."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

RAY_DASHBOARD_URL = os.environ.get("RAY_DASHBOARD_URL", "http://localhost:8265")


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
        submit_kwargs: Ray submission parameters (num_cpus, num_gpus, etc).

    Returns:
        Job submission response dict with job_id, status, timestamp.

    Raises:
        RuntimeError: If Ray is not initialized or submission fails.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        job_id = await client.submit_job(
            entrypoint=entrypoint,
            job_id=None,
            runtime_env=runtime_env or {},
            metadata={"name": name},
            **submit_kwargs or {},
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

        status = await client.get_job_status(job_id)
        logs = await client.get_job_logs(job_id)

        return {
            "job_id": job_id,
            "status": status.value if hasattr(status, "value") else str(status),
            "logs_tail": logs[-2000:] if logs else "",
        }
    except Exception as e:
        logger.error(f"Failed to get status for job {job_id}: {e}")
        raise RuntimeError(f"Failed to get job status: {e}")


async def list_jobs(
    status: str | None = None, limit: int = 100
) -> dict[str, Any]:
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

        jobs = await client.list_jobs()

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


async def delete_job(job_id: str) -> dict[str, str]:
    """Stop/delete a Ray job.

    Args:
        job_id: Ray job ID.

    Returns:
        Status dict.

    Raises:
        RuntimeError: If job not found or stop fails.
    """
    try:
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=RAY_DASHBOARD_URL)

        await client.stop_job(job_id)

        logger.info(f"Job {job_id} stopped")

        return {"job_id": job_id, "status": "STOPPED"}
    except Exception as e:
        logger.error(f"Failed to stop job {job_id}: {e}")
        raise RuntimeError(f"Failed to stop job: {e}")
