"""FastAPI routes for Ray Serve deployments."""

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.models import ServeDeploymentsResponse
from src.modules.serve import service

router = APIRouter()


class DeployRequest(BaseModel):
    """Request body for deploying a model via Ray Serve."""

    name: str = Field(..., description="Application/deployment name")
    type: str = Field("custom", description="Model type: bone-rotation, yolo, efficientnet, vllm, custom")
    model: str | None = Field(None, description="Path to model weights")
    num_replicas: int = Field(1, ge=1, le=8, description="Number of replicas")
    num_gpus: int = Field(0, ge=0, description="GPUs per replica")
    gpu_memory_utilization: float = Field(0.7, ge=0.1, le=1.0, description="vLLM GPU memory fraction")


class UndeployRequest(BaseModel):
    """Request body for removing a Ray Serve application."""

    name: str = Field(..., description="Application name to remove")


@router.get("/deployments", response_model=ServeDeploymentsResponse)
async def list_deployments() -> ServeDeploymentsResponse:
    """List active Ray Serve deployments (inference models).

    Returns:
        ServeDeploymentsResponse with deployments list.
    """
    result = await service.list_deployments()

    return ServeDeploymentsResponse(
        deployments=result.get("deployments", []),
        ray_serve_status=result.get("ray_serve_status", "unavailable"),
    )


@router.get("/status", tags=["serve"])
async def get_serve_status() -> dict[str, Any]:
    """Get Ray Serve global status.

    Returns:
        Serve status with application count and proxy info.
    """
    return await service.get_serve_status()


@router.post("/deploy", status_code=202, tags=["serve"])
async def deploy_model(request: DeployRequest) -> dict[str, Any]:
    """Deploy a model for inference using Ray Serve.

    Args:
        request: Deployment config with model type and replicas.

    Returns:
        Deployment status dict with endpoint URL.

    Raises:
        HTTPException: If deployment fails.
    """
    try:
        result = await service.deploy_model(
            name=request.name,
            model_type=request.type,
            model_path=request.model,
            num_replicas=request.num_replicas,
            num_gpus=request.num_gpus,
            gpu_memory_utilization=request.gpu_memory_utilization,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/undeploy", status_code=204, tags=["serve"])
async def undeploy_model(request: UndeployRequest) -> None:
    """Remove a Ray Serve application.

    Args:
        request: Request with application name to remove.

    Raises:
        HTTPException: If application not found or undeploy fails.
    """
    try:
        await service.undeploy_model(request.name)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/predict/{app_name}", tags=["serve"])
async def predict_inference(app_name: str, request: Request) -> dict[str, Any]:
    """Proxy prediction to a Ray Serve deployment.

    Args:
        app_name: Name of the deployed application.
        request: HTTP request with JSON body for the model.

    Returns:
        Prediction result from the model.

    Raises:
        HTTPException: If deployment is unavailable or returns error.
    """
    payload: dict[str, Any] = await request.json()
    try:
        return await service.predict(app_name, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except (httpx.ConnectError, httpx.ConnectTimeout):
        raise HTTPException(status_code=503, detail=f"Deployment '{app_name}' not reachable")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Inference unavailable: {e}")


@router.get("/deployments/{name}/status", tags=["serve"])
async def deployment_status(name: str) -> dict[str, Any]:
    """Get detailed status of a specific deployment.

    Args:
        name: Application name.

    Returns:
        Deployment status with replicas and health info.

    Raises:
        HTTPException: If application not found.
    """
    try:
        return await service.get_deployment_status(name)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
