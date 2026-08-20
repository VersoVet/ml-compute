#!/usr/bin/env python3
"""Ray Job: EfficientNet-B0 training for bone recognition.

Supports Phase A (angle pre-training) and Phase B (multi-task supervised training)
with DDP, AMP, curriculum learning, and MLflow tracking.

Environment variables:
    DATA_DIR: Path to training data (required)
    PHASE: "pretrain" or "train" (default: "train")
    CHECKPOINT_DIR: Directory to save model checkpoints (default: models)
    EPOCHS: Number of epochs (default: 20 for pretrain, 50 for train)
    BATCH_SIZE: Batch size (default: 16)
    LEARNING_RATE: Learning rate (default: 1e-4)
    DEVICE: Device to use ("auto", "cpu", "cuda:0") (default: "auto")
    MLFLOW_TRACKING_URI: MLflow tracking server URI (optional)
"""

import logging
import os
import sys
from pathlib import Path

from torch.utils.data import DataLoader, random_split

# Add bone-recognition to path for imports
BONE_RECOGNITION_PATH = "/opt/onyx/skills/bone-recognition"
if os.path.exists(BONE_RECOGNITION_PATH):
    sys.path.insert(0, BONE_RECOGNITION_PATH)

# Import from bone-recognition (now available in sys.path)
try:
    from src.config import get_config  # noqa: E402
    from src.data.dataset import BoneDataset  # noqa: E402
    from src.model.architecture import (  # noqa: E402
        AnglePredictionModel,
        BoneRecognitionModel,
    )
    from src.model.trainer import AnglePretrainer, BoneTrainer  # noqa: E402
except ImportError as e:
    print(f"ERROR: Failed to import from bone-recognition: {e}")
    print(f"Make sure bone-recognition is installed at {BONE_RECOGNITION_PATH}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("train-efficientnet")


def create_dataloaders(
    cfg,
    data_dir: str,
) -> tuple[DataLoader, DataLoader]:
    """Create train/val dataloaders.

    Args:
        cfg: Configuration object.
        data_dir: Path to training data directory.

    Returns:
        Tuple of (train_loader, val_loader).
    """
    logger.info(f"Loading datasets from {data_dir}")
    train_dataset = BoneDataset(data_dir, split="train", config=cfg)
    val_dataset = BoneDataset(data_dir, split="val", config=cfg)

    # If val set is empty, split from train
    if len(val_dataset) == 0 and len(train_dataset) > 0:
        val_size = int(len(train_dataset) * cfg.training.val_split)
        train_size = len(train_dataset) - val_size
        train_dataset, val_dataset = random_split(
            train_dataset,
            [train_size, val_size],
        )

    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.training.batch_size,
        shuffle=True,
        num_workers=cfg.training.num_workers,
        pin_memory=True,
        drop_last=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg.training.batch_size,
        shuffle=False,
        num_workers=cfg.training.num_workers,
        pin_memory=False,
    )

    logger.info(f"Loaded {len(train_dataset)} train samples, {len(val_dataset)} val samples")
    return train_loader, val_loader


def run_phase_a(cfg, data_dir: str, checkpoint_dir: str) -> None:
    """Run Phase A: self-supervised angle pre-training.

    Args:
        cfg: Configuration object.
        data_dir: Path to training data.
        checkpoint_dir: Directory to save checkpoints.
    """
    logger.info("=" * 80)
    logger.info("PHASE A: ANGLE PRE-TRAINING (Self-supervised)")
    logger.info("=" * 80)

    train_loader, val_loader = create_dataloaders(cfg, data_dir)

    model = AnglePredictionModel(backbone_name="efficientnet_b0")
    pretrainer = AnglePretrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        config=cfg,
    )

    logger.info(f"Starting pre-training for {cfg.training.pretrain_epochs} epochs")
    pretrainer.train(cfg.training.pretrain_epochs)

    checkpoint_path = Path(checkpoint_dir) / "pretrained_angle.pth"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    pretrainer.save_checkpoint(checkpoint_path)
    logger.info(f"Saved pre-trained checkpoint to {checkpoint_path}")


def run_phase_b(cfg, data_dir: str, checkpoint_dir: str, use_pretrain: bool = True) -> None:
    """Run Phase B: multi-task supervised training.

    Args:
        cfg: Configuration object.
        data_dir: Path to training data.
        checkpoint_dir: Directory to save checkpoints.
        use_pretrain: Whether to use pre-trained angle weights.
    """
    logger.info("=" * 80)
    logger.info("PHASE B: MULTI-TASK SUPERVISED TRAINING")
    logger.info("=" * 80)

    train_loader, val_loader = create_dataloaders(cfg, data_dir)

    model = BoneRecognitionModel(backbone_name="efficientnet_b0")

    # Load pre-trained weights if available
    if use_pretrain:
        pretrain_path = Path(checkpoint_dir) / "pretrained_angle.pth"
        if pretrain_path.exists():
            logger.info(f"Loading pre-trained weights from {pretrain_path}")
            model.load_pretrained_backbone(pretrain_path)
        else:
            logger.warning(f"Pre-trained weights not found at {pretrain_path}. Starting from scratch.")

    trainer = BoneTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        config=cfg,
    )

    logger.info(f"Starting training for {cfg.training.epochs} epochs")
    trainer.train(cfg.training.epochs)

    checkpoint_path = Path(checkpoint_dir) / "best_model.pth"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    trainer.save_checkpoint(checkpoint_path)
    logger.info(f"Saved best model to {checkpoint_path}")

    # Log final metrics
    logger.info("=" * 80)
    logger.info(f"Final validation loss: {trainer.best_val_loss:.4f}")
    logger.info(f"Training completed after {trainer.epoch} epochs")
    logger.info("=" * 80)


def main() -> None:
    """Main entry point for Ray Job."""
    # Read environment variables
    data_dir = os.environ.get("DATA_DIR")
    if not data_dir:
        logger.error("DATA_DIR environment variable is required")
        sys.exit(1)

    phase = os.environ.get("PHASE", "train").lower()
    if phase not in ("pretrain", "train"):
        logger.error(f"PHASE must be 'pretrain' or 'train', got: {phase}")
        sys.exit(1)

    checkpoint_dir = os.environ.get("CHECKPOINT_DIR", "models")
    epochs = int(os.environ.get("EPOCHS", "20" if phase == "pretrain" else "50"))
    batch_size = int(os.environ.get("BATCH_SIZE", "16"))
    learning_rate = float(os.environ.get("LEARNING_RATE", "1e-4"))
    device = os.environ.get("DEVICE", "auto")

    logger.info("=" * 80)
    logger.info("Ray Job: EfficientNet-B0 Training")
    logger.info("=" * 80)
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Phase: {phase}")
    logger.info(f"Checkpoint directory: {checkpoint_dir}")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Learning rate: {learning_rate}")
    logger.info(f"Device: {device}")
    logger.info("=" * 80)

    # Load configuration
    cfg = get_config()

    # Override config from environment variables
    cfg.training.epochs = epochs
    cfg.training.batch_size = batch_size
    cfg.training.learning_rate = learning_rate
    if device != "auto":
        cfg.training.device = device

    # Verify data directory exists
    if not Path(data_dir).exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    # Run training phases
    try:
        if phase == "pretrain":
            run_phase_a(cfg, data_dir, checkpoint_dir)
        elif phase == "train":
            # Run both phases for complete training
            run_phase_a(cfg, data_dir, checkpoint_dir)
            run_phase_b(cfg, data_dir, checkpoint_dir, use_pretrain=True)

        logger.info("Training completed successfully!")

    except Exception as e:
        logger.error(f"Training failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
