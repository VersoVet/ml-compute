"""FastAPI routes for ML models registry."""

from fastapi import APIRouter

from src.models import ModelsResponse
from src.modules.models import service

router = APIRouter()


@router.get("", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """List all available ML models in the registry.

    Returns:
        ModelsResponse with models and total count.
    """
    result = await service.scan_models()

    return ModelsResponse(
        models=[
            {
                "id": m["id"],
                "type": m["type"],
                "size_mb": m["size_mb"],
                "path": m["path"],
                "created": m["created"],
                "source_job": m.get("source_job"),
            }
            for m in result["models"]
        ],
        total=result["total"],
    )
