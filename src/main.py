"""FastAPI wrapper for Ray ML orchestrator.

Provides HTTP API for:
- Submitting ML training/inference jobs to Ray
- Monitoring Ray cluster and workers
- Managing Ray Serve deployments
- Listing available models
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from onyx_sdk import OnyxClient

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
from src.modules.serve_proxy import routes as serve_proxy_routes

logger = logging.getLogger("ml-compute")


class RayClient:
    """Wrapper for Ray cluster via HTTP Dashboard API."""

    def __init__(self, dashboard_url: str | None = None):
        """Initialize Ray client.

        Args:
            dashboard_url: Ray Dashboard URL. Defaults to http://localhost:8265.
        """
        self.dashboard_url = dashboard_url or os.environ.get("RAY_DASHBOARD_URL", "http://localhost:8265")

    async def connect(self) -> None:
        """Verify Ray dashboard is accessible."""
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{self.dashboard_url}/api/v0/nodes", timeout=10.0)
                r.raise_for_status()
            logger.info(f"Connected to Ray dashboard at {self.dashboard_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Ray dashboard: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Ray (no-op for HTTP mode)."""
        logger.info("Disconnected from Ray (HTTP mode)")

    async def health_check(self) -> dict[str, Any]:
        """Check Ray cluster health via dashboard API.

        Returns:
            Cluster health status dict.
        """
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{self.dashboard_url}/api/v0/nodes", timeout=5.0)
                r.raise_for_status()
                data = r.json()

            nodes = data.get("data", {}).get("result", {}).get("result", [])
            resources = {}
            for node in nodes:
                resources.update(node.get("resources_total", {}))

            return {
                "status": "healthy" if nodes else "unhealthy",
                "resources": resources,
                "workers": len(nodes),
            }
        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return {"status": "unhealthy", "reason": str(e)}


# Global clients
ray_client = RayClient()
onyx = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI app lifecycle.

    Connects to Ray on startup, disconnects on shutdown.
    Initializes OnyxClient for status publishing (optional).
    """
    global onyx

    # Startup
    await ray_client.connect()

    # Initialize OnyxClient (optional - non-blocking)
    try:
        onyx = OnyxClient(skill_name="ml-compute")
        onyx.start()
        # Pass client to modules for status publishing
        from src.modules.jobs import routes as jobs_routes

        jobs_routes.set_onyx(onyx)
        logger.info("OnyxClient initialized")
    except Exception as e:
        logger.debug(f"OnyxClient initialization (optional): {e}")
        onyx = None

    yield

    # Shutdown
    if onyx:
        try:
            onyx.stop()
            logger.info("OnyxClient stopped")
        except Exception as e:
            logger.debug(f"OnyxClient shutdown (optional): {e}")

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
app.include_router(serve_proxy_routes.router, prefix="/api/serve", tags=["SAM"])
app.include_router(models_routes.router, prefix="/api/models", tags=["models"])


@app.get("/health", response_model=HealthResponse, tags=["status"])
async def health() -> HealthResponse:
    """Health check endpoint for cluster and workers.

    Returns:
        HealthResponse with cluster status.

    Raises:
        HTTPException: If cluster is unhealthy.
    """

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
    if onyx:
        try:
            onyx.publish_status("WORKING")
        except Exception as e:
            logger.debug(f"Failed to signal WORKING during readiness check: {e}")

    cluster_health = await ray_client.health_check()
    dependencies = {"ray_cluster": "ready" if cluster_health["status"] == "healthy" else "not_ready"}

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
async def root() -> dict[str, str]:
    """Root endpoint returning API info.

    Returns:
        API information dict.
    """
    # Signal active processing if available
    if onyx:
        try:
            onyx.publish_status("WORKING")
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
