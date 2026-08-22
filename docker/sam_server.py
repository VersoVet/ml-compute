#!/usr/bin/env python3
"""SAM FastAPI service for interactive segmentation.

Runs as a Docker service with GPU support.
"""

import asyncio
import logging
import os
import sys
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Lazy import SAM to avoid libGL issues at startup
SAMDeployment = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class InteractRequest(BaseModel):
    """Request model for SAM interaction."""

    image: str | None = None
    positive_points: list[list[int]] = []
    negative_points: list[list[int]] = []


# Create FastAPI app
app = FastAPI(
    title="SAM Service",
    description="Segment Anything Model (vit_b) interactive segmentation",
    version="1.0.0",
)

# Initialize SAM deployment once
sam_deployment: SAMDeployment | None = None


@app.on_event("startup")
async def startup():
    """Initialize SAM on startup."""
    global sam_deployment
    try:
        logger.info("Initializing SAM deployment...")
        # Lazy import SAM module to avoid libGL issues
        sys.path.insert(0, "/app")
        from deployment import SAMDeployment as SAMDepl
        sam_deployment = SAMDepl()
        logger.info("✓ SAM initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SAM: {e}", exc_info=True)
        raise


@app.post("/api/interact")
async def interact(request: InteractRequest) -> dict[str, Any]:
    """Interactive segmentation endpoint.

    Args:
        request: Image and point prompts.

    Returns:
        Segmentation mask and metadata.
    """
    if not sam_deployment:
        return {"status": "error", "message": "SAM not initialized"}

    return await sam_deployment.interact(request.dict())


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "sam-vit-b"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    """Readiness check endpoint."""
    if not sam_deployment:
        return {"status": "not_ready"}
    return {"status": "ready"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "SAM (Segment Anything Model)",
        "model": "vit_b",
        "endpoint": "/api/interact",
        "docs": "/docs",
    }


if __name__ == "__main__":
    port = int(os.environ.get("SAM_PORT", 9470))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
