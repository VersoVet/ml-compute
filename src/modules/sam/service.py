"""SAM Serve lifecycle management service.

Handles starting/stopping SAM Ray Serve deployment to ensure:
1. SAM has exclusive GPU access during annotations (num_gpus=1)
2. GPU is freed after annotations for training jobs
3. No resource contention on OnyxCortex
"""

import logging
import subprocess
import time
from typing import Any

logger = logging.getLogger(__name__)


async def start_sam_serve(
    serve_port: int = 9470,
    ray_address: str = "http://10.0.0.44:8265",
) -> dict[str, Any]:
    """Start SAM Ray Serve deployment.

    Args:
        serve_port: HTTP port for Ray Serve (default: 9470)
        ray_address: Ray dashboard address

    Returns:
        Dict with status, endpoint, message
    """
    try:
        logger.info(f"Starting SAM deployment on port {serve_port}")

        # Check if already running
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"http://10.0.0.44:{serve_port}/api/interact")
                if r.status_code == 200:
                    return {
                        "status": "already_running",
                        "endpoint": f"http://10.0.0.44:{serve_port}/api/interact",
                        "message": "SAM already deployed and ready",
                    }
            except Exception:
                pass  # Not running yet

        # Launch deployment as Ray Job (runs in background)
        from ray.job_submission import JobSubmissionClient

        client = JobSubmissionClient(address=ray_address)

        job_id = client.submit_job(
            entrypoint=f"python /opt/onyx/skills/ml-compute/jobs/sam/deploy_serve.py --ray-address {ray_address} --serve-port {serve_port}",
            runtime_env={
                "pip": [
                    "segment-anything",
                    "opencv-python",
                    "Pillow",
                    "torch",
                    "torchvision",
                ],
                "working_dir": "/opt/onyx/skills/ml-compute",
            },
        )

        logger.info(f"SAM deployment job submitted: {job_id}")

        # Wait for service to start (with timeout)
        max_retries = 30
        for attempt in range(max_retries):
            await asyncio.sleep(1)
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    r = await client.get(f"http://10.0.0.44:{serve_port}/api/interact")
                    if r.status_code == 200:
                        logger.info(f"✓ SAM ready on port {serve_port}")
                        return {
                            "status": "deployed",
                            "endpoint": f"http://10.0.0.44:{serve_port}/api/interact",
                            "job_id": job_id,
                            "message": "SAM deployed successfully, GPU reserved (num_gpus=1)",
                        }
            except Exception:
                pass

        logger.warning(f"SAM deployment timeout after {max_retries}s")
        return {
            "status": "deploying",
            "job_id": job_id,
            "endpoint": f"http://10.0.0.44:{serve_port}/api/interact (starting...)",
            "message": f"SAM deployment in progress (job {job_id}), check /api/jobs/{job_id}",
        }

    except Exception as e:
        logger.error(f"Failed to start SAM: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def stop_sam_serve(job_id: str = None) -> dict[str, Any]:
    """Stop SAM Ray Serve deployment and free GPU.

    Args:
        job_id: Ray job ID of SAM deployment (if known)

    Returns:
        Dict with status, message
    """
    try:
        logger.info("Stopping SAM deployment")

        if job_id:
            from ray.job_submission import JobSubmissionClient

            client = JobSubmissionClient(address="http://10.0.0.44:8265")
            client.stop_job(job_id)
            logger.info(f"Stopped job {job_id}")

        # Try to stop via Ray Serve API
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post("http://10.0.0.44:8265/api/serve/applications/sam-vit-b/stop")
        except Exception:
            pass

        logger.info("✓ SAM deployment stopped, GPU freed for training jobs")
        return {
            "status": "stopped",
            "message": "SAM deployment stopped, GPU is now available for training",
        }

    except Exception as e:
        logger.error(f"Failed to stop SAM: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def get_sam_status(serve_port: int = 9470) -> dict[str, Any]:
    """Check if SAM is running and responsive.

    Returns:
        Dict with status, latency_ms
    """
    import asyncio
    import time

    try:
        import httpx

        async with httpx.AsyncClient(timeout=2.0) as client:
            start = time.time()
            r = await client.get(f"http://10.0.0.44:{serve_port}/api/interact")
            latency_ms = int((time.time() - start) * 1000)

            if r.status_code == 200:
                return {
                    "status": "running",
                    "latency_ms": latency_ms,
                    "endpoint": f"http://10.0.0.44:{serve_port}/api/interact",
                }
            else:
                return {"status": "error", "http_status": r.status_code}

    except asyncio.TimeoutError:
        return {"status": "timeout", "message": "SAM not responding"}
    except Exception as e:
        return {"status": "not_running", "message": str(e)}
