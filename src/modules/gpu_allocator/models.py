"""Pydantic models for GPU allocator."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GPUSlot(BaseModel):
    """Physical GPU slot in the cluster."""

    gpu_id: str = Field(..., description="Unique GPU identifier (e.g. tensor-0)")
    node: str = Field(..., description="Worker node name")
    node_ip: str = Field(..., description="Worker IP address")
    gpu_type: str = Field(..., description="GPU model name")
    vram_mb: int = Field(..., description="Total VRAM in MiB")
    assigned_job_id: str | None = Field(None, description="Ray job ID if busy")
    assigned_at: datetime | None = Field(None, description="Assignment timestamp")


class QueuedJob(BaseModel):
    """Job waiting in the GPU queue."""

    queue_id: int = Field(..., description="Queue entry ID")
    name: str = Field(..., description="Job name")
    entrypoint: str = Field(..., description="Command to run")
    runtime_env: dict[str, Any] = Field(default_factory=dict)
    submit_kwargs: dict[str, Any] = Field(default_factory=dict)
    queued_at: datetime = Field(..., description="Queue insertion time")
    status: str = Field("queued", description="queued, submitted, cancelled")


class AllocationResult(BaseModel):
    """Result of a submit_or_queue call."""

    allocated: bool = Field(..., description="True if GPU was assigned immediately")
    gpu_id: str | None = Field(None, description="Assigned GPU slot ID")
    job_id: str | None = Field(None, description="Ray job ID (if allocated)")
    queued: bool = Field(False, description="True if job was queued")
    queue_id: int | None = Field(None, description="Queue entry ID (if queued)")
    queue_position: int | None = Field(None, description="Position in queue")
    message: str = Field("", description="Human-readable status")
