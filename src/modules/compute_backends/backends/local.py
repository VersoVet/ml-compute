"""Local backend — delegates to existing Ray Jobs API."""

import logging
from typing import Any

import httpx

from src.config import CONFIG
from src.modules.compute_backends.backends.base import ComputeBackend
from src.modules.compute_backends.models import (
    BackendInfo,
    BackendType,
    ComputeJobRequest,
    ComputeJobResponse,
    JobStatus,
)

logger = logging.getLogger(__name__)

RAY_DASHBOARD_URL = CONFIG["endpoints"]["ray_dashboard"]

# Map Ray status to unified status
_STATUS_MAP: dict[str, JobStatus] = {
    "PENDING": JobStatus.PENDING,
    "RUNNING": JobStatus.RUNNING,
    "SUCCEEDED": JobStatus.SUCCEEDED,
    "FAILED": JobStatus.FAILED,
    "STOPPED": JobStatus.CANCELLED,
}


class LocalBackend(ComputeBackend):
    """Local Ray cluster backend via Dashboard HTTP API."""

    async def submit_job(self, request: ComputeJobRequest) -> ComputeJobResponse:
        """Submit a job to the local Ray cluster.

        Args:
            request: Job specification.

        Returns:
            Job response with Ray job ID.
        """
        payload: dict[str, Any] = {
            "entrypoint": request.entrypoint,
            "runtime_env": {"env_vars": request.env_vars},
            "metadata": {"name": request.name},
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{RAY_DASHBOARD_URL}/api/jobs/",
                json=payload,
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()

        job_id = data.get("job_id", data.get("submission_id", ""))
        logger.info(f"Local job submitted: {job_id}")

        return ComputeJobResponse(
            job_id=job_id,
            name=request.name,
            backend=BackendType.LOCAL,
            status=JobStatus.PENDING,
            gpu="RTX 4070 SUPER" if request.gpu_required else None,
        )

    async def get_status(self, job_id: str) -> ComputeJobResponse:
        """Get Ray job status.

        Args:
            job_id: Ray job ID.

        Returns:
            Current job status.
        """
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{RAY_DASHBOARD_URL}/api/jobs/{job_id}",
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()

        ray_status = data.get("status", "UNKNOWN")
        return ComputeJobResponse(
            job_id=job_id,
            name=data.get("metadata", {}).get("name", job_id),
            backend=BackendType.LOCAL,
            status=_STATUS_MAP.get(ray_status, JobStatus.UNKNOWN),
        )

    async def get_logs(self, job_id: str) -> str:
        """Get Ray job logs.

        Args:
            job_id: Ray job ID.

        Returns:
            Job log output.
        """
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{RAY_DASHBOARD_URL}/api/jobs/{job_id}/logs",
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()

        return data.get("logs", "")

    async def stop_job(self, job_id: str) -> bool:
        """Stop a Ray job.

        Args:
            job_id: Ray job ID.

        Returns:
            True if stopped.
        """
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{RAY_DASHBOARD_URL}/api/jobs/{job_id}/stop",
                    timeout=10.0,
                )
                r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to stop local job {job_id}: {e}")
            return False

    async def info(self) -> BackendInfo:
        """Get local cluster info.

        Returns:
            Local backend capabilities.
        """
        available = False
        gpu_types: list[str] = []
        detail = "unreachable"

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{RAY_DASHBOARD_URL}/api/v0/nodes", timeout=5.0)
                r.raise_for_status()
            available = True
            gpu_types = ["RTX 4070 SUPER 12GB", "T1000 8GB"]
            detail = "Ray cluster healthy"
        except Exception as e:
            detail = str(e)

        return BackendInfo(
            name="Local Ray Cluster",
            type=BackendType.LOCAL,
            available=available,
            gpu_types=gpu_types,
            free_quota="Unlimited (on-premise)",
            status_detail=detail,
        )
