"""Proxy service for accessing SAM via Ray Serve.

Routes requests to SAM deployment on Ray Serve (auto-scheduled on GPU workers).
Backend migrated from Docker (10.0.0.26:9470) to Ray Serve on Ray cluster.
"""

import logging
from typing import Any

from src.modules.sam.serve import get_sam_manager

logger = logging.getLogger(__name__)


async def sam_health() -> dict[str, Any]:
    """Check SAM service health via Ray Serve.

    Returns:
        Health status dict.
    """
    try:
        manager = get_sam_manager()
        status = await manager.get_status()
        return {
            "status": status.get("status", "unknown"),
            "service": "sam-vit-b",
            "backend": "Ray Serve",
            "endpoint": status.get("endpoint"),
        }
    except Exception as e:
        logger.error(f"SAM health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def sam_ready() -> dict[str, Any]:
    """Check SAM service readiness.

    Returns:
        Readiness status dict.
    """
    try:
        manager = get_sam_manager()
        if not manager.is_deployed:
            return {"status": "not_ready", "reason": "SAM not deployed"}

        status = await manager.get_status()
        is_ready = status.get("status", "").lower() == "healthy"
        return {"status": "ready" if is_ready else "not_ready"}
    except Exception as e:
        logger.error(f"SAM readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}


async def sam_interact(payload: dict[str, Any]) -> dict[str, Any]:
    """Forward segmentation request to SAM via Ray Serve.

    Args:
        payload: Request dict with image, positive_points, negative_points.

    Returns:
        Segmentation result from SAM.
    """
    try:
        manager = get_sam_manager()
        result = await manager.interact(payload)
        return result
    except Exception as e:
        logger.error(f"SAM inference failed: {e}")
        return {"status": "error", "message": str(e)}


async def sam_info() -> dict[str, Any]:
    """Get SAM service info from Ray Serve.

    Returns:
        Service metadata.
    """
    try:
        manager = get_sam_manager()
        return await manager.info()
    except Exception as e:
        logger.error(f"Failed to get SAM info: {e}")
        return {
            "service": "SAM (Segment Anything Model)",
            "model": "vit_b",
            "backend": "Ray Serve",
            "error": str(e),
        }
