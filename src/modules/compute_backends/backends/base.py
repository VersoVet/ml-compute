"""Abstract base class for compute backends."""

from abc import ABC, abstractmethod

from src.modules.compute_backends.models import (
    BackendInfo,
    ComputeJobRequest,
    ComputeJobResponse,
)


class ComputeBackend(ABC):
    """Abstract interface that all compute backends must implement."""

    @abstractmethod
    async def submit_job(self, request: ComputeJobRequest) -> ComputeJobResponse:
        """Submit a job for execution.

        Args:
            request: Job specification.

        Returns:
            Job response with ID and initial status.
        """

    @abstractmethod
    async def get_status(self, job_id: str) -> ComputeJobResponse:
        """Get current status of a job.

        Args:
            job_id: Backend-specific job identifier.

        Returns:
            Current job status.
        """

    @abstractmethod
    async def get_logs(self, job_id: str) -> str:
        """Get job execution logs.

        Args:
            job_id: Backend-specific job identifier.

        Returns:
            Log output as string.
        """

    @abstractmethod
    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job.

        Args:
            job_id: Backend-specific job identifier.

        Returns:
            True if stopped successfully.
        """

    @abstractmethod
    async def info(self) -> BackendInfo:
        """Get backend availability and capabilities.

        Returns:
            Backend information.
        """
