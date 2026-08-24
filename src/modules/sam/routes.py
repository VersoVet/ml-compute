"""FastAPI routes for SAM Ray Serve deployment control.

Endpoints to manage SAM deployment lifecycle (start/stop/status).
"""

import logging
from typing import Any

from fastapi import APIRouter

from src.modules.sam.serve import get_sam_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["SAM Control"])


@router.post("/sam/deploy")
async def deploy_sam() -> dict[str, Any]:
    """Deploy SAM to Ray Serve with GPU reservation.

    Returns:
        Deployment status.
    """
    manager = get_sam_manager()
    success = await manager.deploy()
    return {
        "status": "deployed" if success else "failed",
        "deployment": manager.deployment_name,
        "endpoint": manager.endpoint,
    }


@router.post("/sam/undeploy")
async def undeploy_sam() -> dict[str, Any]:
    """Stop SAM Ray Serve deployment and free GPU.

    Returns:
        Undeployment status.
    """
    manager = get_sam_manager()
    success = await manager.undeploy()
    return {
        "status": "undeployed" if success else "failed",
        "deployment": manager.deployment_name,
    }


@router.get("/sam/deployment-status")
async def get_deployment_status() -> dict[str, Any]:
    """Get SAM deployment status on Ray Serve.

    Returns:
        Detailed deployment status.
    """
    manager = get_sam_manager()
    return await manager.get_status()
