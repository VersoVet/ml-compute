"""Tests for compute backends module."""

import pytest

from src.modules.compute_backends.models import (
    BackendType,
    ComputeJobRequest,
    JobStatus,
)
from src.modules.compute_backends.service import BackendManager


def test_backend_types() -> None:
    """BackendType enum has expected values."""
    assert BackendType.LOCAL == "local"
    assert BackendType.LIGHTNING == "lightning"
    assert BackendType.KAGGLE == "kaggle"


def test_job_status_values() -> None:
    """JobStatus enum has all expected states."""
    assert len(JobStatus) == 6
    assert JobStatus.PENDING == "pending"
    assert JobStatus.SUCCEEDED == "succeeded"


def test_compute_job_request_defaults() -> None:
    """ComputeJobRequest has correct defaults."""
    req = ComputeJobRequest(name="test-job", entrypoint="python train.py")
    assert req.gpu_required is True
    assert req.backend is None
    assert req.timeout_seconds == 3600
    assert req.env_vars == {}


def test_compute_job_request_with_backend() -> None:
    """ComputeJobRequest accepts explicit backend."""
    req = ComputeJobRequest(
        name="test-job",
        entrypoint="python train.py",
        backend=BackendType.LIGHTNING,
        gpu_required=True,
        env_vars={"EPOCHS": "3"},
    )
    assert req.backend == BackendType.LIGHTNING
    assert req.env_vars["EPOCHS"] == "3"


def test_backend_manager_init() -> None:
    """BackendManager registers all backends."""
    mgr = BackendManager()
    assert BackendType.LOCAL in mgr.backends
    assert BackendType.LIGHTNING in mgr.backends
    assert BackendType.KAGGLE in mgr.backends
    assert len(mgr.backends) == 3


@pytest.mark.asyncio
async def test_get_status_unknown_job() -> None:
    """get_status returns UNKNOWN for untracked jobs."""
    mgr = BackendManager()
    result = await mgr.get_status("nonexistent-job-id")
    assert result.status == JobStatus.UNKNOWN
    assert result.error is not None


@pytest.mark.asyncio
async def test_get_logs_unknown_job() -> None:
    """get_logs returns message for untracked jobs."""
    mgr = BackendManager()
    logs = await mgr.get_logs("nonexistent-job-id")
    assert logs == "Job not tracked"


@pytest.mark.asyncio
async def test_stop_unknown_job() -> None:
    """stop_job returns False for untracked jobs."""
    mgr = BackendManager()
    result = await mgr.stop_job("nonexistent-job-id")
    assert result is False
