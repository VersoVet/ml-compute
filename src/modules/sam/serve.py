"""Nomad-based manager for SAM (Segment Anything Model) deployment.

Manages SAM deployment on Nomad with exclusive GPU allocation.
SAM reserves num_gpus=1 and is scheduled on available GPU workers automatically.
"""

import json
import logging
import os
from typing import Any

import httpx

from src.config import CONFIG

logger = logging.getLogger(__name__)

# Configuration from YAML
_nomad_cfg = CONFIG.get("nomad", {})
_sam_cfg = CONFIG.get("sam", {})
NOMAD_URL = os.environ.get("NOMAD_URL", _nomad_cfg.get("url", "http://10.0.0.44:4646"))
SAM_JOB_NAME = _sam_cfg.get("job_name", "sam-inference")
SAM_ENDPOINT_PORT = _sam_cfg.get("endpoint_port", 9470)
SAM_HOST = _sam_cfg.get("host", "10.0.0.26")
SAM_JOB_SPEC_PATH = _sam_cfg.get("job_spec_path", "/opt/onyx/skills/ml-compute/jobs/sam/sam_job_spec.json")
HTTP_TIMEOUT = _nomad_cfg.get("timeout", 30.0)


class SAMServeManager:
    """Manager for Nomad SAM deployment with exclusive GPU allocation."""

    def __init__(self, nomad_url: str = NOMAD_URL) -> None:
        """Initialize SAM Serve manager.

        Args:
            nomad_url: Nomad API URL.
        """
        self.nomad_url = nomad_url
        self.job_name = SAM_JOB_NAME
        self.deployment_name = SAM_JOB_NAME
        self.is_deployed = False
        self.allocation_id: str | None = None
        self.endpoint = f"http://{SAM_HOST}:{SAM_ENDPOINT_PORT}"

    async def deploy(self) -> bool:
        """Deploy SAM on Nomad with exclusive GPU allocation.

        Returns:
            True if job submitted successfully, False otherwise.
        """
        try:
            logger.info("Deploying SAM via Nomad...")

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{self.nomad_url}/v1/job/{self.job_name}",
                        timeout=HTTP_TIMEOUT,
                    )
                    if response.status_code == 200:
                        logger.info("SAM job already exists in Nomad")
                        self.is_deployed = True
                        return True
                except Exception:
                    pass

                if not os.path.exists(SAM_JOB_SPEC_PATH):
                    logger.error(f"SAM job spec not found: {SAM_JOB_SPEC_PATH}")
                    return False

                with open(SAM_JOB_SPEC_PATH) as f:
                    job_spec = json.load(f)

                response = await client.post(
                    f"{self.nomad_url}/v1/jobs",
                    json={"Job": job_spec},
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

                self.is_deployed = True
                logger.info(f"SAM job submitted to Nomad (evaluation_id: {result.get('EvalID', 'unknown')})")
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
                response = await client.delete(
                    f"{self.nomad_url}/v1/job/{self.job_name}?purge=true",
                    timeout=HTTP_TIMEOUT,
                )
                response.raise_for_status()

            self.is_deployed = False
            self.allocation_id = None
            logger.info("SAM Nomad job stopped and resources freed")
            return True

        except Exception as e:
            logger.error(f"Failed to undeploy SAM: {e}", exc_info=True)
            return False

    async def get_status(self) -> dict[str, Any]:
        """Get SAM container status by checking health on the host.

        Returns:
            Status dict with health and endpoint.
        """
        try:
            sam_health = None
            is_healthy = False

            async with httpx.AsyncClient() as client:
                try:
                    health_response = await client.get(
                        f"{self.endpoint}/health",
                        timeout=5.0,
                    )
                    if health_response.status_code == 200:
                        sam_health = health_response.json().get("status", "unknown")
                        is_healthy = sam_health in ("ok", "ready")
                except Exception:
                    sam_health = "unreachable"

            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "endpoint": self.endpoint,
                "sam_health": sam_health,
                "is_deployed": is_healthy,
            }

        except Exception as e:
            logger.debug(f"Failed to get status: {e}")
            return {
                "status": "error",
                "endpoint": self.endpoint,
                "error": str(e),
                "is_deployed": False,
            }

    async def interact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Forward segmentation request to SAM server.

        Args:
            payload: Segmentation request dict.

        Returns:
            Segmentation result from SAM.
        """
        try:
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
