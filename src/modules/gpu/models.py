"""Pydantic models for GPU management on OnyxCortex."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class GPUMode(StrEnum):
    """Current GPU allocation mode."""

    INFERENCE = "inference"
    TRAINING = "training"
    MIXED = "mixed"


class ContainerState(BaseModel):
    """State of a Docker container on OnyxCortex."""

    name: str = Field(..., description="Container name")
    running: bool = Field(..., description="Whether the container is running")
    gpu_mib: int = Field(default=0, description="GPU memory used in MiB")


class GPUStatusResponse(BaseModel):
    """GPU status on OnyxCortex."""

    gpu_name: str = Field(..., description="GPU model name")
    gpu_memory_used_mib: int = Field(..., description="GPU memory used in MiB")
    gpu_memory_total_mib: int = Field(..., description="Total GPU memory in MiB")
    gpu_memory_free_mib: int = Field(..., description="Free GPU memory in MiB")
    mode: GPUMode = Field(..., description="Current GPU allocation mode")
    containers: list[ContainerState] = Field(..., description="SAM/MedSAM containers")
    acquired_at: datetime | None = Field(None, description="When GPU was acquired for training")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GPUAcquireResponse(BaseModel):
    """Response after acquiring GPU for training."""

    success: bool
    mode: GPUMode
    stopped_containers: list[str] = Field(default_factory=list)
    gpu_memory_free_mib: int = Field(default=0)
    message: str = ""


class GPUReleaseResponse(BaseModel):
    """Response after releasing GPU back to inference."""

    success: bool
    mode: GPUMode
    started_containers: list[str] = Field(default_factory=list)
    message: str = ""
