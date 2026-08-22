"""Proxy service for accessing SAM Docker container via ml-compute API.

Routes requests to SAM service running on OnyxCortex:9470.
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# SAM service address (configurable via env or default)
SAM_HOST = "10.0.0.26"  # OnyxCortex IP
SAM_PORT = 9470
SAM_BASE_URL = f"http://{SAM_HOST}:{SAM_PORT}"
TIMEOUT = 30.0


async def sam_health() -> dict[str, Any]:
    """Check SAM service health.

    Returns:
        Health status dict.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{SAM_BASE_URL}/health")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"SAM health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def sam_ready() -> dict[str, Any]:
    """Check SAM service readiness.

    Returns:
        Readiness status dict.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{SAM_BASE_URL}/ready")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"SAM readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}


async def sam_interact(payload: dict[str, Any]) -> dict[str, Any]:
    """Forward segmentation request to SAM service.

    Args:
        payload: Request dict with image, positive_points, negative_points.

    Returns:
        Segmentation result from SAM.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{SAM_BASE_URL}/api/interact",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"SAM inference failed: {e}")
        return {"status": "error", "message": str(e)}


async def sam_info() -> dict[str, Any]:
    """Get SAM service info.

    Returns:
        Service metadata.
    """
    return {
        "service": "SAM (Segment Anything Model)",
        "model": "vit_b",
        "backend": "Docker",
        "host": SAM_HOST,
        "port": SAM_PORT,
        "endpoint": f"{SAM_BASE_URL}/api/interact",
        "gpu_reserved": 1.0,
        "vram_required_gb": 10,
        "vram_available_onyxcortex_gb": 12,
        "inference_latency_ms": "500-1000",
        "status_endpoint": f"{SAM_BASE_URL}/health",
    }
