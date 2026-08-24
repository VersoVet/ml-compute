"""Pydantic models for compute backends."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BackendType(StrEnum):
    """Available compute backend types."""

    LOCAL = "local"
    LIGHTNING = "lightning"
    KAGGLE = "kaggle"


class JobStatus(StrEnum):
    """Unified job status across all backends."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ComputeJobRequest(BaseModel):
    """Request to submit a job to any backend."""

    name: str = Field(..., description="Job name (kebab-case)")
    entrypoint: str = Field(..., description="Python script path or inline command")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    gpu_required: bool = Field(default=True, description="Whether GPU is needed")
    backend: BackendType | None = Field(default=None, description="Backend to use (auto-select if None)")
    timeout_seconds: int = Field(default=3600, description="Max execution time")


class ComputeJobResponse(BaseModel):
    """Unified job status response."""

    job_id: str = Field(..., description="Backend-specific job identifier")
    name: str = Field(..., description="Job name")
    backend: BackendType = Field(..., description="Backend executing the job")
    status: JobStatus = Field(..., description="Current status")
    gpu: str | None = Field(default=None, description="GPU type used")
    duration_s: float | None = Field(default=None, description="Elapsed time in seconds")
    logs: str | None = Field(default=None, description="Last log lines")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error: str | None = Field(default=None, description="Error message if failed")


class BackendInfo(BaseModel):
    """Backend availability and capabilities."""

    name: str = Field(..., description="Display name")
    type: BackendType = Field(..., description="Backend type")
    available: bool = Field(..., description="Whether backend is reachable")
    gpu_types: list[str] = Field(default_factory=list, description="Available GPU types")
    free_quota: str | None = Field(default=None, description="Free tier limits")
    status_detail: str | None = Field(default=None, description="Additional status info")
