"""FastAPI routes for Ray Serve deployments."""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.models import ServeDeploymentsResponse
from src.modules.serve import service

router = APIRouter()


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


@router.post("/deploy", status_code=202, tags=["serve"])
async def deploy_model(request: dict[str, Any]) -> dict[str, Any]:
    """Deploy a model for inference using Ray Serve.

    Args:
        request: Deployment request with model config.

    Returns:
        Deployment status dict.

    Raises:
        HTTPException: If deployment fails.
    """
    try:
        name = request.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="Model name required")

        result = await service.deploy_model(
            name=name,
            model_type=request.get("type", "unknown"),
            model_path=request.get("model"),
            num_replicas=request.get("num_replicas", 1),
        )

        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/undeploy", status_code=204, tags=["serve"])
async def undeploy_model(request: dict[str, str]) -> None:
    """Remove a Ray Serve deployment.

    Args:
        request: Request with model name to remove.

    Raises:
        HTTPException: If undeploy fails.
    """
    try:
        name = request.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="Model name required")

        await service.undeploy_model(name)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
