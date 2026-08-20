# bone-recognition Training Job Template

Job template for EfficientNet-B0 training on bone recognition with curriculum learning.

## Phases

- **Phase A** (Angle Pre-training): Self-supervised pre-training on angle prediction (20 epochs)
- **Phase B** (Multi-task Training): Supervised training with curriculum learning (50 epochs)

Supports:
- Distributed Data Parallel (DDP) for multi-GPU training
- Automatic Mixed Precision (AMP)
- MLflow tracking (optional)

## Submitting the Job

### Phase A: Angle Pre-training only

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-recognition-pretrain-$(date +%s)",
    "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATA_DIR": "/opt/onyx/skills/bone-recognition/data/processed",
        "CHECKPOINT_DIR": "/opt/onyx/skills/ml-compute/models/bone-recognition",
        "PHASE": "pretrain",
        "EPOCHS": "20"
      }
    },
    "submit_kwargs": {
      "num_cpus": 8,
      "num_gpus": 1,
      "memory": 16000000000
    }
  }'
```

### Phase B: Full Training (A + B)

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-recognition-train-$(date +%s)",
    "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATA_DIR": "/opt/onyx/skills/bone-recognition/data/processed",
        "CHECKPOINT_DIR": "/opt/onyx/skills/ml-compute/models/bone-recognition",
        "PHASE": "train",
        "EPOCHS": "50",
        "BATCH_SIZE": "16",
        "LEARNING_RATE": "1e-4",
        "DEVICE": "auto"
      }
    },
    "submit_kwargs": {
      "num_cpus": 8,
      "num_gpus": 1,
      "memory": 16000000000
    }
  }'
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATA_DIR` | Yes | — | Path to training data directory |
| `PHASE` | No | `train` | `pretrain` or `train` |
| `CHECKPOINT_DIR` | No | `models` | Directory to save model checkpoints |
| `EPOCHS` | No | 20/50 | Number of training epochs |
| `BATCH_SIZE` | No | 16 | Batch size |
| `LEARNING_RATE` | No | 1e-4 | Learning rate (Adam optimizer) |
| `DEVICE` | No | `auto` | Device to use (`auto`, `cpu`, `cuda:0`, etc.) |
| `MLFLOW_TRACKING_URI` | No | — | MLflow server URL for tracking (optional) |

## Monitoring the Job

```bash
# List all jobs
curl http://10.0.0.44:9469/api/jobs

# Get job status and logs
curl http://10.0.0.44:9469/api/jobs/{job_id}

# Stream logs (tail -f)
curl http://10.0.0.44:9469/api/jobs/{job_id}/logs?follow=true
```

## Output

Training produces checkpoints in `CHECKPOINT_DIR`:
- `pretrained_angle.pth` — Pre-trained angle prediction model (Phase A only)
- `best_model.pth` — Best model during multi-task training (Phase B)

Logs are available in Ray Job system.

## Requirements

The job uses Ray's `working_dir` to include the ml-compute skill. Dependencies are installed from:
- `requirements.txt` (ml-compute)
- Available on the worker from bone-recognition's installation

## Workers

Job executes on:
- **OnyxPoint** (10.0.0.86): GPU worker with NVIDIA T1000, 10 CPUs, 23GB RAM
- **Glia** (10.0.0.8): CPU worker with 20 CPUs, 47GB RAM
