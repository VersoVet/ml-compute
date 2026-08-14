"""Tests for ML models registry service."""

import os
from unittest.mock import patch

import pytest

from src.modules.models import service

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _make_pt_file(tmp_path: object, name: str, subdir: str = "yolo") -> object:
    """Create a fake .pt model file inside a subdirectory.

    Args:
        tmp_path: Pytest tmp_path fixture.
        name: Filename without extension.
        subdir: Parent directory name (used as model type).

    Returns:
        Path to the created file.
    """
    model_dir = tmp_path / subdir  # type: ignore[operator]
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / f"{name}.pt"
    model_file.write_bytes(b"\x00" * 2048)  # 2 KB dummy
    return model_file


# ---------------------------------------------------------------------------
# service.scan_models — finds .pt files
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_scan_models_finds_pt_files(tmp_path: object) -> None:
    """scan_models discovers .pt files and returns metadata."""
    _make_pt_file(tmp_path, "best", subdir="yolo")
    _make_pt_file(tmp_path, "classifier", subdir="efficientnet")

    with patch.object(service, "MODELS_DIR", tmp_path):
        result = await service.scan_models()

    assert result["total"] == 2
    assert len(result["models"]) == 2

    ids = {m["id"] for m in result["models"]}
    assert "best" in ids
    assert "classifier" in ids

    yolo_model = next(m for m in result["models"] if m["id"] == "best")
    assert yolo_model["type"] == "yolo"
    assert yolo_model["size_mb"] >= 0
    assert yolo_model["path"].endswith(".pt")
    assert yolo_model["created"] is not None
    assert yolo_model["source_job"] is None


# ---------------------------------------------------------------------------
# service.scan_models — empty when dir doesn't exist
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_scan_models_returns_empty_when_dir_missing(tmp_path: object) -> None:
    """scan_models returns empty list when models directory does not exist."""
    nonexistent = tmp_path / "does_not_exist"  # type: ignore[operator]

    with patch.object(service, "MODELS_DIR", nonexistent):
        result = await service.scan_models()

    assert result["models"] == []
    assert result["total"] == 0


# ---------------------------------------------------------------------------
# service.scan_models — handles file read errors gracefully
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_scan_models_handles_stat_error(tmp_path: object) -> None:
    """scan_models skips files that raise errors during stat()."""
    _make_pt_file(tmp_path, "good", subdir="yolo")
    _make_pt_file(tmp_path, "bad", subdir="yolo")

    def _stat_side_effect() -> None:
        raise PermissionError("access denied")

    with patch.object(service, "MODELS_DIR", tmp_path):
        # Patch Path.stat on the bad file by patching os.stat
        original_os_stat = os.stat

        def selective_stat(path: object, *args: object, **kwargs: object) -> object:
            if str(path).endswith("bad.pt"):
                raise PermissionError("access denied")
            return original_os_stat(path, *args, **kwargs)  # type: ignore[arg-type]

        with patch("os.stat", side_effect=selective_stat):
            result = await service.scan_models()

    # The bad file should be skipped, good file should remain
    assert result["total"] == 1
    assert result["models"][0]["id"] == "good"


# ---------------------------------------------------------------------------
# service.get_model_by_id — returns matching model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_model_by_id_returns_match(tmp_path: object) -> None:
    """get_model_by_id returns metadata for a known model ID."""
    _make_pt_file(tmp_path, "yolov8n", subdir="yolo")
    _make_pt_file(tmp_path, "resnet50", subdir="efficientnet")

    with patch.object(service, "MODELS_DIR", tmp_path):
        model = await service.get_model_by_id("yolov8n")

    assert model is not None
    assert model["id"] == "yolov8n"
    assert model["type"] == "yolo"


# ---------------------------------------------------------------------------
# service.get_model_by_id — returns None for unknown id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_model_by_id_returns_none_for_unknown(tmp_path: object) -> None:
    """get_model_by_id returns None when no model matches the given ID."""
    _make_pt_file(tmp_path, "existing_model", subdir="yolo")

    with patch.object(service, "MODELS_DIR", tmp_path):
        model = await service.get_model_by_id("nonexistent_model")

    assert model is None
