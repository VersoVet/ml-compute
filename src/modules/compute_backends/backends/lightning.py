"""Lightning AI backend — runs jobs on Lightning Studios with GPU."""

import logging
import os
import time
from typing import Any

from src.modules.compute_backends.backends.base import ComputeBackend
from src.modules.compute_backends.models import (
    BackendInfo,
    BackendType,
    ComputeJobRequest,
    ComputeJobResponse,
    JobStatus,
)

logger = logging.getLogger(__name__)

STUDIO_NAME = "onyx-ml-worker"
TEAMSPACE = "default-project"
USERNAME = "verso4vet"


class LightningBackend(ComputeBackend):
    """Lightning AI Studios backend via Python SDK."""

    def __init__(self) -> None:
        """Initialize Lightning backend."""
        self._api_key: str | None = None
        self._jobs: dict[str, dict[str, Any]] = {}

    async def _get_api_key(self) -> str:
        """Retrieve API key from Vault.

        Returns:
            Lightning AI API key.
        """
        if self._api_key:
            return self._api_key

        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get("http://10.0.0.44:8050/vault/lightning_api_key", timeout=5.0)
            r.raise_for_status()
            self._api_key = r.json()["value"]

        os.environ["LIGHTNING_API_KEY"] = self._api_key
        return self._api_key

    def _get_studio(self) -> Any:
        """Get or create the Lightning Studio.

        Returns:
            Lightning Studio instance.
        """
        from lightning_sdk import Machine, Studio

        studio = Studio(name=STUDIO_NAME, teamspace=TEAMSPACE, user=USERNAME, create_ok=True)

        if studio.status.value != "running":
            studio.start()

        if studio.machine != Machine.T4:
            studio.switch_machine(Machine.T4)

        return studio

    async def submit_job(self, request: ComputeJobRequest) -> ComputeJobResponse:
        """Submit a job to Lightning AI Studio.

        Args:
            request: Job specification.

        Returns:
            Job response with tracking ID.
        """
        await self._get_api_key()

        job_id = f"lightning-{request.name}-{int(time.time())}"
        self._jobs[job_id] = {
            "name": request.name,
            "status": JobStatus.RUNNING,
            "start_time": time.time(),
        }

        try:
            studio = self._get_studio()

            env_exports = " ".join(f"export {k}={v} &&" for k, v in request.env_vars.items())
            command = f"{env_exports} {request.entrypoint}" if env_exports else request.entrypoint

            logger.info(f"Lightning job {job_id}: running on T4...")
            output = studio.run(command)

            self._jobs[job_id]["status"] = JobStatus.SUCCEEDED
            self._jobs[job_id]["output"] = output
            self._jobs[job_id]["duration"] = time.time() - self._jobs[job_id]["start_time"]

            logger.info(f"Lightning job {job_id}: completed in {self._jobs[job_id]['duration']:.1f}s")

            return ComputeJobResponse(
                job_id=job_id,
                name=request.name,
                backend=BackendType.LIGHTNING,
                status=JobStatus.SUCCEEDED,
                gpu="Tesla T4",
                duration_s=self._jobs[job_id]["duration"],
                logs=output[-2000:] if output else None,
            )
        except Exception as e:
            self._jobs[job_id]["status"] = JobStatus.FAILED
            self._jobs[job_id]["error"] = str(e)
            logger.error(f"Lightning job {job_id} failed: {e}")

            return ComputeJobResponse(
                job_id=job_id,
                name=request.name,
                backend=BackendType.LIGHTNING,
                status=JobStatus.FAILED,
                error=str(e),
            )

    async def get_status(self, job_id: str) -> ComputeJobResponse:
        """Get Lightning job status.

        Args:
            job_id: Job tracking ID.

        Returns:
            Current job status.
        """
        job = self._jobs.get(job_id)
        if not job:
            return ComputeJobResponse(
                job_id=job_id,
                name="unknown",
                backend=BackendType.LIGHTNING,
                status=JobStatus.UNKNOWN,
                error="Job not found",
            )

        return ComputeJobResponse(
            job_id=job_id,
            name=job["name"],
            backend=BackendType.LIGHTNING,
            status=job["status"],
            gpu="Tesla T4",
            duration_s=job.get("duration"),
            logs=job.get("output", "")[-2000:] if job.get("output") else None,
            error=job.get("error"),
        )

    async def get_logs(self, job_id: str) -> str:
        """Get Lightning job output.

        Args:
            job_id: Job tracking ID.

        Returns:
            Job output.
        """
        job = self._jobs.get(job_id)
        return job.get("output", "") if job else "Job not found"

    async def stop_job(self, job_id: str) -> bool:
        """Stop Lightning job (stops the Studio).

        Args:
            job_id: Job tracking ID.

        Returns:
            True if Studio stopped.
        """
        try:
            await self._get_api_key()
            studio = self._get_studio()
            studio.stop()
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = JobStatus.CANCELLED
            return True
        except Exception as e:
            logger.error(f"Failed to stop Lightning studio: {e}")
            return False

    async def stop_studio(self) -> bool:
        """Stop the Lightning Studio to preserve credits.

        Returns:
            True if stopped.
        """
        try:
            await self._get_api_key()
            from lightning_sdk import Studio

            studio = Studio(name=STUDIO_NAME, teamspace=TEAMSPACE, user=USERNAME)
            studio.stop()
            logger.info("Lightning Studio stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop studio: {e}")
            return False

    async def info(self) -> BackendInfo:
        """Get Lightning AI backend info.

        Returns:
            Backend capabilities.
        """
        available = False
        detail = "not configured"

        try:
            await self._get_api_key()
            from lightning_sdk import Studio

            studio = Studio(name=STUDIO_NAME, teamspace=TEAMSPACE, user=USERNAME)
            available = True
            detail = f"Studio '{STUDIO_NAME}' ({studio.status.value})"
        except Exception as e:
            detail = str(e)

        return BackendInfo(
            name="Lightning AI",
            type=BackendType.LIGHTNING,
            available=available,
            gpu_types=["Tesla T4 16GB"],
            free_quota="~22h GPU/mois",
            status_detail=detail,
        )
