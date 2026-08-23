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

## Deployment via ml-compute API

### 1. Deploy SAM Job

```bash
curl -X POST http://10.0.0.44:9469/api/serve/sam/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "action": "deploy"
  }'
```

**Response** (success):
```json
{
  "status": "deployed",
  "message": "SAM job submitted to Nomad"
}
```

### 2. Check SAM Status

```bash
curl http://10.0.0.44:9469/api/serve/sam/status
```

**Response** (when running):
```json
{
  "status": "deployed",
  "job_name": "sam-inference",
  "job_status": "running",
  "allocation_count": 1,
  "running_allocation": "...",
  "endpoint": "http://10.0.0.26:9470",
  "sam_health": "ok",
  "is_deployed": true,
  "gpu_allocated": [...]
}
```

### 3. Submit Segmentation Request

```bash
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "...",
    "points": [[100, 200], [150, 300]],
    "negative_points": [[50, 50]]
  }'
```

### 4. Stop SAM Job

```bash
curl -X DELETE http://10.0.0.44:9469/api/serve/sam/undeploy \
  -H "Content-Type: application/json" \
  -d '{
    "action": "undeploy"
  }'
```

## Direct Nomad Submission (Advanced)

For advanced usage, submit directly to Nomad API:

```bash
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/submit \
  -H "Content-Type: application/json" \
  -d @sam_job_spec.json
```

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
