"""Pydantic models for Nomad job specifications and status."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobPriority(int, Enum):
    """Nomad job priority levels."""

    LOW = 25
    NORMAL = 50
    HIGH = 75


class TaskGroupConstraint(BaseModel):
    """Resource constraint for task group."""

    task_name: str = Field(..., description="Task identifier")
    cpu_mhz: int = Field(default=1000, description="CPU allocation in MHz")
    memory_mb: int = Field(default=512, description="Memory in MB")
    num_gpus: int = Field(default=0, description="Number of GPUs (0-1)")


class NomadJobRequest(BaseModel):
    """Request to submit a job to Nomad."""

    name: str = Field(..., description="Job name (kebab-case, unique)")
    job_type: str = Field(
        default="batch", description="Job type: batch, service, system, sysbatch"
    )
    priority: JobPriority = Field(default=JobPriority.NORMAL)
    datacenters: list[str] = Field(default_factory=lambda: ["onyx-dc"])
    constraints: list[TaskGroupConstraint] = Field(default_factory=list)
    command: str = Field(..., description="Command to execute")
    image: Optional[str] = Field(
        default=None, description="Docker image (for Docker driver)"
    )
    driver: str = Field(default="docker", description="Driver: docker, raw_exec, exec")
    env_vars: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    volumes: dict[str, str] = Field(
        default_factory=dict, description="Host path -> container path mapping"
    )
    timeout_seconds: int = Field(
        default=3600, description="Job timeout in seconds"
    )
    max_retries: int = Field(default=0, description="Maximum restart attempts")


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    DEAD = "dead"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class AllocationStatus(BaseModel):
    """Status of a job allocation."""

    allocation_id: str = Field(..., description="Nomad allocation ID")
    job_id: str = Field(..., description="Job name")
    task_name: str = Field(..., description="Task name")
    status: TaskStatus = Field(..., description="Current status")
    node_id: str = Field(..., description="Nomad node ID")
    node_name: str = Field(..., description="Node hostname")
    cpu_used_mhz: int = Field(default=0, description="CPU usage in MHz")
    memory_used_mb: int = Field(default=0, description="Memory usage in MB")
    uptime_seconds: int = Field(default=0, description="Time running in seconds")
    exit_code: Optional[int] = Field(default=None, description="Exit code if finished")
    failure_reason: Optional[str] = Field(
        default=None, description="Failure reason if failed"
    )


class NomadJobStatus(BaseModel):
    """Complete status of a Nomad job."""

    job_id: str = Field(..., description="Job name")
    status: str = Field(..., description="Job status: pending, running, complete, failed, lost")
    priority: int = Field(..., description="Job priority")
    allocations: list[AllocationStatus] = Field(
        default_factory=list, description="Task allocations"
    )
    create_index: int = Field(..., description="Nomad create index")
    modify_index: int = Field(..., description="Nomad modify index")


class GPUStatus(BaseModel):
    """GPU status on a Nomad node."""

    node_id: str = Field(..., description="Nomad node ID")
    node_name: str = Field(..., description="Node hostname")
    num_gpus: int = Field(..., description="Total GPUs on node")
    available_gpus: int = Field(..., description="Free GPUs available for allocation")
    in_use: list[str] = Field(
        default_factory=list, description="Job IDs using GPUs"
    )


class NomadClusterStatus(BaseModel):
    """Cluster-wide status."""

    nodes_ready: int = Field(..., description="Nodes ready to accept jobs")
    nodes_total: int = Field(..., description="Total nodes in cluster")
    gpus_total: int = Field(..., description="Total GPUs across cluster")
    gpus_available: int = Field(..., description="Free GPUs available")
    jobs_running: int = Field(..., description="Running jobs")
    jobs_pending: int = Field(..., description="Pending jobs")
