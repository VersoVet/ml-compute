"""ML models registry service layer."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MODELS_DIR = Path("/opt/onyx/skills/ml-compute/models")


async def scan_models() -> dict[str, Any]:
    """Scan filesystem for available ML models.

    Returns:
        Dict with models list and total count.
    """
    models = []

    try:
        if not MODELS_DIR.exists():
            logger.warning(f"Models directory not found: {MODELS_DIR}")
            return {"models": [], "total": 0}

        for model_path in MODELS_DIR.rglob("*.pt"):
            try:
                stat = model_path.stat()
                size_mb = stat.st_size / (1024 * 1024)
                created = datetime.fromtimestamp(stat.st_ctime)

                model_type = model_path.parent.name

                models.append(
                    {
                        "id": model_path.stem,
                        "type": model_type,
                        "size_mb": round(size_mb, 2),
                        "path": str(model_path),
                        "created": created.isoformat(),
                        "source_job": None,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to read model {model_path}: {e}")

        logger.info(f"Found {len(models)} models")

        return {"models": models, "total": len(models)}
    except Exception as e:
        logger.error(f"Failed to scan models: {e}")
        return {"models": [], "total": 0}


async def get_model_by_id(model_id: str) -> dict[str, Any] | None:
    """Get specific model metadata by ID.

    Args:
        model_id: Model identifier.

    Returns:
        Model info dict or None if not found.
    """
    result = await scan_models()

    for model in result["models"]:
        if model["id"] == model_id:
            return model

    return None
