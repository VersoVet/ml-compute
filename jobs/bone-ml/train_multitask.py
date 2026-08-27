"""Ray job: MultiHeadAnatomyNet training for bone multitask analysis.

Trains segmentation (zones) + landmarks (heatmaps) + criteria (binary/ordinal/continuous).
All config comes from environment variables set by bone-ml train_service.py.

This script runs inside a Ray worker container with NFS access to:
- /mnt/ml-store/models (output)
- /mnt/ml-store/runs (logs)
- /mnt/bonestore (images)
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("bone-ml-multitask")


def get_env(key: str, default: str | None = None) -> str:
    """Get required environment variable.

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


async def fetch_labels(url: str, bone_type: str) -> dict:
    """Fetch multitask taxonomy from label-generator.

    Args:
        url: Label generator base URL.
        bone_type: Bone type to fetch.

    Returns:
        Dict with zone_map, landmark_names, criteria.
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        # YOLO zone map
        r = await client.get(f"{url}/labels/api/export/yolo", params={"bone_type": bone_type})
        r.raise_for_status()
        yolo = r.json()
        class_map = yolo.get("class_map", {})
        zone_map = {k: v + 1 for k, v in class_map.items()}  # +1 for background=0

        # Label summary for landmarks
        r = await client.get(f"{url}/labels/api/summary", params={"bone_type": bone_type})
        r.raise_for_status()
        summary = r.json()
        lm_names = summary.get("bones", {}).get(bone_type, {}).get("landmark_names", [])

        # If summary doesn't have landmark_names, fetch from multitask export
        if not lm_names:
            r = await client.get(f"{url}/labels/api/export/multitask", params={"bone_type": bone_type})
            r.raise_for_status()
            mt = r.json()
            if bone_type in mt:
                struct = mt[bone_type].get("structures", {}).get(bone_type, {})
                lm_names = [lm["label"] for lm in struct.get("landmarks", [])]
                for z in struct.get("zones", []):
                    lm_names.extend(lm["label"] for lm in z.get("landmarks", []))

    logger.info("Labels: %d zones, %d landmarks", len(zone_map), len(lm_names))
    return {"zone_map": zone_map, "landmark_names": lm_names}


async def fetch_annotations(
    host: str, port: int, db: str, user: str, password: str,
    bone_type: str, source_filter: str,
) -> list[dict]:
    """Fetch validated annotations from PostgreSQL.

    Args:
        host: PG host.
        port: PG port.
        db: Database name.
        user: PG user.
        password: PG password.
        bone_type: Filter by bone type.
        source_filter: Comma-separated source names.

    Returns:
        List of annotation record dicts.
    """
    import asyncpg

    conn = await asyncpg.connect(
        host=host, port=port, database=db, user=user, password=password,
        server_settings={"search_path": "bone_annotations,public"},
        ssl=False,
    )
    sources = [s.strip() for s in source_filter.split(",")]
    rows = await conn.fetch(
        """SELECT fa.acquisition_id, fa.frame_filename, fa.annotation_type,
                  fa.label, fa.data
           FROM frame_annotations fa
           JOIN annotation_tasks t ON fa.acquisition_id = t.acquisition_id
           WHERE t.status = 'validated' AND t.bone_type = $1
           AND fa.source = ANY($2)
           ORDER BY fa.acquisition_id, fa.frame_filename""",
        bone_type, sources,
    )
    await conn.close()
    logger.info("Fetched %d annotation rows for %s", len(rows), bone_type)
    return [dict(r) for r in rows]


def group_annotations(rows: list[dict]) -> list[dict]:
    """Group flat annotation rows into per-frame groups.

    Args:
        rows: Flat annotation records.

    Returns:
        List of dicts with acquisition_id, frame_filename, zones, landmarks.
    """
    groups: dict[str, dict] = {}
    for row in rows:
        key = f"{row['acquisition_id']}:{row['frame_filename']}"
        if key not in groups:
            groups[key] = {
                "acquisition_id": row["acquisition_id"],
                "frame_filename": row["frame_filename"],
                "dataset_path": "",
                "zones": [],
                "landmarks": [],
            }
        ann_type = row["annotation_type"]
        data = row["data"] if isinstance(row["data"], dict) else json.loads(row["data"])
        entry = {"label": row["label"], "data": data}
        if ann_type == "zone":
            groups[key]["zones"].append(entry)
        elif ann_type == "landmark":
            groups[key]["landmarks"].append(entry)
    return list(groups.values())


def main() -> None:
    """Train MultiHeadAnatomyNet on Ray worker."""
    logger.info("=== bone-ml MultiHead training job ===")

    # Config from env
    bone_type = get_env("BONE_TYPE", "humerus")
    epochs = int(get_env("EPOCHS", "100"))
    batch_size = int(get_env("BATCH_SIZE", "4"))
    img_size = int(get_env("IMG_SIZE", "512"))
    lr = float(get_env("LEARNING_RATE", "0.0001"))
    encoder_name = get_env("ENCODER_NAME", "resnet50")
    generation = int(get_env("GENERATION", "1"))
    parent_model = os.environ.get("PARENT_MODEL", "")
    ml_models_dir = get_env("ML_MODELS_DIR", "/mnt/ml-store/models")
    label_url = get_env("LABEL_GENERATOR_URL", "http://10.0.0.59:9466")
    pg_host = get_env("PG_HOST", "10.0.0.59")
    pg_port = int(get_env("PG_PORT", "5432"))
    pg_db = get_env("PG_DB", "bone_recognition")
    pg_user = get_env("PG_USER", "bone")
    pg_password = get_env("PG_PASSWORD")
    source_filter = get_env("SOURCE_FILTER", "manual,corrected_ml")

    logger.info("Config: bone=%s epochs=%d batch=%d encoder=%s gen=%d",
                bone_type, epochs, batch_size, encoder_name, generation)

    Path(ml_models_dir).mkdir(parents=True, exist_ok=True)

    # Fetch data
    loop = asyncio.new_event_loop()
    labels = loop.run_until_complete(fetch_labels(label_url, bone_type))
    raw_anns = loop.run_until_complete(fetch_annotations(
        pg_host, pg_port, pg_db, pg_user, pg_password, bone_type, source_filter,
    ))
    loop.close()

    zone_map = labels["zone_map"]
    lm_names = labels["landmark_names"]
    groups = group_annotations(raw_anns)

    if not groups:
        logger.error("No annotations found — aborting")
        sys.exit(1)

    n_seg = len(zone_map) + 1  # +1 for background
    logger.info("Dataset: %d frames, %d seg classes, %d landmarks", len(groups), n_seg, len(lm_names))

    # Training
    import torch
    from torch.utils.data import DataLoader

    import segmentation_models_pytorch as smp  # noqa: F401 — ensures smp available

    # Import bone-ml from skill path
    sys.path.insert(0, "/opt/onyx/skills/bone-ml")
    from src.modules.multitask.model import MultiHeadAnatomyNet
    from src.modules.multitask.losses import MultiTaskLoss
    from src.modules.multitask.dataset import MultitaskDataset

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s", device)

    model = MultiHeadAnatomyNet(
        n_seg_classes=n_seg,
        n_landmarks=len(lm_names),
        encoder_name=encoder_name,
        encoder_weights="imagenet",
    ).to(device)

    # Load parent model for fine-tuning
    if parent_model:
        parent_path = Path(ml_models_dir) / parent_model
        if parent_path.exists():
            model.load_state_dict(torch.load(str(parent_path), map_location=device), strict=False)
            logger.info("Loaded parent model: %s", parent_path)

    # Build FrameAnnotationGroup-compatible objects
    class _FakeGroup:
        def __init__(self, g: dict) -> None:
            self.acquisition_id = g["acquisition_id"]
            self.frame_filename = g["frame_filename"]
            self.dataset_path = g.get("dataset_path", "")
            self.zones = g.get("zones", [])
            self.landmarks = g.get("landmarks", [])

    fake_groups = [_FakeGroup(g) for g in groups]

    # Split
    n_train = int(len(fake_groups) * 0.8)
    train_ds = MultitaskDataset(fake_groups[:n_train], zone_map, lm_names, img_size)
    val_ds = MultitaskDataset(fake_groups[n_train:], zone_map, lm_names, img_size)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2)

    criterion = MultiTaskLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
    scaler = torch.amp.GradScaler("cuda")

    best_dice = 0.0
    run_name = f"{bone_type}_multitask_gen{generation}"

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        for batch in train_loader:
            imgs = batch["image"].to(device)
            seg_t = batch["seg_mask"].to(device)
            hm_t = batch["heatmaps"].to(device)
            fov = batch["fov_mask"].to(device)
            seg_m = batch["seg_present"].to(device)
            lm_m = batch["landmark_mask"].to(device)

            optimizer.zero_grad()
            with torch.amp.autocast("cuda"):
                seg_pred, hm_pred, _ = model(imgs)
                losses = criterion(seg_pred, seg_t, hm_pred, hm_t, fov, seg_mask=seg_m, lm_mask=lm_m)

            scaler.scale(losses["total"]).backward()
            scaler.step(optimizer)
            scaler.update()
            epoch_loss += losses["total"].item()
            n_batches += 1

        scheduler.step()

        # Validation Dice
        model.eval()
        dice_sum, dice_count = 0.0, 0
        with torch.no_grad():
            for batch in val_loader:
                imgs = batch["image"].to(device)
                seg_t = batch["seg_mask"].to(device)
                with torch.amp.autocast("cuda"):
                    seg_pred, _, _ = model(imgs)
                pred_cls = seg_pred.argmax(dim=1)
                for c in range(1, n_seg):
                    inter = ((pred_cls == c).float() * (seg_t == c).float()).sum()
                    union = (pred_cls == c).float().sum() + (seg_t == c).float().sum()
                    if union > 0:
                        dice_sum += (2 * inter / (union + 1e-8)).item()
                        dice_count += 1
        val_dice = dice_sum / max(dice_count, 1)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            logger.info("Epoch %d/%d loss=%.4f dice=%.4f", epoch + 1, epochs,
                        epoch_loss / max(n_batches, 1), val_dice)

        if val_dice > best_dice:
            best_dice = val_dice
            model_path = Path(ml_models_dir) / f"{run_name}_best.pt"
            torch.save(model.state_dict(), model_path)

    logger.info("Training complete: best_dice=%.4f", best_dice)
    print(json.dumps({"best_dice": best_dice, "epochs_run": epochs}))


if __name__ == "__main__":
    main()
