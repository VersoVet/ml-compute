"""FastAPI wrapper for Ray ML orchestrator.

Provides HTTP API for:
- Submitting ML training/inference jobs to Ray
- Monitoring Ray cluster and workers
- Managing Ray Serve deployments
- Listing available models
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from onyx_sdk import OnyxClient

# Status constants for SDK visibility
SKILL_STATUS_UP = "UP"
SKILL_STATUS_DOWN = "DOWN"
SKILL_STATUS_WORKING = "WORKING"

_skill_status = None

from src.models import (
    HealthResponse,
    PageInfo,
    PagesResponse,
    ReadyResponse,
)
from src.modules.jobs import routes as jobs_routes
from src.modules.models import routes as models_routes
from src.modules.nodes import routes as nodes_routes
from src.modules.serve import routes as serve_routes

logger = logging.getLogger("ml-compute")


class RayClient:
    """Wrapper for Ray cluster connection."""

    def __init__(self, ray_address: str = "ray://10.0.0.44:6379"):
        """Initialize Ray client.

        Args:
            ray_address: Ray head node address.
        """
        self.ray_address = ray_address
        self._client = None

    async def connect(self) -> None:
        """Connect to Ray cluster."""
        try:
            import ray

            if not ray.is_initialized():
                ray.init(address=self.ray_address, ignore_reinit_error=True)
            logger.info(f"Connected to Ray at {self.ray_address}")
        except Exception as e:
            logger.error(f"Failed to connect to Ray: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Ray cluster."""
        try:
            import ray

            if ray.is_initialized():
                ray.shutdown()
            logger.info("Disconnected from Ray")
        except Exception as e:
            logger.error(f"Failed to disconnect from Ray: {e}")

    async def health_check(self) -> dict:
        """Check Ray cluster health.

        Returns:
            Cluster health status dict.
        """
        try:
            import ray

            if not ray.is_initialized():
                return {
                    "status": "unhealthy",
                    "reason": "Ray not initialized",
                }

            cluster_info = ray.cluster_resources()
            return {
                "status": "healthy" if cluster_info else "unhealthy",
                "resources": cluster_info,
                "workers": len(ray.nodes()),
            }
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}


# Global clients
ray_client = RayClient()
onyx_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI app lifecycle.

    Connects to Ray on startup, disconnects on shutdown.
    Initializes OnyxClient for status publishing.
    """
    global onyx_client

    # Startup
    await ray_client.connect()

    try:
        _skill_status = OnyxClient(skill_name="ml-compute")
        # Publish UP status (skill is now online)
        await _skill_status.start()
        # Signal that orchestration is ready and processing
        await _skill_status.set_working()
        onyx_client = _skill_status
        # Pass client to modules for status publishing
        from src.modules.jobs import routes as jobs_routes
        jobs_routes.set_onyx_client(onyx_client)
        logger.info("OnyxClient connected and status UP/WORKING")
    except Exception as e:
        logger.error(f"OnyxClient initialization failed: {e}")
        raise

    yield

    # Shutdown
    if onyx_client:
        try:
            # Publish DOWN status (skill is offline)
            await onyx_client.stop()
            logger.info("OnyxClient status DOWN published")
        except Exception as e:
            logger.warning(f"Failed to publish shutdown status: {e}")

    await ray_client.disconnect()


app = FastAPI(
    title="ml-compute",
    description="Ray ML orchestrator API",
    version="0.1.0",
    lifespan=lifespan,
)


# Include routers
app.include_router(jobs_routes.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(nodes_routes.router, prefix="/api/nodes", tags=["nodes"])
app.include_router(serve_routes.router, prefix="/api/serve", tags=["serve"])
app.include_router(models_routes.router, prefix="/api/models", tags=["models"])


@app.get("/health", response_model=HealthResponse, tags=["status"])
async def health() -> HealthResponse:
    """Health check endpoint for cluster and workers.

    Returns:
        HealthResponse with cluster status.

    Raises:
        HTTPException: If cluster is unhealthy.
    """
    # Signal active processing during health check
    if onyx_client:
        try:
            await onyx_client.set_working()
        except Exception as e:
            logger.debug(f"Failed to signal WORKING during health check: {e}")

    cluster_health = await ray_client.health_check()

    if cluster_health["status"] != "healthy":
        logger.warning(f"Cluster unhealthy: {cluster_health}")
        raise HTTPException(status_code=503, detail=cluster_health)

    return HealthResponse(
        status="healthy",
        ray_cluster={
            "head_node": "10.0.0.44",
            "port": 6379,
            "status": "running",
            "workers_connected": cluster_health.get("workers", 0),
            "resources": cluster_health.get("resources", {}),
        },
    )


@app.get("/ready", response_model=ReadyResponse, tags=["status"])
async def ready() -> ReadyResponse:
    """Readiness check for dependencies.

    Returns:
        ReadyResponse indicating if service is ready.
    """
    # Signal active processing during readiness check
    if onyx_client:
        try:
            await onyx_client.set_working()
        except Exception as e:
            logger.debug(f"Failed to signal WORKING during readiness check: {e}")

    cluster_health = await ray_client.health_check()
    dependencies = {
        "ray_cluster": "ready"
        if cluster_health["status"] == "healthy"
        else "not_ready"
    }

    return ReadyResponse(
        status="ready" if all(v == "ready" for v in dependencies.values()) else "not_ready",
        dependencies=dependencies,
    )


@app.get("/pages", response_model=PagesResponse, tags=["ui"])
async def get_pages() -> PagesResponse:
    """List UI pages for Onyx portal registration.

    Returns:
        List of available pages with metadata.
    """
    pages = [
        PageInfo(
            id="dashboard",
            label="Dashboard",
            path="/",
            icon="📊",
            order=0,
        ),
        PageInfo(
            id="jobs",
            label="Jobs",
            path="/jobs",
            icon="⚙️",
            order=1,
        ),
        PageInfo(
            id="nodes",
            label="Workers",
            path="/nodes",
            icon="🖥️",
            order=2,
        ),
        PageInfo(
            id="models",
            label="Models",
            path="/models",
            icon="🧠",
            order=3,
        ),
    ]

    return PagesResponse(pages=pages)


@app.get("/", tags=["ui"])
async def root() -> dict:
    """Root endpoint returning API info.

    Returns:
        API information dict.
    """
    # Signal active processing if available
    if onyx_client:
        try:
            await onyx_client.publish_status("WORKING")
        except Exception:
            pass

    return {
        "service": "ml-compute",
        "version": "0.1.0",
        "description": "Ray ML orchestrator API",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=9469,
        reload=False,
        log_level="info",
    )
