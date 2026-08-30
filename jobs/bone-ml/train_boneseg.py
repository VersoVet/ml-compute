"""Ray job: BoneSegNet training for per-bone segmentation.

Trains smp U-Net + MC-Dropout on validated zone annotations from PostgreSQL.
Invoked by bone-ml via POST /api/jobs with entrypoint python jobs/bone-ml/train_boneseg.py.

Requires NFS on the Ray worker:
- /mnt/ml-store (models output)
- /mnt/bonestore (source images)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("bone-ml-boneseg")


def get_env(key: str, default: str | None = None) -> str:
    """Get environment variable.

    Args:
        key: Variable name.
        default: Default value.

    Returns:
        Variable value.

    Raises:
        ValueError: If required and missing.
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Required env var '{key}' not set")
    return value


def _configure_bone_ml_env() -> None:
    """Map Ray job env vars to bone-ml configuration."""
    mapping = {
        "BONE_ANNOTATOR_PG_PASSWORD": get_env("PG_PASSWORD"),
        "BONE_ANNOTATOR_PG_HOST": get_env("PG_HOST", "10.0.0.59"),
        "BONE_ANNOTATOR_PG_PORT": get_env("PG_PORT", "5432"),
        "BONE_ANNOTATOR_PG_DB": get_env("PG_DB", "bone_recognition"),
        "BONE_ANNOTATOR_PG_USER": get_env("PG_USER", "bone"),
        "BONESTORE_PATH": os.environ.get("BONESTORE_PATH", "/mnt/bonestore"),
        "ML_STORE_PATH": os.environ.get("ML_STORE_PATH", "/mnt/ml-store"),
    }
    for env_key, value in mapping.items():
        os.environ[env_key] = value


def _parse_generation(run_name: str) -> int:
    """Extract generation number from run name.

    Args:
        run_name: Run name like humerus_boneseg_gen3.

    Returns:
        Generation number (default 1).
    """
    match = re.search(r"_gen(\d+)$", run_name)
    return int(match.group(1)) if match else 1


async def _load_annotations(bone_type: str, tiers: list[str]) -> tuple[list[Any], list[str]]:
    """Load train/val annotations and test acquisition IDs.

    Args:
        bone_type: Bone type filter.
        tiers: Quality tiers to include.

    Returns:
        Tuple of annotations (test set excluded) and test acquisition IDs.
    """
    from src.modules.boneseg.pg_loader import get_boneseg_annotations, get_test_set_ids

    test_ids = await get_test_set_ids(bone_type)
    annotations = await get_boneseg_annotations(
        bone_type,
        tiers=tiers,
        exclude_acquisition_ids=test_ids,
    )
    return annotations, test_ids


async def _load_test_annotations(
    bone_type: str,
    tiers: list[str],
    test_ids: list[str],
) -> list[Any]:
    """Load annotations restricted to frozen test acquisitions.

    Args:
        bone_type: Bone type filter.
        tiers: Quality tiers to include.
        test_ids: Test acquisition IDs.

    Returns:
        Test set annotations.
    """
    if not test_ids:
        return []

    from src.modules.boneseg.pg_loader import get_boneseg_annotations

    all_anns = await get_boneseg_annotations(bone_type, tiers=tiers)
    test_set = set(test_ids)
    return [ann for ann in all_anns if ann.acquisition_id in test_set]


async def _update_run(
    run_id: int,
    status: str,
    *,
    best_dice: float | None = None,
    per_class_dice: dict[str, float] | None = None,
    test_dice: float | None = None,
    model_output_path: str | None = None,
    epochs: int | None = None,
) -> None:
    """Update boneseg_training_runs row.

    Args:
        run_id: Database run ID.
        status: Run status.
        best_dice: Best validation Dice.
        per_class_dice: Per-class Dice scores.
        test_dice: Test set Dice.
        model_output_path: Saved checkpoint path.
        epochs: Epochs completed.
    """
    from src.modules.boneseg.training_registry import update_training_run

    await update_training_run(
        run_id,
        status,
        best_dice=best_dice,
        per_class_dice=per_class_dice,
        test_dice=test_dice,
        model_output_path=model_output_path,
        epochs=epochs,
    )


def _compute_dice(
    logits: Any,
    targets: Any,
    class_names: list[str],
) -> tuple[float, dict[str, float]]:
    """Compute mean and per-class Dice on a batch.

    Args:
        logits: Model logits (B, C, H, W).
        targets: Ground truth (B, H, W).
        class_names: Class names indexed by channel.

    Returns:
        Mean Dice (non-background) and per-class Dice dict.
    """
    import torch

    pred_cls = logits.argmax(dim=1)
    per_class: dict[str, float] = {}
    dice_sum = 0.0
    dice_count = 0

    for class_idx, name in enumerate(class_names):
        if class_idx == 0:
            continue
        inter = ((pred_cls == class_idx) & (targets == class_idx)).sum().float()
        union = (pred_cls == class_idx).sum().float() + (targets == class_idx).sum().float()
        if union > 0:
            dice = (2 * inter / (union + 1e-8)).item()
            per_class[name] = dice
            dice_sum += dice
            dice_count += 1

    mean_dice = dice_sum / max(dice_count, 1)
    return mean_dice, per_class


def _evaluate(
    model: Any,
    loader: Any,
    device: Any,
    class_names: list[str],
    use_amp: bool,
) -> tuple[float, dict[str, float]]:
    """Run validation and aggregate Dice metrics.

    Args:
        model: BoneSegNet model.
        loader: Validation DataLoader.
        device: Torch device.
        class_names: Segmentation class names.
        use_amp: Whether to use autocast.

    Returns:
        Mean validation Dice and per-class Dice.
    """
    import torch

    model.eval()
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}

    with torch.no_grad():
        for batch in loader:
            imgs = batch["image"].to(device)
            seg_t = batch["seg_mask"].to(device)
            with torch.amp.autocast("cuda", enabled=use_amp):
                logits = model(imgs)
            _, batch_per_class = _compute_dice(logits, seg_t, class_names)
            for name, dice in batch_per_class.items():
                totals[name] = totals.get(name, 0.0) + dice
                counts[name] = counts.get(name, 0) + 1

    per_class = {name: totals[name] / counts[name] for name in totals}
    mean_dice = sum(per_class.values()) / max(len(per_class), 1)
    return mean_dice, per_class


def main() -> None:
    """Train BoneSegNet on Ray worker."""
    logger.info("=== bone-ml BoneSeg training job ===")

    bone_type = get_env("BONE_TYPE", "humerus")
    epochs = int(get_env("EPOCHS", "100"))
    batch_size = int(get_env("BATCH_SIZE", "4"))
    img_size = int(get_env("IMG_SIZE", "1408"))
    lr = float(get_env("LEARNING_RATE", "0.001"))
    weight_decay = float(get_env("WEIGHT_DECAY", "0.0001"))
    base_model = os.environ.get("BASE_MODEL", "")
    run_id = int(get_env("RUN_ID"))
    run_name = get_env("RUN_NAME")
    tiers = [t.strip() for t in get_env("TIERS", "gold,silver").split(",") if t.strip()]
    ml_models_dir = get_env("ML_MODELS_DIR", "/mnt/ml-store/models")
    patience = int(os.environ.get("EARLY_STOPPING_PATIENCE", "15"))
    generation = _parse_generation(run_name)

    _configure_bone_ml_env()
    sys.path.insert(0, "/opt/onyx/skills/bone-ml")

    from src.modules.boneseg.config import (
        BONE_CLASS_MAP,
        BONE_CLASSES,
        EARLY_STOPPING_PATIENCE,
        ENCODER_NAME,
        TIER_WEIGHTS,
    )
    from src.modules.boneseg.dataset import BoneSegDataset
    from src.modules.boneseg.losses import TierWeightedSegLoss
    from src.modules.boneseg.model import BoneSegNet

    patience = patience or EARLY_STOPPING_PATIENCE
    n_classes = len(BONE_CLASSES)

    logger.info(
        "Config: bone=%s run=%s epochs=%d batch=%d img=%d tiers=%s",
        bone_type,
        run_name,
        epochs,
        batch_size,
        img_size,
        tiers,
    )

    Path(ml_models_dir).mkdir(parents=True, exist_ok=True)
    model_path = Path(ml_models_dir) / f"{run_name}_best.pt"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        annotations, test_ids = loop.run_until_complete(_load_annotations(bone_type, tiers))
        if not annotations:
            raise RuntimeError(f"No annotations for {bone_type} tiers={tiers}")

        random.seed(42)
        random.shuffle(annotations)
        val_count = max(1, len(annotations) // 5)
        train_anns = annotations[val_count:]
        val_anns = annotations[:val_count]

        logger.info(
            "Dataset: %d train, %d val, %d test acquisitions excluded",
            len(train_anns),
            len(val_anns),
            len(test_ids),
        )

        import torch
        from torch.utils.data import DataLoader

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        use_amp = device.type == "cuda"
        logger.info("Device: %s (amp=%s)", device, use_amp)

        model = BoneSegNet(
            n_classes=n_classes,
            encoder_name=ENCODER_NAME,
        ).to(device)

        if base_model:
            ckpt_path = Path(base_model)
            if not ckpt_path.is_absolute():
                ckpt_path = Path(ml_models_dir) / base_model
            if ckpt_path.exists():
                checkpoint = torch.load(str(ckpt_path), map_location=device, weights_only=False)
                state = (
                    checkpoint["model_state_dict"]
                    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint
                    else checkpoint
                )
                model.load_state_dict(state, strict=False)
                logger.info("Loaded base model: %s", ckpt_path)

        train_ds = BoneSegDataset(train_anns, BONE_CLASS_MAP, img_size, TIER_WEIGHTS)
        val_ds = BoneSegDataset(val_anns, BONE_CLASS_MAP, img_size, TIER_WEIGHTS)
        train_loader = DataLoader(
            train_ds,
            batch_size=batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=use_amp,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=use_amp,
        )

        criterion = TierWeightedSegLoss(tier_weights=TIER_WEIGHTS)
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=10, T_mult=2,
        )
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

        best_dice = 0.0
        best_per_class: dict[str, float] = {}
        epochs_run = 0
        stale_epochs = 0

        for epoch in range(epochs):
            epochs_run = epoch + 1
            model.train()
            epoch_loss = 0.0
            n_batches = 0

            for batch in train_loader:
                imgs = batch["image"].to(device, non_blocking=True)
                seg_t = batch["seg_mask"].to(device, non_blocking=True)
                tiers_batch = batch["tier"]

                optimizer.zero_grad(set_to_none=True)
                with torch.amp.autocast("cuda", enabled=use_amp):
                    logits = model(imgs)
                    losses = criterion(logits, seg_t, tiers=tiers_batch)

                scaler.scale(losses["total"]).backward()
                scaler.step(optimizer)
                scaler.update()
                epoch_loss += losses["total"].item()
                n_batches += 1

            scheduler.step()
            val_dice, per_class = _evaluate(
                model, val_loader, device, BONE_CLASSES, use_amp,
            )

            if (epoch + 1) % 5 == 0 or epoch == 0:
                logger.info(
                    "Epoch %d/%d loss=%.4f val_dice=%.4f",
                    epoch + 1,
                    epochs,
                    epoch_loss / max(n_batches, 1),
                    val_dice,
                )

            if val_dice > best_dice:
                best_dice = val_dice
                best_per_class = per_class
                stale_epochs = 0
                torch.save(
                    {
                        "model_state_dict": model.state_dict(),
                        "n_classes": n_classes,
                        "encoder_name": ENCODER_NAME,
                        "bone_classes": BONE_CLASS_MAP,
                        "generation": generation,
                        "best_dice": best_dice,
                        "per_class_dice": best_per_class,
                    },
                    model_path,
                )
                logger.info("Saved best checkpoint dice=%.4f → %s", best_dice, model_path)
            else:
                stale_epochs += 1
                if stale_epochs >= patience:
                    logger.info("Early stopping after %d epochs without improvement", patience)
                    break

        test_dice: float | None = None
        test_anns = loop.run_until_complete(_load_test_annotations(bone_type, tiers, test_ids))
        if test_anns and model_path.exists():
            test_ds = BoneSegDataset(test_anns, BONE_CLASS_MAP, img_size, TIER_WEIGHTS)
            test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=2)
            checkpoint = torch.load(str(model_path), map_location=device, weights_only=False)
            model.load_state_dict(checkpoint["model_state_dict"])
            test_dice, _ = _evaluate(model, test_loader, device, BONE_CLASSES, use_amp)
            logger.info("Test Dice: %.4f (%d frames)", test_dice, len(test_anns))

        loop.run_until_complete(
            _update_run(
                run_id,
                "completed",
                best_dice=best_dice,
                per_class_dice=best_per_class,
                test_dice=test_dice,
                model_output_path=str(model_path),
                epochs=epochs_run,
            )
        )

        result = {
            "run_id": run_id,
            "run_name": run_name,
            "best_dice": best_dice,
            "per_class_dice": best_per_class,
            "test_dice": test_dice,
            "epochs_run": epochs_run,
            "model_path": str(model_path),
        }
        logger.info("Training complete: %s", json.dumps(result))
        print(json.dumps(result))

    except Exception:
        logger.exception("BoneSeg training failed")
        try:
            loop.run_until_complete(_update_run(run_id, "failed"))
        except Exception as update_err:
            logger.error("Failed to update run status: %s", update_err)
        sys.exit(1)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
