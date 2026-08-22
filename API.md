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

## Nomad Orchestration API

### GET /api/nomad/status
Récupère le statut global du cluster Nomad (nodes, GPUs, jobs).

**Response**:
```json
{
  "nodes_ready": 3,
  "nodes_total": 3,
  "gpus_total": 2,
  "gpus_available": 2,
  "jobs_running": 0,
  "jobs_pending": 0
}
```

**Description**:
- `nodes_ready`: Nombre de nœuds prêts à recevoir des jobs
- `gpus_total`: Total des GPUs dans le cluster (OnyxCortex + OnyxPoint)
- `gpus_available`: GPUs libres pour allocation
- `jobs_running`: Jobs en cours d'exécution
- `jobs_pending`: Jobs en attente d'allocation

---

### POST /api/nomad/jobs/submit
Soumet un job à Nomad avec reservation de ressources (CPU, RAM, GPU).

**Request**:
```json
{
  "name": "bone-ml-training-001",
  "job_type": "batch",
  "driver": "docker",
  "image": "rayproject/ray:2.35.0-py312",
  "command": "python /app/train_multitask.py",
  "constraints": [
    {
      "task_name": "training",
      "cpu_mhz": 8000,
      "memory_mb": 16384,
      "num_gpus": 1
    }
  ],
  "env_vars": {
    "EPOCHS": "100",
    "BATCH_SIZE": "32",
    "BONE_TYPE": "femur"
  },
  "volumes": {
    "/mnt/ml-store": "/data/ml",
    "/mnt/bonestore": "/data/bones"
  },
  "timeout_seconds": 7200
}
```

**Response** (202 OK):
```json
{
  "status": "submitted",
  "job_id": "bone-ml-training-001",
  "evaluation_id": "c0e1bdd3-8896-92fd-516c-d941c3011e76"
}
```

**Champs**:
- `name`: Identifiant unique du job (kebab-case)
- `job_type`: Type de job (`batch` = one-time, `service` = long-running)
- `driver`: Driver d'exécution (`docker`, `raw_exec`, `exec`)
- `image`: Image Docker (pour driver docker)
- `command`: Commande à exécuter
- `constraints`: Ressources requises (CPU MHz, RAM MB, num_gpus)
- `env_vars`: Variables d'environnement pour le job
- `volumes`: Montages NFS (source → destination)
- `timeout_seconds`: Durée maximale du job

**GPU Reservation**:
- Si `num_gpus: 1` → Nomad alloue 1 GPU exclusif au job
- Si SAM Docker utilise déjà une GPU → Job attend libération
- GPU exclusive = pas de CUDA OOM conflict

---

### GET /api/nomad/jobs/{job_id}
Récupère le statut et l'historique d'allocation d'un job.

**Response**:
```json
{
  "job_id": "bone-ml-training-001",
  "status": "running",
  "priority": 50,
  "allocations": [
    {
      "allocation_id": "c7da9579-d226-3ce3-833c-3211e98c18d9",
      "job_id": "bone-ml-training-001",
      "task_name": "training-group",
      "status": "running",
      "node_id": "d4ef94c9-5613-6017-253f-018c4f02d5b0",
      "node_name": "onyxcortex",
      "cpu_used_mhz": 7200,
      "memory_used_mb": 12800,
      "uptime_seconds": 324
    }
  ],
  "create_index": 41,
  "modify_index": 45
}
```

**Statuts possibles**:
- `pending`: Job créé, en attente d'allocation
- `running`: Job en exécution
- `complete`: Job terminé avec succès
- `dead`: Job arrêté ou échoué
- `failed`: Job échoué avec erreur
- `lost`: Allocation perdue

---

### POST /api/nomad/jobs/{job_id}/stop
Arrête un job en cours d'exécution.

**Response**:
```json
{
  "status": "stopped",
  "job_id": "bone-ml-training-001"
}
```

---

### GET /api/nomad/gpu-status
Récupère l'état des GPUs par nœud (occupation, availability).

**Response**:
```json
[
  {
    "node_id": "d4ef94c9-5613-6017-253f-018c4f02d5b0",
    "node_name": "onyxcortex",
    "num_gpus": 1,
    "available_gpus": 0,
    "in_use": ["bone-ml-001"]
  },
  {
    "node_id": "924e46c2-c342-e2d6-869b-d374aae530aa",
    "node_name": "OnyxPoint",
    "num_gpus": 1,
    "available_gpus": 1,
    "in_use": []
  },
  {
    "node_id": "08af0f22-8fd5-11b4-59ea-7b59cd84aa4e",
    "node_name": "onyxglia",
    "num_gpus": 0,
    "available_gpus": 0,
    "in_use": []
  }
]
```

**Utilisé pour**:
- Vérifier disponibilité GPU avant soumettre job
- Déboguer GPU allocation conflicts
- Monitorer saturation GPU

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

---

## Job Templates

Les job templates sont des scripts Python autonomes exécutables via Ray Jobs API. Ils sont stockés dans `jobs/` et peuvent être soumis via `POST /api/jobs`.

### bone-recognition Training (`jobs/bone-recognition/train_efficientnet.py`)

Entraîne EfficientNet-B0 avec curriculum learning multi-task.

**Phases** :
- Phase A : Pre-training angle (self-supervised, 20 epochs)
- Phase B : Supervised multi-task training (classification, density, landmarks, triplet loss, 50 epochs)

**Soumettre Phase A (pretrain only)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-pretrain-'$(date +%s)'",
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
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Soumettre Phase B (full training A + B)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-train-'$(date +%s)'",
    "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATA_DIR": "/opt/onyx/skills/bone-recognition/data/processed",
        "CHECKPOINT_DIR": "/opt/onyx/skills/ml-compute/models/bone-recognition",
        "PHASE": "train",
        "EPOCHS": "50",
        "BATCH_SIZE": "16",
        "LEARNING_RATE": "1e-4"
      }
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Env vars** : DATA_DIR (required), CHECKPOINT_DIR, PHASE (pretrain|train), EPOCHS, BATCH_SIZE, LEARNING_RATE, DEVICE

Voir `jobs/bone-recognition/README.md` pour docs complètes.

### bone-annotator Training (`jobs/bone-annotator/train_yolo.py`)

Entraîne YOLOv8 pour la détection d'objets (bone annotation).

**Soumettre YOLOv8m training (medium model, ~100 epochs)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-yolo-'$(date +%s)'",
    "entrypoint": "python jobs/bone-annotator/train_yolo.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml",
        "MODEL_BASE": "yolov8m.pt",
        "EPOCHS": "100",
        "BATCH_SIZE": "16",
        "LEARNING_RATE": "0.001",
        "ML_MODELS_DIR": "/opt/onyx/skills/bone-ml/models"
      }
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Soumettre YOLOv8n training (nano model, fast/cheap)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-yolo-quick-'$(date +%s)'",
    "entrypoint": "python jobs/bone-annotator/train_yolo.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml",
        "MODEL_BASE": "yolov8n.pt",
        "EPOCHS": "30",
        "BATCH_SIZE": "32",
        "ML_MODELS_DIR": "/opt/onyx/skills/bone-ml/models"
      }
    },
    "submit_kwargs": {"num_cpus": 4, "num_gpus": 1, "memory": 8000000000}
  }'
```

**Env vars** : DATASET_YAML (required), MODEL_BASE, EPOCHS, IMGSZ, BATCH_SIZE, LEARNING_RATE, DEVICE, ML_MODELS_DIR

Voir `jobs/bone-annotator/README.md` pour docs complètes et guide de sélection du modèle.

### bone-ml Multitask Training (`jobs/bone-ml/train_multitask.py`)

Entraîne un Dual-Head U-Net pour segmentation de zones anatomiques + landmarks heatmaps.

**Soumettre Dual-Head U-Net training (humerus, ResNet34)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-multitask-humerus-'$(date +%s)'",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "humerus",
        "EPOCHS": "100",
        "BATCH_SIZE": "4",
        "IMG_SIZE": "1408",
        "ENCODER_NAME": "resnet34",
        "DEVICE": "0",
        "ML_MODELS_DIR": "/mnt/ml-store/models",
        "PG_PASSWORD": "vault-password",
        "SOURCE_FILTER": "manual,corrected_ml"
      }
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Soumettre fine-tuning (ResNet50, parent model)** :
```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-finetune-femur-'$(date +%s)'",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "femur",
        "EPOCHS": "50",
        "BATCH_SIZE": "2",
        "ENCODER_NAME": "resnet50",
        "GENERATION": "2",
        "PARENT_MODEL": "/mnt/ml-store/models/femur_multitask_gen1_best.pt",
        "LEARNING_RATE": "0.00005",
        "PG_PASSWORD": "vault-password"
      }
    },
    "submit_kwargs": {"num_cpus": 12, "num_gpus": 1, "memory": 24000000000}
  }'
```

**Env vars** : BONE_TYPE, EPOCHS, BATCH_SIZE, IMG_SIZE, LEARNING_RATE, ENCODER_NAME, DEVICE, ML_MODELS_DIR, ML_RUNS_DIR, GENERATION, PARENT_MODEL (optional), LABEL_GENERATOR_URL, PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD (required)

Voir `jobs/bone-ml/README.md` pour docs complètes, guide des encodeurs, et exemple pipeline complet.

### SAM (Segment Anything Model) - Docker Service + Proxy

Déploie Segment Anything Model (vit_b) en tant que service Docker sur OnyxCortex avec proxy via ml-compute.

**⚠️ CRITICAL: GPU Resource Management**
- OnyxCortex a 1 GPU (RTX 4070 SUPER, 12GB VRAM)
- SAM Docker container réserve le GPU exclusivement
- Les jobs de training sont BLOQUÉS tant que SAM tourne
- **Stratégie**: Start SAM → Annotate → Stop SAM → Launch training

#### Deployment

Construire et lancer SAM Docker sur OnyxCortex:

```bash
# SSH sur OnyxCortex (10.0.0.26)
ssh onyx@10.0.0.26

# Build et start le container
cd /opt/onyx/skills/ml-compute
bash docker/build_and_run_sam.sh

# Vérifier que SAM est actif
docker ps | grep sam-service
curl http://10.0.0.26:9470/health
```

#### GET /api/serve/sam/status
**Vérifier l'état de SAM via proxy ml-compute**

```bash
curl -X GET http://10.0.0.44:9469/api/serve/sam/status
```

**Response** (SAM running):
```json
{
  "status": "healthy",
  "service": "sam-vit-b"
}
```

**Response** (SAM not running):
```json
{
  "status": "unhealthy",
  "error": "Connection refused"
}
```

#### GET /api/serve/sam/ready
**Vérifier la disponibilité de SAM**

```bash
curl -X GET http://10.0.0.44:9469/api/serve/sam/ready
```

**Response**:
```json
{
  "status": "ready"
}
```

#### POST /api/serve/sam/interact
**Utiliser SAM pour la segmentation interactive**

```bash
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image_or_array",
    "positive_points": [[x1, y1], [x2, y2]],
    "negative_points": [[x3, y3]]
  }'
```

**Request**:
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "positive_points": [[100, 100], [200, 200]],
  "negative_points": [[150, 150]]
}
```

**Response**:
```json
{
  "mask": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "area": 12345,
  "status": "success",
  "image_shape": [1080, 1920, 3]
}
```

**Latence**: 500-1000ms par prédiction

#### GET /api/serve/sam/info
**Spécifications SAM et resource requirements**

```bash
curl -X GET http://10.0.0.44:9469/api/serve/sam/info
```

**Response**:
```json
{
  "service": "SAM (Segment Anything Model)",
  "model": "vit_b",
  "backend": "Docker",
  "host": "10.0.0.26",
  "port": 9470,
  "endpoint": "http://10.0.0.26:9470/api/interact",
  "gpu_reserved": 1.0,
  "vram_required_gb": 10,
  "vram_available_onyxcortex_gb": 12,
  "inference_latency_ms": "500-1000",
  "status_endpoint": "http://10.0.0.26:9470/health"
}
```

#### Stopping SAM

```bash
# Stop le container (libère le GPU)
docker stop sam-service

# Redémarrer
docker start sam-service

# Nettoyer complètement
docker rm -f sam-service
docker rmi onyx/sam:latest
```

**Notes**:
- Modèle : ~/sam-gpu/sam_vit_b_01ec64.pth (375MB, 10GB VRAM requis)
- OnyxCortex : RTX 4070 SUPER 12GB ✅ Optimal
- OnyxPoint : T1000 8GB ❌ Insuffisant (CUDA OOM garanti)
- Image max recommandée : 1024x1024

Voir `jobs/sam/README.md` pour docs complètes et workflow CVAT integration.

---

## Updates

### [v0.1.47] 2026-08-22
- ✅ Ray cluster avec 2 workers (OnyxSoma head + OnyxCortex GPU)
- ✅ NFS volumes montés dans ray-head et ray-worker containers
- ✅ Jobs Ray testés avec accès NFS (/mnt/ml-store, /mnt/bonestore)
- ✅ SAM (Segment Anything) deployment via Ray Serve
- ✅ Fixed: asyncpg.connect() dans bone-ml/train_multitask.py (server_settings, ssl=False)

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
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml"
      }
    },
    "submit_kwargs": {"num_gpus": 1, "num_cpus": 4, "memory": 16000000000}
  }'

# Lister les jobs en cours
curl -X GET http://10.0.0.44:9469/api/jobs?status=RUNNING

# État des workers
curl -X GET http://10.0.0.44:9469/api/nodes | jq .

# Lister les modèles disponibles
curl -X GET http://10.0.0.44:9469/api/models
```
