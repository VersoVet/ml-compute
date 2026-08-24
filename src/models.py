"""Pydantic models for ml-compute API."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status: healthy/unhealthy")
    ray_cluster: dict[str, Any] = Field(..., description="Ray cluster info")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str = Field(..., description="Ready status: ready/not_ready")
    dependencies: dict[str, str] = Field(default_factory=dict, description="Dependency status")


class JobSubmitRequest(BaseModel):
    """Job submission request for Ray Jobs API."""

    name: str = Field(..., description="Job name")
    entrypoint: str = Field(..., description="Command to run")
    runtime_env: dict[str, Any] = Field(default_factory=dict, description="Ray runtime environment")
    submit_kwargs: dict[str, Any] = Field(default_factory=dict, description="Ray job submission parameters")


class JobResponse(BaseModel):
    """Job status response."""

    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status: SUBMITTED/RUNNING/SUCCEEDED/FAILED")
    name: str = Field(..., description="Job name")
    submission_time: datetime | None = Field(None, description="Submission timestamp")
    start_time: datetime | None = Field(None, description="Start timestamp")
    end_time: datetime | None = Field(None, description="End timestamp")
    runtime: float | None = Field(None, description="Runtime in seconds")


class NodesResponse(BaseModel):
    """Cluster nodes status response."""

    nodes: list[dict[str, Any]] = Field(..., description="List of worker nodes")
    cluster_status: str = Field(..., description="Cluster status")


class ModelInfo(BaseModel):
    """Model metadata."""

    id: str = Field(..., description="Model ID")
    type: str = Field(..., description="Model type (yolo/efficientnet/vllm)")
    size_mb: float = Field(..., description="Size in MB")
    path: str = Field(..., description="Full path to model file")
    created: datetime = Field(..., description="Creation timestamp")
    source_job: str | None = Field(None, description="Source job ID")


class ModelsResponse(BaseModel):
    """Models list response."""

    models: list[ModelInfo] = Field(..., description="Available models")
    total: int = Field(..., description="Total count")


class DeploymentInfo(BaseModel):
    """Ray Serve deployment info."""

    name: str = Field(..., description="Deployment name")
    status: str = Field(..., description="Deployment status")
    replicas: int = Field(..., description="Number of replicas")
    memory: int | None = Field(None, description="Memory per replica")
    endpoint: str | None = Field(None, description="Serving endpoint")


class ServeDeploymentsResponse(BaseModel):
    """Ray Serve deployments list."""

    deployments: list[DeploymentInfo] = Field(..., description="Deployments")
    ray_serve_status: str = Field(..., description="Ray Serve status")


class PageInfo(BaseModel):
    """UI page metadata."""

    id: str = Field(..., description="Page ID")
    label: str = Field(..., description="Display label")
    path: str = Field(..., description="URL path")
    icon: str | None = Field(None, description="Icon emoji or name")
    order: int = Field(default=0, description="Display order")


class PagesResponse(BaseModel):
    """List of UI pages for portal."""

    pages: list[PageInfo] = Field(..., description="Available pages")
