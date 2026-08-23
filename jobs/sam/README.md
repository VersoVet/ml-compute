# SAM (Segment Anything Model) Deployment via Nomad

SAM est un modèle d'inférence deep learning pour segmentation automatique d'images. Il est déployé en tant que job Nomad avec **réservation GPU exclusive** pour éviter les conflits avec les jobs Ray training.

## Architecture

```
User Submit SAM Request
  ↓
ml-compute API (/api/serve/sam/interact)
  ↓
Check GPU availability via Nomad
  ├─ If GPU free → allocate + start SAM Docker
  └─ If GPU busy → queue or reject
  ↓
SAM runs with exclusive GPU access
  ↓
Return segmentation mask to user
  ↓
Release GPU via Nomad
```

## Submission via Nomad API

### Option 1: Direct Nomad Job Submission

```bash
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sam-inference",
    "job_type": "service",
    "driver": "docker",
    "image": "pytorch/pytorch:2.1-cuda12.1-runtime-ubuntu22.04",
    "command": "python -c \"import torch; print(torch.cuda.is_available())\"",
    "constraints": [
      {
        "task_name": "sam",
        "cpu_mhz": 4000,
        "memory_mb": 12288,
        "num_gpus": 1
      }
    ],
    "env_vars": {
      "CUDA_VISIBLE_DEVICES": "0"
    }
  }'
```

### Option 2: Via ml-compute SAM Routes (Future)

Routes SAM géreront automatiquement coordination Nomad:

```bash
POST /api/serve/sam/start     # Start with GPU reservation
POST /api/serve/sam/interact  # Run inference
POST /api/serve/sam/stop      # Stop + release GPU
```

## Ressources Requises

| Ressource | Valeur |
|-----------|--------|
| GPU | 1x (12GB min) — SAM ViT-B |
| CPU | 4 cores |
| RAM | 12 GB |

**Supported GPUs**:
- ✓ OnyxCortex: RTX 4070 SUPER 12GB — RECOMMANDÉ
- ⚠ OnyxPoint: T1000 8GB — Possible mais risqué (OOM)
- ✗ Glia: CPU-only — Not supported

## Coordination avec Ray Training

```
SAM active (GPU reserved)
  ↓ Ray job soumis?
  ├─ OnyxCortex GPU: BUSY (SAM)
  ├─ OnyxPoint GPU: FREE → allouer job là
  └─ Glia CPU: FREE → allouer job CPU
  
Ray training finit
  ↓ Prochaine requête SAM?
  └─ GPU libre → allocation OK
```

## Testing

```bash
# Check GPU availability before submitting
curl http://10.0.0.44:9469/api/nomad/gpu-status

# Submit simple test job (no GPU)
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/submit \
  -d '{
    "name": "test-sam",
    "image": "ubuntu:22.04",
    "command": "echo SAM test",
    "constraints": [{"task_name": "t", "cpu_mhz": 500, "memory_mb": 256, "num_gpus": 0}]
  }' | jq .job_id

# Check job status
curl http://10.0.0.44:9469/api/nomad/jobs/<job-id>
```

## Next: SAM Integration Workflow

1. ✓ Nomad cluster ready (GPU coordination)
2. ✓ API endpoints for job management
3. → Update SAM routes to use Nomad
4. → Test SAM + Ray training parallel execution
5. → Monitor via Prometheus
