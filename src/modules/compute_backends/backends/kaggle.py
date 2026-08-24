"""Kaggle backend — runs jobs as Kaggle Notebooks via CLI API."""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
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

KAGGLE_USERNAME = "versovet"

# Map Kaggle kernel status to unified status
_STATUS_MAP: dict[str, JobStatus] = {
    "queued": JobStatus.PENDING,
    "running": JobStatus.RUNNING,
    "complete": JobStatus.SUCCEEDED,
    "error": JobStatus.FAILED,
    "cancelAcknowledged": JobStatus.CANCELLED,
}


class KaggleBackend(ComputeBackend):
    """Kaggle Notebooks backend via kaggle CLI API."""

    def __init__(self) -> None:
        """Initialize Kaggle backend."""
        self._token: str | None = None
        self._jobs: dict[str, dict[str, Any]] = {}

    async def _setup_token(self) -> None:
        """Retrieve API token from Vault and configure kaggle client."""
        if self._token:
            return

        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get("http://10.0.0.44:8050/vault/kaggle_api_token", timeout=5.0)
            r.raise_for_status()
            self._token = r.json()["value"]

        os.environ["KAGGLE_API_TOKEN"] = self._token

        token_path = Path.home() / ".kaggle" / "access_token"
        token_path.parent.mkdir(exist_ok=True)
        token_path.write_text(self._token)
        token_path.chmod(0o600)

    async def submit_job(self, request: ComputeJobRequest) -> ComputeJobResponse:
        """Submit a job as a Kaggle kernel.

        Args:
            request: Job specification.

        Returns:
            Job response with kernel slug.
        """
        await self._setup_token()

        kernel_slug = request.name.lower().replace("_", "-")[:50]
        full_slug = f"{KAGGLE_USERNAME}/{kernel_slug}"

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata = {
                "id": full_slug,
                "title": request.name,
                "code_file": "script.py",
                "language": "python",
                "kernel_type": "script",
                "is_private": True,
                "enable_gpu": request.gpu_required,
                "enable_internet": True,
            }
            Path(tmpdir, "kernel-metadata.json").write_text(json.dumps(metadata))

            env_lines = "\n".join(f'os.environ["{k}"] = "{v}"' for k, v in request.env_vars.items())
            script = f"import os\n{env_lines}\n\n# Entrypoint\nimport subprocess\nsubprocess.run({request.entrypoint!r}, shell=True, check=True)\n"
            Path(tmpdir, "script.py").write_text(script)

            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()
            api.kernels_push(tmpdir)

        self._jobs[full_slug] = {"name": request.name, "start_time": time.time()}
        logger.info(f"Kaggle kernel pushed: {full_slug}")

        return ComputeJobResponse(
            job_id=full_slug,
            name=request.name,
            backend=BackendType.KAGGLE,
            status=JobStatus.PENDING,
            gpu="T4" if request.gpu_required else None,
        )

    async def get_status(self, job_id: str) -> ComputeJobResponse:
        """Get Kaggle kernel status.

        Args:
            job_id: Kernel slug (user/kernel-name).

        Returns:
            Current kernel status.
        """
        await self._setup_token()

        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        status_str = api.kernels_status(job_id)

        kaggle_status = "unknown"
        for key, val in _STATUS_MAP.items():
            if key.lower() in str(status_str).lower():
                kaggle_status = key
                break

        job_info = self._jobs.get(job_id, {})
        duration = time.time() - job_info.get("start_time", time.time()) if job_info else None

        return ComputeJobResponse(
            job_id=job_id,
            name=job_info.get("name", job_id),
            backend=BackendType.KAGGLE,
            status=_STATUS_MAP.get(kaggle_status, JobStatus.UNKNOWN),
            duration_s=duration,
        )

    async def get_logs(self, job_id: str) -> str:
        """Get Kaggle kernel output logs.

        Args:
            job_id: Kernel slug.

        Returns:
            Kernel log output (available only after completion).
        """
        await self._setup_token()

        with tempfile.TemporaryDirectory() as tmpdir:
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()
            api.kernels_output(job_id, path=tmpdir)

            log_file = next(Path(tmpdir).glob("*.log"), None)
            if log_file:
                raw = json.loads(log_file.read_text())
                return "\n".join(entry["data"] for entry in raw if entry.get("stream_name") == "stdout")
        return "No logs available"

    async def stop_job(self, job_id: str) -> bool:
        """Stop a Kaggle kernel (not supported via API).

        Args:
            job_id: Kernel slug.

        Returns:
            False (Kaggle does not support stopping kernels via API).
        """
        logger.warning("Kaggle API does not support stopping running kernels")
        return False

    async def info(self) -> BackendInfo:
        """Get Kaggle backend info.

        Returns:
            Backend capabilities.
        """
        available = False
        detail = "not configured"

        try:
            await self._setup_token()
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()
            available = True
            detail = f"User: {KAGGLE_USERNAME} (GPU pending verification)"
        except Exception as e:
            detail = str(e)

        return BackendInfo(
            name="Kaggle Notebooks",
            type=BackendType.KAGGLE,
            available=available,
            gpu_types=["Tesla T4 16GB"],
            free_quota="30h GPU/semaine",
            status_detail=detail,
        )
