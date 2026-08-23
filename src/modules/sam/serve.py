"""Nomad-based manager for SAM (Segment Anything Model) deployment.

Manages SAM deployment on Nomad with exclusive GPU allocation.
SAM reserves num_gpus=1 and is scheduled on available GPU workers automatically.
"""

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Nomad configuration
NOMAD_URL = os.environ.get("NOMAD_URL", "http://10.0.0.44:4646")
SAM_JOB_NAME = "sam-inference"
SAM_ENDPOINT_PORT = 9470
HTTP_TIMEOUT = 30.0


class SAMServeManager:
    """Manager for Nomad SAM deployment with exclusive GPU allocation."""

    def __init__(self, nomad_url: str = NOMAD_URL):
        """Initialize SAM Serve manager.

        Args:
            nomad_url: Nomad API URL (default: http://10.0.0.44:4646)
        """
        self.nomad_url = nomad_url
        self.job_name = SAM_JOB_NAME
        self.is_deployed = False
        self.allocation_id: str | None = None

    async def deploy(self) -> bool:
        """Deploy SAM on Nomad with exclusive GPU allocation.

        Submits the sam-inference job to Nomad cluster.
        GPU allocation is managed exclusively by Nomad.

        Returns:
            True if job submitted successfully, False otherwise.
        """
        try:
            logger.info("Deploying SAM via Nomad...")

            # Check if job already exists
            async with httpx.AsyncClient() as client:
                # First, check if job is already running
                try:
                    response = await client.get(
                        f"{self.nomad_url}/v1/job/{self.job_name}",
                        timeout=HTTP_TIMEOUT,
                    )
                    if response.status_code == 200:
                        logger.info("✓ SAM job already exists in Nomad")
                        self.is_deployed = True
                        return True
                except Exception:
                    pass

                # Job doesn't exist or error occurred, submit new job
                # Load job spec from file
                job_spec_path = "/opt/onyx/skills/ml-compute/jobs/sam/sam_job_spec.json"
                if not os.path.exists(job_spec_path):
                    logger.error(f"SAM job spec not found: {job_spec_path}")
                    return False

                with open(job_spec_path) as f:
                    job_spec = json.load(f)

                # Submit job to Nomad
                response = await client.post(
                    f"{self.nomad_url}/v1/jobs",
                    json={"Job": job_spec},
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

                self.is_deployed = True
                logger.info(f"✓ SAM job submitted to Nomad (evaluation_id: {result.get('EvalID', 'unknown')})")
                return True

        except Exception as e:
            logger.error(f"Failed to deploy SAM on Nomad: {e}", exc_info=True)
            return False

    async def undeploy(self) -> bool:
        """Stop SAM Nomad job and free GPU allocation.

        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info("Stopping SAM Nomad job...")

            async with httpx.AsyncClient() as client:
                # Delete job from Nomad (purge=true removes it completely)
                response = await client.delete(
                    f"{self.nomad_url}/v1/job/{self.job_name}?purge=true",
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()

            self.is_deployed = False
            self.allocation_id = None
            logger.info("✓ SAM Nomad job stopped and resources freed")
            return True

        except Exception as e:
            logger.error(f"Failed to undeploy SAM: {e}", exc_info=True)
            return False

    async def get_status(self) -> dict[str, Any]:
        """Get SAM Nomad job status.

        Checks job state in Nomad and verifies SAM server health.

        Returns:
            Status dict with job info, allocations, and health.
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get job status from Nomad
                response = await client.get(
                    f"{self.nomad_url}/v1/job/{self.job_name}",
                    timeout=HTTP_TIMEOUT,
                )

                if response.status_code == 404:
                    # Job doesn't exist
                    return {
                        "status": "not_deployed",
                        "job_name": self.job_name,
                        "job_status": "unknown",
                        "is_deployed": False,
                    }

                response.raise_for_status()
                job_data = response.json()
                job_status = job_data.get("Status", "unknown")

                # Get allocations
                alloc_response = await client.get(
                    f"{self.nomad_url}/v1/job/{self.job_name}/allocations",
                    timeout=HTTP_TIMEOUT,
                )
                allocations = alloc_response.json() if alloc_response.status_code == 200 else []

                # Find a running allocation
                running_alloc = None
                for alloc in allocations:
                    if alloc.get("ClientStatus") == "running":
                        running_alloc = alloc
                        self.allocation_id = alloc.get("ID")
                        break

                # Determine health and endpoint
                sam_endpoint = None
                sam_health = None
                is_healthy = False

                if running_alloc:
                    # Try to get health from running SAM server
                    node_id = running_alloc.get("NodeID")
                    node_response = await client.get(
                        f"{self.nomad_url}/v1/node/{node_id}",
                        timeout=HTTP_TIMEOUT,
                    )
                    if node_response.status_code == 200:
                        node_data = node_response.json()
                        node_ip = node_data.get("HTTPAddr", "").split(":")[0]
                        sam_endpoint = f"http://{node_ip}:{SAM_ENDPOINT_PORT}"

                        # Check SAM server health
                        try:
                            health_response = await client.get(
                                f"{sam_endpoint}/health",
                                timeout=5.0,
                            )
                            if health_response.status_code == 200:
                                sam_health = health_response.json().get("status", "unknown")
                                is_healthy = sam_health in ("ok", "ready")
                        except Exception:
                            sam_health = "unreachable"

                return {
                    "status": "deployed" if is_healthy else "pending" if job_status == "pending" else "unhealthy",
                    "job_name": self.job_name,
                    "job_status": job_status,
                    "allocation_count": len(allocations),
                    "running_allocation": running_alloc.get("ID") if running_alloc else None,
                    "endpoint": sam_endpoint,
                    "sam_health": sam_health,
                    "is_deployed": is_healthy,
                    "gpu_allocated": running_alloc.get("Resources", {}).get("Devices", []) if running_alloc else [],
                }

        except Exception as e:
            logger.debug(f"Failed to get status: {e}")
            return {
                "status": "error",
                "job_name": self.job_name,
                "error": str(e),
                "is_deployed": False,
            }

    async def interact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Forward segmentation request to Nomad-deployed SAM server.

        Args:
            payload: Segmentation request dict.

        Returns:
            Segmentation result from SAM.
        """
        try:
            # Get current SAM status to find endpoint
            status = await self.get_status()
            sam_endpoint = status.get("endpoint")

            if not sam_endpoint or not status.get("is_deployed"):
                logger.error("SAM is not deployed or endpoint not found")
                return {
                    "status": "error",
                    "message": "SAM service not available. Please deploy first.",
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{sam_endpoint}/segment",
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
            "backend": "Nomad",
            "job_name": self.job_name,
            "gpu_reserved": 1.0,
            "auto_scheduled": True,
            "vram_required_gb": 10,
            "inference_latency_ms": "500-1000",
            "note": "Nomad manages exclusive GPU allocation (OnyxCortex or OnyxPoint)",
            "nomad_url": self.nomad_url,
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
