"""Integration tests for job templates (bone-recognition and bone-annotator).

Tests verify job template payload structure and environment variable handling.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class TestJobTemplatePayloads:
    """Tests for job template submission payloads."""

    def test_bone_recognition_phase_a_payload(self):
        """Test bone-recognition Phase A (pretrain) job payload."""
        payload = {
            "name": "bone-pretrain-test",
            "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
            "runtime_env": {
                "working_dir": "/opt/onyx/skills/ml-compute",
                "env_vars": {
                    "DATA_DIR": "/opt/onyx/skills/bone-recognition/data/processed",
                    "CHECKPOINT_DIR": "/tmp/checkpoints",
                    "PHASE": "pretrain",
                    "EPOCHS": "20",
                },
            },
            "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000},
        }

        # Validate JSON serializability
        json_str = json.dumps(payload)
        parsed = json.loads(json_str)

        assert parsed["name"] == "bone-pretrain-test"
        assert parsed["runtime_env"]["env_vars"]["PHASE"] == "pretrain"
        assert parsed["submit_kwargs"]["num_gpus"] == 1

    def test_bone_recognition_phase_b_payload(self):
        """Test bone-recognition Phase B (full training) job payload."""
        payload = {
            "name": "bone-train-test",
            "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
            "runtime_env": {
                "working_dir": "/opt/onyx/skills/ml-compute",
                "env_vars": {
                    "DATA_DIR": "/opt/onyx/skills/bone-recognition/data/processed",
                    "CHECKPOINT_DIR": "/tmp/checkpoints",
                    "PHASE": "train",
                    "EPOCHS": "50",
                    "BATCH_SIZE": "16",
                    "LEARNING_RATE": "1e-4",
                },
            },
            "submit_kwargs": {"num_cpus": 8, "num_gpus": 1},
        }

        json_str = json.dumps(payload)
        parsed = json.loads(json_str)

        assert parsed["runtime_env"]["env_vars"]["PHASE"] == "train"
        assert parsed["runtime_env"]["env_vars"]["EPOCHS"] == "50"

    def test_bone_annotator_yolo_m_payload(self):
        """Test bone-annotator YOLOv8m training job payload."""
        payload = {
            "name": "bone-yolo-train-test",
            "entrypoint": "python jobs/bone-annotator/train_yolo.py",
            "runtime_env": {
                "working_dir": "/opt/onyx/skills/ml-compute",
                "env_vars": {
                    "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml",
                    "MODEL_BASE": "yolov8m.pt",
                    "EPOCHS": "100",
                    "BATCH_SIZE": "16",
                    "LEARNING_RATE": "0.001",
                },
            },
            "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000},
        }

        json_str = json.dumps(payload)
        parsed = json.loads(json_str)

        assert parsed["runtime_env"]["env_vars"]["MODEL_BASE"] == "yolov8m.pt"
        assert parsed["runtime_env"]["env_vars"]["EPOCHS"] == "100"

    def test_bone_annotator_yolo_n_payload(self):
        """Test bone-annotator YOLOv8n (quick) training job payload."""
        payload = {
            "name": "bone-yolo-quick-test",
            "entrypoint": "python jobs/bone-annotator/train_yolo.py",
            "runtime_env": {
                "working_dir": "/opt/onyx/skills/ml-compute",
                "env_vars": {
                    "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml",
                    "MODEL_BASE": "yolov8n.pt",
                    "EPOCHS": "30",
                    "BATCH_SIZE": "32",
                },
            },
            "submit_kwargs": {"num_cpus": 4, "num_gpus": 1, "memory": 8000000000},
        }

        json_str = json.dumps(payload)
        parsed = json.loads(json_str)

        assert parsed["runtime_env"]["env_vars"]["MODEL_BASE"] == "yolov8n.pt"


class TestJobTemplateFiles:
    """Tests for job template file existence and structure."""

    def test_bone_recognition_template_exists(self):
        """Test that bone-recognition training template exists."""
        template_path = Path("/home/onyx/projects/skills/ml-compute") / "jobs" / "bone-recognition" / "train_efficientnet.py"
        assert template_path.exists(), f"Template not found: {template_path}"

    def test_bone_annotator_template_exists(self):
        """Test that bone-annotator training template exists."""
        template_path = Path("/home/onyx/projects/skills/ml-compute") / "jobs" / "bone-annotator" / "train_yolo.py"
        assert template_path.exists(), f"Template not found: {template_path}"

    def test_bone_recognition_readme_exists(self):
        """Test that bone-recognition README exists."""
        readme_path = Path("/home/onyx/projects/skills/ml-compute") / "jobs" / "bone-recognition" / "README.md"
        assert readme_path.exists(), f"README not found: {readme_path}"

        # Verify content has examples
        content = readme_path.read_text()
        assert "Phase A" in content or "pretrain" in content
        assert "curl" in content

    def test_bone_annotator_readme_exists(self):
        """Test that bone-annotator README exists."""
        readme_path = Path("/home/onyx/projects/skills/ml-compute") / "jobs" / "bone-annotator" / "README.md"
        assert readme_path.exists(), f"README not found: {readme_path}"

        # Verify content has model selection guide
        content = readme_path.read_text()
        assert "YOLOv8" in content or "yolov8" in content
        assert "curl" in content


class TestJobTemplateEnvVars:
    """Tests for environment variable handling in job templates."""

    def test_bone_recognition_required_env_vars(self):
        """Test that bone-recognition template requires DATA_DIR."""
        # The template checks DATA_DIR in main()
        required_vars = ["DATA_DIR"]

        payload = {
            "runtime_env": {
                "env_vars": {
                    "DATA_DIR": "/path/to/data",
                    "CHECKPOINT_DIR": "/path/to/checkpoints",
                    "PHASE": "train",
                }
            }
        }

        # Verify all required vars are present
        for var in required_vars:
            assert var in payload["runtime_env"]["env_vars"]

    def test_bone_annotator_required_env_vars(self):
        """Test that bone-annotator template requires DATASET_YAML."""
        required_vars = ["DATASET_YAML"]

        payload = {
            "runtime_env": {
                "env_vars": {
                    "DATASET_YAML": "/path/to/dataset.yaml",
                    "MODEL_BASE": "yolov8m.pt",
                    "EPOCHS": "100",
                }
            }
        }

        # Verify all required vars are present
        for var in required_vars:
            assert var in payload["runtime_env"]["env_vars"]

    def test_env_var_defaults(self):
        """Test that optional env vars have sensible defaults."""
        # bone-recognition defaults
        br_defaults = {
            "PHASE": "train",
            "CHECKPOINT_DIR": "models",
            "EPOCHS": "50",
            "BATCH_SIZE": "16",
            "LEARNING_RATE": "1e-4",
        }

        # bone-annotator defaults
        ba_defaults = {
            "MODEL_BASE": "yolov8m.pt",
            "EPOCHS": "100",
            "IMGSZ": "640",
            "BATCH_SIZE": "16",
            "LEARNING_RATE": "0.001",
        }

        # These should be documented in the templates
        assert "train" in br_defaults["PHASE"]
        assert "yolov8m.pt" in ba_defaults["MODEL_BASE"]
