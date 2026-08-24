"""FastAPI routes for SAM service proxy (Ray Serve backend).

Routes requests to SAM deployment on Ray Serve.
Endpoint remains compatible with bone-annotator clients (no breaking changes).
"""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.serve_proxy.service import sam_health, sam_info, sam_interact, sam_ready

logger = logging.getLogger(__name__)
router = APIRouter(tags=["SAM"])


class InteractRequest(BaseModel):
    """Request model for SAM interaction."""

    image: str | None = None
    positive_points: list[list[int]] = []
    negative_points: list[list[int]] = []


@router.get("/sam/status")
async def get_sam_health() -> dict[str, Any]:
    """Check SAM service health and status.

    Returns:
        Health status from SAM service.
    """
    return await sam_health()


@router.get("/sam/ready")
async def get_sam_ready() -> dict[str, Any]:
    """Check SAM service readiness.

    Returns:
        Readiness status from SAM service.
    """
    return await sam_ready()


@router.post("/sam/interact")
async def sam_segment(request: InteractRequest) -> dict[str, Any]:
    """Forward segmentation request to SAM via Ray Serve.

    Args:
        request: Image and point prompts for segmentation.

    Returns:
        Segmentation mask and metadata.
    """
    return await sam_interact(request.model_dump())


@router.get("/sam/info")
async def get_sam_info() -> dict[str, Any]:
    """Get SAM service information and resource specifications.

    Returns:
        SAM model specs and resource requirements.
    """
    return await sam_info()
