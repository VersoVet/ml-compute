"""Compute backends service — unified job submission across providers."""

import logging

from src.modules.compute_backends.backends.base import ComputeBackend
from src.modules.compute_backends.backends.kaggle import KaggleBackend
from src.modules.compute_backends.backends.lightning import LightningBackend
from src.modules.compute_backends.backends.local import LocalBackend
from src.modules.compute_backends.models import (
    BackendInfo,
    BackendType,
    ComputeJobRequest,
    ComputeJobResponse,
    JobStatus,
)

logger = logging.getLogger(__name__)


class BackendManager:
    """Manages compute backends and routes jobs to the right provider."""

    def __init__(self) -> None:
        """Initialize all available backends."""
        self.backends: dict[BackendType, ComputeBackend] = {
            BackendType.LOCAL: LocalBackend(),
            BackendType.LIGHTNING: LightningBackend(),
            BackendType.KAGGLE: KaggleBackend(),
        }
        self._job_backend_map: dict[str, BackendType] = {}

    def _get_backend(self, backend_type: BackendType) -> ComputeBackend:
        """Get a backend by type.

        Args:
            backend_type: Backend to retrieve.

        Returns:
            Backend instance.

        Raises:
            ValueError: If backend type is unknown.
        """
        backend = self.backends.get(backend_type)
        if not backend:
            raise ValueError(f"Unknown backend: {backend_type}")
        return backend

    async def auto_select_backend(self, request: ComputeJobRequest) -> BackendType:
        """Auto-select the best available backend for a job.

        Priority: local (if healthy) > lightning > kaggle.

        Args:
            request: Job specification.

        Returns:
            Best available backend type.
        """
        for backend_type in [BackendType.LOCAL, BackendType.LIGHTNING, BackendType.KAGGLE]:
            try:
                info = await self.backends[backend_type].info()
                if info.available:
                    if request.gpu_required and not info.gpu_types:
                        continue
                    return backend_type
            except Exception:
                continue

        return BackendType.LOCAL

    async def submit_job(self, request: ComputeJobRequest) -> ComputeJobResponse:
        """Submit a job to the specified or auto-selected backend.

        Args:
            request: Job specification.

        Returns:
            Job response from the chosen backend.
        """
        backend_type = request.backend or await self.auto_select_backend(request)
        backend = self._get_backend(backend_type)

        logger.info(f"Submitting job '{request.name}' to {backend_type.value}")
        response = await backend.submit_job(request)

        self._job_backend_map[response.job_id] = backend_type
        return response

    async def get_status(self, job_id: str) -> ComputeJobResponse:
        """Get job status from the backend that ran it.

        Args:
            job_id: Job identifier.

        Returns:
            Current job status.
        """
        backend_type = self._job_backend_map.get(job_id)
        if not backend_type:
            return ComputeJobResponse(
                job_id=job_id,
                name="unknown",
                backend=BackendType.LOCAL,
                status=JobStatus.UNKNOWN,
                error="Job not tracked — unknown backend",
            )

        backend = self._get_backend(backend_type)
        return await backend.get_status(job_id)

    async def get_logs(self, job_id: str) -> str:
        """Get job logs from the backend that ran it.

        Args:
            job_id: Job identifier.

        Returns:
            Job log output.
        """
        backend_type = self._job_backend_map.get(job_id)
        if not backend_type:
            return "Job not tracked"

        backend = self._get_backend(backend_type)
        return await backend.get_logs(job_id)

    async def stop_job(self, job_id: str) -> bool:
        """Stop a job on its backend.

        Args:
            job_id: Job identifier.

        Returns:
            True if stopped successfully.
        """
        backend_type = self._job_backend_map.get(job_id)
        if not backend_type:
            return False

        backend = self._get_backend(backend_type)
        return await backend.stop_job(job_id)

    async def list_backends(self) -> list[BackendInfo]:
        """Get info for all registered backends.

        Returns:
            List of backend capabilities and availability.
        """
        results: list[BackendInfo] = []
        for backend in self.backends.values():
            try:
                info = await backend.info()
                results.append(info)
            except Exception as e:
                logger.error(f"Failed to get backend info: {e}")
        return results
