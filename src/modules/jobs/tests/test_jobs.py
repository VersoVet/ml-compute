"""Tests for Ray Jobs service layer."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.modules.jobs import service

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _mock_job_submission_client(
    submit_return: str = "raysubmit_abc123",
    status_return: str = "RUNNING",
    logs_return: str = "epoch 1/10 loss=0.5",
    list_return: list | None = None,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Build a fake JobSubmissionClient with async methods.

    Args:
        submit_return: Value returned by submit_job.
        status_return: Value returned by get_job_status.
        logs_return: Value returned by get_job_logs.
        list_return: Value returned by list_jobs.
        side_effect: Exception to raise on all calls.

    Returns:
        MagicMock configured as a JobSubmissionClient.
    """
    client = MagicMock()

    if side_effect:
        client.submit_job = AsyncMock(side_effect=side_effect)
        client.get_job_status = AsyncMock(side_effect=side_effect)
        client.get_job_logs = AsyncMock(side_effect=side_effect)
        client.list_jobs = AsyncMock(side_effect=side_effect)
        client.stop_job = AsyncMock(side_effect=side_effect)
    else:
        client.submit_job = AsyncMock(return_value=submit_return)

        status_mock = MagicMock()
        status_mock.value = status_return
        client.get_job_status = AsyncMock(return_value=status_mock)
        client.get_job_logs = AsyncMock(return_value=logs_return)

        if list_return is None:
            list_return = []
        client.list_jobs = AsyncMock(return_value=list_return)
        client.stop_job = AsyncMock(return_value=None)

    return client


def _make_job_info(submission_id: str, status: str, name: str = "test") -> MagicMock:
    """Build a fake Ray JobInfo object.

    Args:
        submission_id: Job submission ID.
        status: Job status string.
        name: Job name in metadata.

    Returns:
        MagicMock mimicking a Ray JobInfo.
    """
    job = MagicMock()
    job.submission_id = submission_id
    job.status = status
    job.metadata = {"name": name}
    return job


def _patch_ray_client(mock_client: MagicMock):
    """Create a context manager that patches ray.job_submission.JobSubmissionClient.

    The service imports JobSubmissionClient inside each function via
    ``from ray.job_submission import JobSubmissionClient``.  We inject a
    fake ``ray.job_submission`` module into ``sys.modules`` whose
    ``JobSubmissionClient`` attribute is a class returning *mock_client*.

    Args:
        mock_client: Pre-configured mock client instance.

    Returns:
        Context manager that patches the import.
    """
    mock_cls = MagicMock(return_value=mock_client)
    mock_job_sub = MagicMock()
    mock_job_sub.JobSubmissionClient = mock_cls

    mock_ray = MagicMock()
    mock_ray.job_submission = mock_job_sub

    return patch.dict(
        sys.modules,
        {"ray": mock_ray, "ray.job_submission": mock_job_sub},
    )


# ---------------------------------------------------------------------------
# service.submit_job
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_job_success() -> None:
    """submit_job returns job_id and SUBMITTED status on success."""
    mock_client = _mock_job_submission_client(submit_return="raysubmit_xyz789")

    with _patch_ray_client(mock_client):
        result = await service.submit_job(
            name="train-yolo",
            entrypoint="python train.py",
            runtime_env={"pip": ["torch"]},
        )

    assert result["job_id"] == "raysubmit_xyz789"
    assert result["status"] == "SUBMITTED"
    assert result["name"] == "train-yolo"
    mock_client.submit_job.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_job_failure_raises_runtime_error() -> None:
    """submit_job raises RuntimeError when Ray submission fails."""
    mock_client = _mock_job_submission_client(
        side_effect=ConnectionError("Ray cluster unreachable"),
    )

    with _patch_ray_client(mock_client):
        with pytest.raises(RuntimeError, match="Job submission failed"):
            await service.submit_job(
                name="failing-job",
                entrypoint="python fail.py",
            )


# ---------------------------------------------------------------------------
# service.get_job_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_job_status_success() -> None:
    """get_job_status returns status and truncated logs."""
    mock_client = _mock_job_submission_client(
        status_return="SUCCEEDED",
        logs_return="Training complete. Accuracy: 0.95",
    )

    with _patch_ray_client(mock_client):
        result = await service.get_job_status("raysubmit_abc123")

    assert result["job_id"] == "raysubmit_abc123"
    assert result["status"] == "SUCCEEDED"
    assert "Accuracy: 0.95" in result["logs_tail"]
    mock_client.get_job_status.assert_awaited_once_with("raysubmit_abc123")
    mock_client.get_job_logs.assert_awaited_once_with("raysubmit_abc123")


@pytest.mark.asyncio
async def test_get_job_status_not_found_raises_runtime_error() -> None:
    """get_job_status raises RuntimeError when job ID does not exist."""
    mock_client = _mock_job_submission_client(
        side_effect=ValueError("Job raysubmit_ghost not found"),
    )

    with _patch_ray_client(mock_client):
        with pytest.raises(RuntimeError, match="Failed to get job status"):
            await service.get_job_status("raysubmit_ghost")


# ---------------------------------------------------------------------------
# service.list_jobs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_jobs_returns_jobs_list() -> None:
    """list_jobs returns all jobs from Ray cluster."""
    jobs = [
        _make_job_info("job_1", "RUNNING", "train-yolo"),
        _make_job_info("job_2", "SUCCEEDED", "eval-model"),
    ]
    mock_client = _mock_job_submission_client(list_return=jobs)

    with _patch_ray_client(mock_client):
        result = await service.list_jobs()

    assert result["total"] == 2
    assert len(result["jobs"]) == 2


@pytest.mark.asyncio
async def test_list_jobs_with_status_filter() -> None:
    """list_jobs filters results by status string."""
    jobs = [
        _make_job_info("job_1", "RUNNING", "train"),
        _make_job_info("job_2", "SUCCEEDED", "eval"),
        _make_job_info("job_3", "RUNNING", "train-2"),
    ]
    mock_client = _mock_job_submission_client(list_return=jobs)

    with _patch_ray_client(mock_client):
        result = await service.list_jobs(status="RUNNING")

    assert result["total"] == 2
    assert len(result["jobs"]) == 2


@pytest.mark.asyncio
async def test_list_jobs_returns_empty_on_error() -> None:
    """list_jobs returns empty list when Ray connection fails."""
    mock_client = _mock_job_submission_client(
        side_effect=ConnectionError("Ray unreachable"),
    )

    with _patch_ray_client(mock_client):
        result = await service.list_jobs()

    assert result["jobs"] == []
    assert result["total"] == 0


# ---------------------------------------------------------------------------
# service.delete_job
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_job_success() -> None:
    """delete_job stops the job and returns STOPPED status."""
    mock_client = _mock_job_submission_client()

    with _patch_ray_client(mock_client):
        result = await service.delete_job("raysubmit_abc123")

    assert result["job_id"] == "raysubmit_abc123"
    assert result["status"] == "STOPPED"
    mock_client.stop_job.assert_awaited_once_with("raysubmit_abc123")


@pytest.mark.asyncio
async def test_delete_job_failure_raises_runtime_error() -> None:
    """delete_job raises RuntimeError when stop fails."""
    mock_client = _mock_job_submission_client(
        side_effect=ValueError("Job not found"),
    )

    with _patch_ray_client(mock_client):
        with pytest.raises(RuntimeError, match="Failed to stop job"):
            await service.delete_job("raysubmit_ghost")
