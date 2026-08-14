# ml-compute - API

## Health & Status

### GET /health
Vérifie la santé du cluster Ray et la connectivité aux workers.

**Response**:
```json
{
  "status": "healthy",
  "ray_cluster": {
    "head_node": "10.0.0.44",
    "port": 6379,
    "status": "running",
    "workers_connected": 3
  },
  "timestamp": "2026-08-08T12:00:00Z"
}
```

---

## Jobs API

### POST /api/jobs
Soumet un job Ray pour training ou inférence.

**Request**:
```json
{
  "name": "yolo-training-20240808",
  "entrypoint": "python jobs/bone-annotator/train_yolo.py",
  "runtime_env": {
    "working_dir": "/opt/onyx/skills/ml-compute",
    "env_vars": {
      "CUDA_VISIBLE_DEVICES": "0"
    }
  },
  "submit_kwargs": {
    "num_cpus": 4,
    "num_gpus": 1,
    "memory": 8000000000
  }
}
```

**Response** (202 Accepted):
```json
{
  "job_id": "01000000-0000-0000-0000-000000000001",
  "status": "SUBMITTED",
  "name": "yolo-training-20240808",
  "submission_time": "2026-08-08T12:00:00Z"
}
```

### GET /api/jobs
Liste les jobs avec filtres optionnels.

**Query Parameters**:
- `status`: SUBMITTED, RUNNING, SUCCEEDED, FAILED (optionnel)
- `limit`: Max résultats (défaut: 100)

**Response**:
```json
{
  "jobs": [
    {
      "job_id": "01000000-0000-0000-0000-000000000001",
      "name": "yolo-training-20240808",
      "status": "RUNNING",
      "submission_time": "2026-08-08T12:00:00Z",
      "start_time": "2026-08-08T12:00:10Z",
      "runtime": 120
    }
  ],
  "total": 1
}
```

### GET /api/jobs/{job_id}
Statut détaillé et logs d'un job.

**Response**:
```json
{
  "job_id": "01000000-0000-0000-0000-000000000001",
  "name": "yolo-training-20240808",
  "status": "RUNNING",
  "submission_time": "2026-08-08T12:00:00Z",
  "start_time": "2026-08-08T12:00:10Z",
  "driver_info": {
    "node_ip": "10.0.0.86",
    "pid": 12345
  },
  "logs_tail": "[2026-08-08 12:00:15] Starting YOLO training...\n[2026-08-08 12:01:00] Epoch 1/100..."
}
```

### DELETE /api/jobs/{job_id}
Arrête un job.

**Response** (204 No Content):
```
Job stopped successfully
```

---

## Nodes API

### GET /api/nodes
État des workers Ray (GPU, CPU, RAM).

**Response**:
```json
{
  "nodes": [
    {
      "node_id": "12345678-abcd",
      "node_name": "onyxpoint",
      "node_ip": "10.0.0.86",
      "is_head": false,
      "resources": {
        "CPU": 4.0,
        "GPU": 1.0,
        "memory": 16000000000,
        "VRAM_GB": 8
      },
      "available_resources": {
        "CPU": 2.0,
        "GPU": 0.5,
        "memory": 8000000000
      },
      "status": "alive"
    },
    {
      "node_id": "87654321-dcba",
      "node_name": "glia",
      "node_ip": "10.0.0.8",
      "is_head": false,
      "resources": {
        "CPU": 8.0,
        "memory": 64000000000
      },
      "available_resources": {
        "CPU": 6.0,
        "memory": 50000000000
      },
      "status": "alive"
    }
  ],
  "cluster_status": "healthy"
}
```

### GET /api/nodes/summary
Résumé agrégé des ressources cluster (CPU, GPU, mémoire) avec utilisation %.

**Response**:
```json
{
  "total": {
    "cpu": 30.0,
    "gpu": 1.0,
    "memory_bytes": 70300000000
  },
  "available": {
    "cpu": 28.0,
    "gpu": 1.0,
    "memory_bytes": 65000000000
  },
  "utilization": {
    "cpu_percent": 6.7,
    "gpu_percent": 0.0,
    "memory_percent": 7.5
  }
}
```

---

## Serve API

### GET /api/serve/deployments
Liste les applications Ray Serve déployées via l'API Dashboard HTTP.

**Response**:
```json
{
  "deployments": [
    {
      "name": "yolo-v8-bones",
      "application": "yolo-v8-bones",
      "status": "HEALTHY",
      "replicas": 2,
      "endpoint": "http://10.0.0.44:8000/yolo-v8-bones"
    }
  ],
  "ray_serve_status": "running"
}
```

### GET /api/serve/status
Statut global de Ray Serve (nombre d'applications, proxy).

**Response**:
```json
{
  "status": "running",
  "applications": 2,
  "proxy_location": "EveryNode"
}
```

### POST /api/serve/deploy
Déploie un modèle d'inférence comme application Ray Serve.

**Request**:
```json
{
  "name": "llama-3.3-8b",
  "type": "vllm",
  "model": "meta-llama/Llama-3.3-8B",
  "gpu_memory_utilization": 0.7,
  "num_replicas": 1,
  "num_gpus": 1
}
```

Types supportés : `yolo`, `efficientnet`, `vllm`, `custom`.

**Response** (202 Accepted):
```json
{
  "name": "llama-3.3-8b",
  "status": "DEPLOYING",
  "type": "vllm",
  "replicas": 1,
  "endpoint": "http://10.0.0.44:8000/llama-3.3-8b"
}
```

### POST /api/serve/undeploy
Retire une application Ray Serve.

**Request**:
```json
{
  "name": "yolo-v8-bones"
}
```

**Response** (204 No Content)

---

## Models API

### GET /api/models
Liste les modèles ML disponibles (dans /opt/onyx/skills/ml-compute/models/).

**Response**:
```json
{
  "models": [
    {
      "id": "yolo-bones-v8.1",
      "type": "yolo",
      "size_mb": 250,
      "path": "/opt/onyx/skills/ml-compute/models/bone-annotator/yolo-bones-v8.1.pt",
      "created": "2026-07-15T10:30:00Z",
      "source_job": "01000000-0000-0000-0000-000000000010"
    },
    {
      "id": "efficientnet-b0-bones",
      "type": "efficientnet",
      "size_mb": 85,
      "path": "/opt/onyx/skills/ml-compute/models/bone-recognition/efficientnet-b0-bones.pt",
      "created": "2026-08-01T14:20:00Z",
      "source_job": "01000000-0000-0000-0000-000000000015"
    }
  ],
  "total": 2
}
```

---

## Examples cURL

```bash
# Health check
curl -X GET http://10.0.0.44:9469/health

# Soumettre un job YOLO training
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "yolo-train-daily",
    "entrypoint": "python jobs/bone-annotator/train_yolo.py",
    "submit_kwargs": {"num_gpus": 1, "num_cpus": 4}
  }'

# Lister les jobs en cours
curl -X GET http://10.0.0.44:9469/api/jobs?status=RUNNING

# État des workers
curl -X GET http://10.0.0.44:9469/api/nodes | jq .

# Lister les modèles disponibles
curl -X GET http://10.0.0.44:9469/api/models
```
