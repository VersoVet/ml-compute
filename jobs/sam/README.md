# SAM (Segment Anything Model) Deployment via Ray Serve

Deploy the Segment Anything Model (vit_b) on OnyxCortex GPU worker for interactive annotation with CVAT.

## ⚠️ CRITICAL: GPU Resource Management

**OnyxCortex has 1 GPU (RTX 4070 SUPER)**. SAM reserves `num_gpus=1` permanently when deployed.

- While SAM is running → GPU is 100% reserved, training jobs are BLOCKED in PENDING state
- SAM must be explicitly stopped before launching training jobs
- GPU becomes available for training only after SAM is stopped

**Strategy**: SAM is deployed/stopped on-demand:
1. **Annotation Phase**: Start SAM, use for annotations, then STOP
2. **Training Phase**: Launch training jobs (GPU now available)

---

## Prerequisites

- Ray cluster running (OnyxSoma head + OnyxCortex worker)
- Model file: `~/sam-gpu/sam_vit_b_01ec64.pth` on OnyxCortex (375MB)
- GPU: RTX 4070 SUPER (12GB VRAM) - OnyxCortex ✅
- Python packages: `segment-anything`, `opencv-python`, `Pillow`, `torch`

**NOT recommended for OnyxPoint**: T1000 8GB is insufficient (~10GB required for SAM vit_b)

---

## Usage: Start / Stop Lifecycle

### Step 1: Start SAM (Before Annotations)

```bash
# Start SAM Serve deployment
curl -X POST http://10.0.0.44:9469/api/serve/start-sam

# Response:
{
  "status": "deployed",
  "endpoint": "http://10.0.0.44:9470/api/interact",
  "job_id": "raysubmit_abc123",
  "message": "SAM deployed successfully, GPU reserved (num_gpus=1)"
}
```

### Step 2: Use SAM for Annotations

CVAT or your annotation tool sends POST requests to SAM:

```bash
curl -X POST http://10.0.0.44:9470/api/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image",
    "positive_points": [[100, 100], [200, 200]],
    "negative_points": [[150, 150]],
    "prompt_labels": [1, 1, 0]
  }'

# Response:
{
  "mask": "base64_encoded_png_mask",
  "area": 12345,
  "status": "success",
  "image_shape": [1080, 1920, 3]
}
```

### Step 3: Check SAM Status

```bash
# Monitor SAM responsiveness
curl -X GET http://10.0.0.44:9469/api/serve/sam/status

# Response:
{
  "status": "running",
  "latency_ms": 450,
  "endpoint": "http://10.0.0.44:9470/api/interact"
}
```

### Step 4: Stop SAM (Before Training)

**MANDATORY before launching training jobs!**

```bash
# Stop SAM Serve deployment
curl -X POST http://10.0.0.44:9469/api/serve/stop-sam

# Response:
{
  "status": "stopped",
  "message": "SAM deployment stopped, GPU is now available for training"
}
```

### Step 5: Launch Training (GPU Now Available)

```bash
# GPU is now free, training can use num_gpus=1
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-training-after-annotations",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "humerus",
        "EPOCHS": "100"
      }
    },
    "submit_kwargs": {"num_gpus": 1}
  }'
```

---

## API Endpoints

### POST /api/serve/start-sam
Start SAM deployment with GPU reservation.

### POST /api/serve/stop-sam
Stop SAM and free GPU for training.

### GET /api/serve/sam/status
Check if SAM is running and responsive.

### GET /api/serve/sam/info
Get SAM specs, resource requirements, and usage strategy.

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Model load time | ~2-3 seconds (first time) |
| Inference latency | 500-1000ms per prediction |
| Max batch size | 1 (single image) |
| Memory peak | ~10-11 GB during inference |
| Recommended max image size | 1024x1024 |

---

## Resource Allocation Summary

```
Scenario 1: Annotations Only
┌─────────────────────┐
│ GPU 1: SAM running  │
│ Training: BLOCKED   │
└─────────────────────┘

Scenario 2: After stopping SAM
┌─────────────────────┐
│ GPU 1: Training     │
│ Annotations: N/A    │
└─────────────────────┘

Scenario 3: After training finishes
┌─────────────────────┐
│ GPU 1: Available    │
│ Can restart SAM     │
└─────────────────────┘
```

---

## Troubleshooting

### SAM not responding after start-sam
- Check job status: `curl http://10.0.0.44:9469/api/jobs/{job_id}`
- Check OnyxCortex connectivity: `curl http://10.0.0.44:9469/api/nodes`
- Verify model file exists: `ssh onyx@10.0.0.26 ls ~/sam-gpu/`

### Training job stuck in PENDING while SAM is running
- **This is expected!** SAM has num_gpus=1 reserved
- Stop SAM: `curl -X POST http://10.0.0.44:9469/api/serve/stop-sam`
- Training will start immediately after SAM stops

### OnyxPoint GPU incompatibility
- T1000 has 8GB, SAM needs ~10GB → guaranteed OOM
- OnyxPoint cannot run SAM vit_b
- Use OnyxCortex only

---

## Integration with CVAT

CVAT Smart Tool can call SAM endpoint directly after start-sam:

```python
# CVAT annotation plugin example
def get_mask_from_sam(image_base64, points_positive, points_negative):
    import requests
    response = requests.post(
        "http://10.0.0.44:9470/api/interact",
        json={
            "image": image_base64,
            "positive_points": points_positive,
            "negative_points": points_negative
        },
        timeout=5
    )
    if response.status_code == 200:
        mask_base64 = response.json()["mask"]
        return mask_base64
    else:
        raise RuntimeError("SAM not responding - start it with POST /api/serve/start-sam")
```
