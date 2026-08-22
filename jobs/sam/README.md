# SAM (Segment Anything Model) Deployment via Docker

Deploy the Segment Anything Model (vit_b) on OnyxCortex GPU worker for interactive annotation with CVAT.

## ⚠️ CRITICAL: GPU Resource Management

**OnyxCortex has 1 GPU (RTX 4070 SUPER, 12GB VRAM)**. SAM reserves the GPU exclusively while running.

- While SAM Docker container is running → GPU is 100% reserved, training jobs are BLOCKED
- SAM must be explicitly stopped before launching training jobs
- GPU becomes available for training only after SAM container stops

**Strategy**: Deploy and stop SAM on-demand via Docker:
1. **Annotation Phase**: Start SAM container, use for annotations
2. **Training Phase**: Stop SAM, launch training jobs (GPU now free)

---

## Quick Start

### Prerequisites

- OnyxCortex machine with GPU (RTX 4070 SUPER)
- SAM model weights: `~/sam-gpu/sam_vit_b_01ec64.pth` (375MB)
- Docker and NVIDIA Container Toolkit installed
- ml-compute skill deployed on OnyxSoma (10.0.0.44:9469)

**NOT recommended for OnyxPoint**: T1000 8GB is insufficient (~10GB required for SAM vit_b)

### Build and Deploy

```bash
# On OnyxCortex (10.0.0.26):
cd /opt/onyx/skills/ml-compute
bash docker/build_and_run_sam.sh
```

The script will:
1. Build `onyx/sam:latest` Docker image
2. Start SAM container on port 9470
3. Mount GPU and NFS volumes
4. Verify health check

### Verify SAM is Running

```bash
# Check container status
docker ps | grep sam-service

# Check health
curl http://10.0.0.26:9470/health

# Check readiness
curl http://10.0.0.26:9470/ready
```

---

## Using SAM via ml-compute API

Once SAM is running on OnyxCortex, access it through ml-compute proxy endpoints:

### Check SAM Status

```bash
curl http://10.0.0.44:9469/api/serve/sam/status
```

Response:
```json
{
  "status": "healthy",
  "service": "sam-vit-b"
}
```

### Get SAM Info

```bash
curl http://10.0.0.44:9469/api/serve/sam/info
```

Returns: model specs, GPU requirements, inference latency, and endpoints.

### Interactive Segmentation

```bash
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image",
    "positive_points": [[100, 100], [200, 200]],
    "negative_points": [[150, 150]]
  }'
```

Response:
```json
{
  "mask": "base64_encoded_png_mask",
  "area": 12345,
  "status": "success",
  "image_shape": [1080, 1920, 3]
}
```

---

## Docker Container Management

### Stop SAM (Free GPU)

```bash
docker stop sam-service
```

### Restart SAM

```bash
docker start sam-service
```

### Remove SAM (Complete Cleanup)

```bash
docker rm -f sam-service
docker rmi onyx/sam:latest
```

### View Logs

```bash
docker logs -f sam-service
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Container startup time | ~30s (includes pip install first time) |
| Model load time | ~2-3 seconds |
| Inference latency | 500-1000ms per prediction |
| Max batch size | 1 (single image) |
| Memory peak | ~10-11 GB during inference |
| Recommended max image size | 1024x1024 |

---

## Integration with CVAT

CVAT Smart Tool can call SAM endpoint after container starts:

```python
# CVAT annotation plugin
def get_mask_from_sam(image_base64, points_positive, points_negative):
    import requests
    
    # Use ml-compute proxy
    response = requests.post(
        "http://10.0.0.44:9469/api/serve/sam/interact",
        json={
            "image": image_base64,
            "positive_points": points_positive,
            "negative_points": points_negative
        },
        timeout=5
    )
    
    if response.status_code == 200:
        return response.json()["mask"]
    else:
        raise RuntimeError("SAM not available")
```

---

## Troubleshooting

### SAM container won't start

```bash
# Check logs
docker logs sam-service

# Verify GPU access
docker exec sam-service nvidia-smi

# Rebuild from scratch
docker rm -f sam-service
bash docker/build_and_run_sam.sh
```

### ml-compute proxy returns "unhealthy"

```bash
# Verify OnyxCortex is accessible
curl http://10.0.0.26:9470/health

# Check ml-compute logs
docker logs ml-compute
```

### Training job still PENDING while SAM runs

**This is expected!** SAM has exclusive GPU access. Stop SAM first:

```bash
docker stop sam-service
# Training will start immediately
```

---

## Architecture

```
CVAT / User Interface
        ↓
ml-compute (OnyxSoma:9469)
    ↓ proxy request
SAM Docker Service (OnyxCortex:9470)
    ↓ forward
SAM Model (PyTorch, GPU)
```

- **ml-compute**: Central orchestrator with SAM proxy routes
- **SAM Docker**: Lightweight service on GPU machine
- **GPU isolation**: Docker + NVIDIA runtime ensures exclusive GPU access
