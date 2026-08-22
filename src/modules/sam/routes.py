"""HTTP routes for SAM management and inference."""

import logging
from fastapi import APIRouter, HTTPException
from .service import start_sam_serve, stop_sam_serve, get_sam_status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/serve", tags=["SAM Serve"])


@router.post("/start-sam")
async def start_sam(port: int = 9470) -> dict:
    """Start SAM Ray Serve deployment.

    Reserves num_gpus=1 on OnyxCortex (GPU becomes unavailable for training).

    Args:
        port: Ray Serve HTTP port (default: 9470)

    Returns:
        Status dict with endpoint URL and job ID
    """
    return await start_sam_serve(serve_port=port)


@router.post("/stop-sam")
async def stop_sam(job_id: str = None) -> dict:
    """Stop SAM deployment and free GPU.

    Once stopped, GPU becomes available for training jobs.

    Args:
        job_id: Ray job ID from start-sam response (optional)

    Returns:
        Confirmation dict
    """
    return await stop_sam_serve(job_id=job_id)


@router.get("/sam/status")
async def sam_status(port: int = 9470) -> dict:
    """Check SAM deployment status.

    Returns:
        Status: running | not_running | timeout
    """
    return await get_sam_status(serve_port=port)


@router.get("/sam/info")
async def sam_info() -> dict:
    """Get SAM deployment info and resource requirements.

    Returns:
        Info dict with model specs, GPU requirements, OnyxCortex config
    """
    return {
        "model": "sam_vit_b",
        "model_path": "~/sam-gpu/sam_vit_b_01ec64.pth",
        "model_size_gb": 0.375,
        "vram_required_gb": 10,
        "vram_available_onyxcortex_gb": 12,
        "scheduling": {
            "gpu_reserved": 1.0,
            "blocks_training_jobs": True,
            "recommended_hardware": "OnyxCortex (RTX 4070 SUPER)",
            "not_recommended": "OnyxPoint (T1000 8GB - insufficient VRAM)",
        },
        "inference_latency_ms": "500-1000",
        "use_strategy": """
1. Start SAM: POST /api/serve/start-sam
2. Annotate (via CVAT): POST http://10.0.0.44:9470/api/interact
3. Check status: GET /api/serve/sam/status
4. Stop SAM: POST /api/serve/stop-sam
5. Launch training: POST /api/jobs (GPU now free)
        """.strip(),
    }
