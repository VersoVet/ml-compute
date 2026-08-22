"""Ray Serve manager for SAM (Segment Anything Model) deployment.

Manages SAM deployment on Ray Serve via Ray Dashboard APIs.
SAM reserves num_gpus=1 and is scheduled on available GPU workers automatically.
"""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Ray configuration
RAY_DASHBOARD_URL = os.environ.get("RAY_DASHBOARD_URL", "http://localhost:8265")
RAY_SERVE_URL = "http://localhost:8000"
SAM_DEPLOYMENT_NAME = "sam-vit-b"
HTTP_TIMEOUT = 30.0


class SAMServeManager:
    """Manager for Ray Serve SAM deployment via Dashboard APIs."""

    def __init__(self, dashboard_url: str = RAY_DASHBOARD_URL):
        """Initialize SAM Serve manager.

        Args:
            dashboard_url: Ray Dashboard URL (default: localhost:8265)
        """
        self.dashboard_url = dashboard_url
        self.serve_url = RAY_SERVE_URL
        self.deployment_name = SAM_DEPLOYMENT_NAME
        self.endpoint = f"{self.serve_url}/{self.deployment_name}"
        self.is_deployed = False

    async def deploy(self) -> bool:
        """Deploy SAM as Ray Serve deployment with GPU reservation.

        Uses Python driver API to deploy SAMDeployment with num_gpus=1.
        Ray automatically schedules on available GPU workers (OnyxCortex, OnyxPoint, etc).

        Returns:
            True if deployment succeeded, False otherwise.
        """
        try:
            logger.info("Deploying SAM via Ray Serve (num_gpus=1)...")

            # Import Ray Serve and deploy locally
            from ray import serve

            from .deployment import SAMDeployment

            # Deploy SAM with GPU reservation
            serve.run(
                SAMDeployment.bind(),
                name=self.deployment_name,
                route_prefix=f"/{self.deployment_name}",
            )

            self.is_deployed = True
            logger.info(f"✓ SAM deployed at {self.endpoint} with num_gpus=1")
            return True

        except Exception as e:
            logger.error(f"Failed to deploy SAM: {e}", exc_info=True)
            return False

    async def undeploy(self) -> bool:
        """Stop SAM Ray Serve deployment and free GPU.

        Returns:
            True if undeployment succeeded, False otherwise.
        """
        try:
            logger.info("Undeploying SAM from Ray Serve...")

            from ray import serve

            serve.shutdown()

            self.is_deployed = False
            logger.info("✓ SAM undeployed, GPU freed")
            return True
        except Exception as e:
            logger.error(f"Failed to undeploy SAM: {e}", exc_info=True)
            return False

    async def get_status(self) -> dict[str, Any]:
        """Get SAM deployment status from Ray Dashboard.

        Returns:
            Status dict with deployment info.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.dashboard_url}/api/serve/applications/",
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()

            applications = data.get("applications", {})

            # Look for SAM deployment in any application
            for app_name, app_info in applications.items():
                deployments = app_info.get("deployments", {})
                if self.deployment_name in deployments:
                    deploy_info = deployments[self.deployment_name]
                    return {
                        "status": deploy_info.get("status", "unknown"),
                        "deployment": self.deployment_name,
                        "endpoint": self.endpoint,
                        "num_replicas": len(
                            deploy_info.get("replica_states", {}).get("RUNNING", [])
                        ),
                        "is_deployed": True,
                    }

            return {
                "status": "not_deployed",
                "deployment": self.deployment_name,
                "endpoint": self.endpoint,
                "num_replicas": 0,
                "is_deployed": False,
            }
        except Exception as e:
            logger.debug(f"Failed to get status: {e}")
            return {
                "status": "error",
                "deployment": self.deployment_name,
                "endpoint": self.endpoint,
                "error": str(e),
                "is_deployed": False,
            }

    async def interact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Forward segmentation request to Ray Serve SAM deployment.

        Args:
            payload: Segmentation request dict.

        Returns:
            Segmentation result from SAM.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"SAM inference failed: {e}")
            return {"status": "error", "message": str(e)}

    async def info(self) -> dict[str, Any]:
        """Get SAM service information.

        Returns:
            Service metadata.
        """
        return {
            "service": "SAM (Segment Anything Model)",
            "model": "vit_b",
            "backend": "Ray Serve",
            "deployment": self.deployment_name,
            "endpoint": self.endpoint,
            "gpu_reserved": 1.0,
            "auto_scheduled": True,
            "vram_required_gb": 10,
            "inference_latency_ms": "500-1000",
            "note": "Ray allocates GPU automatically to available workers (OnyxCortex, OnyxPoint, etc)",
        }


# Global SAM Serve manager instance
sam_manager: SAMServeManager | None = None


def get_sam_manager() -> SAMServeManager:
    """Get or create global SAM Serve manager.

    Returns:
        SAMServeManager instance.
    """
    global sam_manager
    if sam_manager is None:
        sam_manager = SAMServeManager()
    return sam_manager
