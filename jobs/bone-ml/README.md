# bone-ml Dual-Head U-Net Multitask Training Job Template

Job template for training a Dual-Head U-Net model on bone anatomical zones and landmarks using segmentation-models-pytorch.

## Features

- Segmentation: Bone anatomical zones (humerus, femur, tibia, fibula, etc.)
- Landmarks: Gaussian heatmaps for anatomical points
- Shared encoder: ResNet34/50/Swin backbone (pretrained ImageNet)
- Curriculum learning via SGR (Segmentation-Guided Refinement)
- Mixed precision training (AMP)
- Early stopping with patience (15 epochs)
- PostgreSQL-backed annotation validation
- Automatic model checkpointing

## Submitting the Job

### Basic Training (humerus, ResNet34)

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-multitask-humerus-$(date +%s)",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "humerus",
        "EPOCHS": "100",
        "BATCH_SIZE": "4",
        "IMG_SIZE": "1408",
        "LEARNING_RATE": "0.0001",
        "ENCODER_NAME": "resnet34",
        "DEVICE": "0",
        "ML_MODELS_DIR": "/mnt/ml-store/models",
        "ML_RUNS_DIR": "/mnt/ml-store/runs",
        "GENERATION": "1",
        "LABEL_GENERATOR_URL": "http://10.0.0.59:9466",
        "PG_HOST": "10.0.0.59",
        "PG_PORT": "5432",
        "PG_DB": "bone_recognition",
        "PG_USER": "bone",
        "PG_PASSWORD": "YOUR_PASSWORD_HERE",
        "SOURCE_FILTER": "manual,corrected_ml"
      }
    },
    "submit_kwargs": {
      "num_cpus": 8,
      "num_gpus": 1,
      "memory": 16000000000
    }
  }'
```

### Large Model Training (ResNet50, fine-tuning)

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-multitask-femur-resnet50-$(date +%s)",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "femur",
        "EPOCHS": "150",
        "BATCH_SIZE": "2",
        "ENCODER_NAME": "resnet50",
        "DEVICE": "0",
        "LEARNING_RATE": "0.00005",
        "GENERATION": "2",
        "PARENT_MODEL": "/mnt/ml-store/models/femur_multitask_gen1_best.pt",
        "PG_PASSWORD": "YOUR_PASSWORD_HERE"
      }
    },
    "submit_kwargs": {
      "num_cpus": 12,
      "num_gpus": 1,
      "memory": 24000000000
    }
  }'
```

### Quick Training (Swin backbone, reduced size)

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-multitask-quick-$(date +%s)",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "tibia",
        "EPOCHS": "50",
        "BATCH_SIZE": "8",
        "IMG_SIZE": "768",
        "ENCODER_NAME": "swin_small_patch4_window7_224",
        "PG_PASSWORD": "YOUR_PASSWORD_HERE"
      }
    },
    "submit_kwargs": {
      "num_cpus": 6,
      "num_gpus": 1,
      "memory": 12000000000
    }
  }'
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BONE_TYPE` | No | `humerus` | Bone type: humerus, femur, tibia, fibula, radius, ulna |
| `EPOCHS` | No | `100` | Number of training epochs |
| `BATCH_SIZE` | No | `4` | Batch size per GPU |
| `IMG_SIZE` | No | `1408` | Image size (pixels) |
| `LEARNING_RATE` | No | `0.0001` | Initial learning rate (AdamW) |
| `ENCODER_NAME` | No | `resnet34` | Backbone encoder: resnet34, resnet50, resnet101, swin_small, swin_base |
| `DEVICE` | No | `0` | CUDA device ID (0, 1, ...) or `cpu` |
| `ML_MODELS_DIR` | No | `/mnt/ml-store/models` | Output directory for trained models |
| `ML_RUNS_DIR` | No | `/mnt/ml-store/runs` | Directory for training runs and logs |
| `GENERATION` | No | `1` | Model generation/version number |
| `PARENT_MODEL` | No | — | Path to parent model for fine-tuning (optional) |
| `LABEL_GENERATOR_URL` | No | `http://10.0.0.59:9466` | Label generator service URL |
| `PG_HOST` | No | `10.0.0.59` | PostgreSQL host |
| `PG_PORT` | No | `5432` | PostgreSQL port |
| `PG_DB` | No | `bone_recognition` | PostgreSQL database |
| `PG_USER` | No | `bone` | PostgreSQL user |
| `PG_PASSWORD` | **Yes** | — | PostgreSQL password (store in Vault, not in code!) |
| `SOURCE_FILTER` | No | `manual,corrected_ml` | Annotation sources to include (comma-separated) |

## Encoder Selection Guide

| Encoder | Speed | Accuracy | Memory | Best For |
|---------|-------|----------|--------|----------|
| **resnet34** | Fast | Good | 8GB | Standard, balanced |
| **resnet50** | Medium | Better | 12GB | **Recommended** for production |
| **resnet101** | Slow | Best | 18GB | Maximum accuracy |
| **swin_small** | Medium | Very Good | 10GB | Vision Transformer alternative |
| **swin_base** | Very Slow | Best | 20GB | Highest accuracy (resource-intensive) |

## Architecture

### Dual-Head U-Net

```
Input (B, 3, 1408, 1408)
    ↓
Shared Encoder (ResNet34)
    ├→ Segmentation Decoder → [N_classes] (zones)
    ├→ Landmarks Decoder → [N_landmarks] (heatmaps)
    └→ Concatenate (SGR) → Refined Landmarks
```

**Segmentation Head**: Cross-Entropy + Dice loss on zone masks
**Landmarks Head**: MSE loss on Gaussian heatmaps
**SGR Pattern**: Segmentation output guides landmark refinement via feature concatenation

## Data Sources

### label-generator API (10.0.0.59:9466)
- Classes and bone mapping: `GET /labels/api/export/yolo?bone_type={BONE_TYPE}`
- Landmark definitions: `GET /labels/api/export/cvat` (XML)

### PostgreSQL (10.0.0.59:5432)
Database: `bone_recognition`

Table: `annotation_tasks`
- `id`, `bone_type`, `status` (validated/pending/rejected)
- `created_at`, `updated_at`

Table: `frame_annotations`
- `id`, `task_id`, `image_id`
- `zones` (JSON mask regions)
- `landmarks` (JSON heatmap points)
- `source` (manual, corrected_ml, auto_generated)

Query filters by:
- `status = 'validated'` (only approved annotations)
- `bone_type = ?` (specific bone)
- `source IN ?` (included sources, e.g., manual, corrected_ml)

### Images (BoneStore NFS)
- Path: `/mnt/bonestore/images/{bone_type}/{image_id}.png`
- Format: 16-bit grayscale TIFF or PNG
- Automatically loaded by `MultitaskDataset`

## Monitoring the Job

```bash
# List all jobs
curl http://10.0.0.44:9469/api/jobs

# Get job status and logs
curl http://10.0.0.44:9469/api/jobs/{job_id}

# Stop a job
curl -X DELETE http://10.0.0.44:9469/api/jobs/{job_id}
```

## Output

Training produces files in `ML_MODELS_DIR`:

- `{BONE_TYPE}_multitask_gen{GENERATION}_best.pt` — Best model weights (lowest validation loss)
- `{BONE_TYPE}_multitask_gen{GENERATION}_final.pt` — Final model (end of training)

Training logs in `ML_RUNS_DIR`:
- `{BONE_TYPE}_gen{GENERATION}/metrics.json` — Per-epoch metrics (dice, loss, val_loss)
- `{BONE_TYPE}_gen{GENERATION}/config.yaml` — Training hyperparameters

## Workers

Job executes on:
- **OnyxPoint** (10.0.0.86): GPU worker with NVIDIA T1000, 10 CPUs, 23GB RAM
- **Glia** (10.0.0.8): CPU worker with 20 CPUs, 47GB RAM (suitable for quick experiments)

## Example: Full Training Pipeline

1. **Prepare dataset** (via label-generator and PostgreSQL)
   - Push annotations via label-generator API
   - Mark as validated in PostgreSQL

2. **Submit training job**
   ```bash
   curl -X POST http://10.0.0.44:9469/api/jobs -d '...' # See examples above
   ```

3. **Monitor progress**
   ```bash
   # Every 30 seconds
   curl http://10.0.0.44:9469/api/jobs/{job_id} | jq .status
   ```

4. **Deploy trained model** (via bone-ml inference service)
   ```bash
   # Inference automatically uses the newest model (by mtime)
   curl -X POST http://10.0.0.86:9463/api/predict \
     -F "image=@photo.png" \
     -F "bone_type=humerus"
   ```

## Security Notes

- **PG_PASSWORD**: Never hardcode. Fetch from Vault:
  ```bash
  PG_PASS=$(curl -s -H "X-Vault-Token: $ONYX_VAULT_TOKEN" \
    http://10.0.0.44:8050/vault/pg_bone_password)
  ```

- **GPU Resource Limits**: Set `num_gpus` to ensure fair sharing with other jobs

- **Storage**: Ensure `/mnt/ml-store` has sufficient space (models ~500MB each, runs ~2GB per epoch)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **No annotations found** | Check `PG_PASSWORD` and `SOURCE_FILTER`; verify data in PostgreSQL |
| **GPU out of memory** | Reduce `BATCH_SIZE` or `IMG_SIZE`; use smaller encoder |
| **Slow training** | Increase `BATCH_SIZE` if memory allows; use `num_cpus=12` |
| **Model not saved** | Check write permissions on `ML_MODELS_DIR` and disk space |
| **Import errors** | Ensure `bone-ml` skill is deployed; dependencies: `segmentation-models-pytorch`, `timm`, `asyncpg` |

## Dependencies

Required on worker:
- `torch`, `torchvision` (GPU support)
- `segmentation-models-pytorch`
- `timm` (timm encoders)
- `asyncpg` (PostgreSQL async driver)
- `httpx` (async HTTP client)
- `blosc2` (image compression)
- `Pillow`, `opencv-python-headless`

These are installed as part of the bone-ml skill or Ray worker image.
