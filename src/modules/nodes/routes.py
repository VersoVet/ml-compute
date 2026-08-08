"""FastAPI routes for Ray cluster nodes monitoring."""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.models import NodesResponse
from src.modules.nodes import service

router = APIRouter()


@router.get("", response_model=NodesResponse)
async def get_nodes() -> NodesResponse:
    """Get all Ray worker nodes with resource availability.

    Returns:
        NodesResponse with list of workers and cluster status.

    Raises:
        HTTPException: If cluster not initialized.
    """
    try:
        result = await service.get_cluster_nodes()

        return NodesResponse(
            nodes=result["nodes"],
            cluster_status=result["cluster_status"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/summary", tags=["nodes"])
async def get_resource_summary() -> dict[str, Any]:
    """Get aggregated cluster resource summary.

    Returns:
        Dict with total/available resources and utilization %.
    """
    result = await service.get_resource_summary()

    return result
