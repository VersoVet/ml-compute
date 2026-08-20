#!/usr/bin/env python3
"""Ray Job: YOLOv8 training for bone annotation.

Trains a YOLOv8 object detection model on the bone dataset.

Environment variables:
    DATASET_YAML: Path to dataset.yaml (required)
    MODEL_BASE: Base model to use (default: "yolov8m.pt", options: yolov8n/s/m/l/x)
    EPOCHS: Number of training epochs (default: 100)
    IMGSZ: Image size (default: 640)
    BATCH_SIZE: Batch size (default: 16)
    LEARNING_RATE: Learning rate (default: 0.001)
    DEVICE: Device to use (default: "0" for GPU)
    ML_MODELS_DIR: Directory to save trained model (default: "/opt/onyx/skills/bone-ml/models")
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not found. Install with: pip install ultralytics")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("train-yolo")


def main() -> None:
    """Main entry point for Ray Job."""
    # Read environment variables
    dataset_yaml = os.environ.get("DATASET_YAML")
    if not dataset_yaml:
        logger.error("DATASET_YAML environment variable is required")
        sys.exit(1)

    model_base = os.environ.get("MODEL_BASE", "yolov8m.pt")
    epochs = int(os.environ.get("EPOCHS", "100"))
    imgsz = int(os.environ.get("IMGSZ", "640"))
    batch_size = int(os.environ.get("BATCH_SIZE", "16"))
    learning_rate = float(os.environ.get("LEARNING_RATE", "0.001"))
    device = os.environ.get("DEVICE", "0")
    ml_models_dir = os.environ.get("ML_MODELS_DIR", "/opt/onyx/skills/bone-ml/models")

    logger.info("=" * 80)
    logger.info("Ray Job: YOLOv8 Training")
    logger.info("=" * 80)
    logger.info(f"Dataset YAML: {dataset_yaml}")
    logger.info(f"Model base: {model_base}")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Image size: {imgsz}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Learning rate: {learning_rate}")
    logger.info(f"Device: {device}")
    logger.info(f"Output directory: {ml_models_dir}")
    logger.info("=" * 80)

    # Verify dataset YAML exists
    dataset_path = Path(dataset_yaml)
    if not dataset_path.exists():
        logger.error(f"Dataset YAML not found: {dataset_yaml}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(ml_models_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {output_dir}")

    try:
        # Load model
        logger.info(f"Loading YOLOv8 model: {model_base}")
        model = YOLO(model_base)

        # Train the model
        logger.info(f"Starting training for {epochs} epochs")
        results = model.train(
            data=dataset_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch_size,
            lr0=learning_rate,
            device=device,
            patience=20,  # Early stopping patience
            save=True,
            verbose=True,
            project="runs/detect",
            name="train",
        )

        logger.info("Training completed successfully!")

        # Extract metrics from results
        metrics = {
            "epochs": epochs,
            "model_base": model_base,
            "final_results": {
                "box_loss": float(results.box.loss) if hasattr(results, "box") else None,
                "cls_loss": float(results.cls.loss) if hasattr(results, "cls") else None,
                "map50": float(results.results_dict.get("metrics/mAP50(B)", 0.0)) if hasattr(results, "results_dict") else None,
                "map50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0.0)) if hasattr(results, "results_dict") else None,
            },
        }

        logger.info(f"Final metrics: {json.dumps(metrics, indent=2)}")

        # Move best.pt to ML_MODELS_DIR
        train_weights_path = Path("runs/detect/train/weights/best.pt")
        if train_weights_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"bone-annotator-yolov8m-{timestamp}.pt"
            output_model_path = output_dir / model_name

            shutil.copy2(train_weights_path, output_model_path)
            logger.info(f"Saved trained model to: {output_model_path}")

            # Also save metrics as JSON
            metrics_path = output_dir / f"bone-annotator-yolov8m-{timestamp}-metrics.json"
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Saved metrics to: {metrics_path}")

        else:
            logger.warning("Best weights not found at expected location")

        logger.info("=" * 80)
        logger.info("Training job completed successfully!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Training failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
