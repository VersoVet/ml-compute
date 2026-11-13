# ml-compute - API

**Base URL** : `http://10.0.0.44:9469`

**Scope** : Orchestration training ML (Ray + GPU Allocator) sur le cluster GPU Onyx.

**Cluster GPU** :
- **OnyxCortex** (10.0.0.26) — RTX 4070S (12 Go) — **bone training primary** (priorité 1, SAM arrêtés, GPU 100% training)
- **OnyxTensor** (10.0.0.73) — 3 GPU (3080+4060+2060S, 26 Go) — training overflow (priorité 2)
- **OnyxSynth** (10.0.0.78) — 7 GPU (58 Go) — **LLM Qwen3-32B-Q8_0 DÉDIÉ** (hors Ray, port 8080)

SAM/MedSAM est gere par bone-annotator (voir bone-annotator/API.md).

---

## Health & Status

### GET /health
Verifie la sante du cluster Ray et la connectivite aux workers.

```bash
curl http://10.0.0.44:9469/health
```

**Response**:
```json
{
  "status": "healthy",
  "ray_cluster": {
    "head_node": "10.0.0.44",
    "port": 6380,
    "status": "running",
    "workers_connected": 3
  },
  "timestamp": "2026-08-24T12:00:00Z"
}
```

### GET /ready
Verification de disponibilite des dependances.

```bash
curl http://10.0.0.44:9469/ready
```

---

## Jobs API

### POST /api/jobs
Soumet un job Ray pour training. Passe par le **GPU Allocator** : si un GPU est libre, le job est soumis a Ray directement (SUBMITTED) ; sinon il est mis en file d'attente FIFO (QUEUED) et dispatche automatiquement quand un slot se libere.

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "yolo-training-001",
    "entrypoint": "python jobs/bone-annotator/train_yolo.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "DATASET_YAML": "/opt/onyx/skills/bone-ml/datasets/current/dataset.yaml",
        "EPOCHS": "100"
      }
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Response** (202 Accepted — GPU libre, job soumis a Ray):
```json
{
  "job_id": "raysubmit_abc123",
  "status": "SUBMITTED",
  "name": "yolo-training-001"
}
```

**Response** (202 Accepted — GPU occupee, job en file):
```json
{
  "job_id": null,
  "queue_id": "queue_xyz789",
  "status": "QUEUED",
  "name": "yolo-training-001",
  "queue_position": 2
}
```

### GET /api/jobs
Liste les jobs avec filtres optionnels.

**Query Parameters**: `status` (SUBMITTED/RUNNING/SUCCEEDED/FAILED), `limit` (defaut: 100)

```bash
curl http://10.0.0.44:9469/api/jobs?status=RUNNING
```

### GET /api/jobs/{job_id}
Statut detaille et logs d'un job.

```bash
curl http://10.0.0.44:9469/api/jobs/{job_id}
```

**Response**:
```json
{
  "job_id": "raysubmit_abc123",
  "name": "yolo-training-001",
  "status": "RUNNING",
  "submission_time": "2026-08-24T12:00:00Z",
  "start_time": "2026-08-24T12:00:10Z",
  "logs_tail": "[2026-08-24 12:01:00] Epoch 1/100..."
}
```

### DELETE /api/jobs/{job_id}
Arrete un job.

```bash
curl -X DELETE http://10.0.0.44:9469/api/jobs/{job_id}
```

---

## Nodes API

### GET /api/nodes
Etat des workers Ray (GPU, CPU, RAM).

```bash
curl http://10.0.0.44:9469/api/nodes
```

**Response**:
```json
{
  "nodes": [
    {
      "node_name": "onyxcortex",
      "node_ip": "10.0.0.26",
      "resources": {"CPU": 16.0, "GPU": 1.0, "memory": 46000000000},
      "status": "alive"
    }
  ],
  "cluster_status": "healthy"
}
```

### GET /api/nodes/summary
Resume agrege des ressources cluster avec utilisation %.

```bash
curl http://10.0.0.44:9469/api/nodes/summary
```

---

## GPU Allocator API

Allocation exclusive des GPUs avec file d'attente FIFO. Garantit qu'un seul job s'execute par GPU (prevention conflits CUDA). Le background worker detecte les zombies et auto-release les jobs termines.

### GET /api/gpu-allocator/status
Etat complet de tous les slots GPU, file d'attente, et resume.

```bash
curl http://10.0.0.44:9469/api/gpu-allocator/status
```

**Response**:
```json
{
  "slots": [
    {
      "gpu_id": "cortex-0",
      "node": "OnyxCortex",
      "gpu_name": "RTX 4070 SUPER 12Go",
      "status": "busy",
      "current_job_id": "raysubmit_abc123",
      "acquired_at": "2026-11-05T10:00:00Z"
    },
    {
      "gpu_id": "tensor-0",
      "node": "OnyxTensor",
      "gpu_name": "RTX 3080 10Go",
      "status": "free",
      "current_job_id": null,
      "acquired_at": null
    }
  ],
  "queue": [
    {
      "queue_id": "queue_xyz789",
      "job_name": "yolo-training-002",
      "queued_at": "2026-11-05T10:05:00Z",
      "position": 1,
      "num_gpus": 1
    }
  ],
  "summary": {
    "slots_total": 4,
    "slots_free": 3,
    "slots_busy": 1,
    "queue_depth": 1
  }
}
```

### POST /api/gpu-allocator/release/{job_id}
Liberation manuelle d'un slot (escape hatch si le job est zombie et non detecte automatiquement).

```bash
curl -X POST http://10.0.0.44:9469/api/gpu-allocator/release/raysubmit_abc123
```

**Response**:
```json
{
  "success": true,
  "gpu_id": "cortex-0",
  "message": "Slot cortex-0 released for job raysubmit_abc123"
}
```

### DELETE /api/gpu-allocator/queue/{queue_id}
Annule un job en attente dans la file FIFO.

```bash
curl -X DELETE http://10.0.0.44:9469/api/gpu-allocator/queue/queue_xyz789
```

**Response**:
```json
{
  "success": true,
  "queue_id": "queue_xyz789",
  "message": "Queued job queue_xyz789 cancelled"
}
```

---

## Serve API

### GET /api/serve/deployments
Liste les applications Ray Serve deployees.

```bash
curl http://10.0.0.44:9469/api/serve/deployments
```

### GET /api/serve/status
Statut global de Ray Serve.

### POST /api/serve/deploy
Deploie un modele d'inference via Ray Serve.

```bash
curl -X POST http://10.0.0.44:9469/api/serve/deploy \
  -H "Content-Type: application/json" \
  -d '{"name": "yolo-bones", "type": "yolo", "num_replicas": 1, "num_gpus": 1}'
```

### POST /api/serve/undeploy
Retire une application Ray Serve.

```bash
curl -X POST http://10.0.0.44:9469/api/serve/undeploy \
  -H "Content-Type: application/json" \
  -d '{"name": "yolo-bones"}'
```

### POST /api/serve/predict/{app_name}
Envoie une requete d'inference a une application Ray Serve deployee.

```bash
curl -X POST http://10.0.0.44:9469/api/serve/predict/bone_rotation_app \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/mnt/bonestore/frame_001.png", "options": {}}'
```

**Response**:
```json
{
  "app_name": "bone_rotation_app",
  "result": {"rotation_degrees": 12.4, "confidence": 0.91},
  "duration_ms": 143.2
}
```

### GET /api/serve/deployments/{name}/status
Statut detaille d'une application Ray Serve.

```bash
curl http://10.0.0.44:9469/api/serve/deployments/bone_rotation_app/status
```

**Response**:
```json
{
  "name": "bone_rotation_app",
  "status": "RUNNING",
  "num_replicas": 1,
  "num_gpus_per_replica": 1,
  "last_deployed": "2026-11-05T09:00:00Z"
}
```

---

## Compute Backends API

API unifiee pour soumettre des jobs ML sur differents backends (local, Lightning AI, Kaggle).
Les skills clients n'ont pas besoin de savoir quel backend execute le job.

### GET /api/backends
Liste tous les backends avec disponibilite et GPU.

```bash
curl http://10.0.0.44:9469/api/backends
```

**Response**:
```json
[
  {
    "name": "Local Ray Cluster",
    "type": "local",
    "available": true,
    "gpu_types": ["RTX 4070 SUPER 12GB", "T1000 8GB"],
    "free_quota": "Unlimited (on-premise)",
    "status_detail": "Ray cluster healthy"
  },
  {
    "name": "Lightning AI",
    "type": "lightning",
    "available": true,
    "gpu_types": ["Tesla T4 16GB"],
    "free_quota": "~22h GPU/mois",
    "status_detail": "Studio 'onyx-ml-worker' (stopped)"
  },
  {
    "name": "Kaggle Notebooks",
    "type": "kaggle",
    "available": true,
    "gpu_types": ["Tesla T4 16GB"],
    "free_quota": "30h GPU/semaine",
    "status_detail": "User: versovet"
  }
]
```

### POST /api/compute/submit
Soumet un job ML. Backend auto-selectionne (local > lightning > kaggle) ou explicite.

```bash
# Auto-select backend
curl -X POST http://10.0.0.44:9469/api/compute/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "yolo-test",
    "entrypoint": "python train.py",
    "gpu_required": true,
    "env_vars": {"EPOCHS": "3", "BATCH_SIZE": "16"}
  }'

# Forcer Lightning AI
curl -X POST http://10.0.0.44:9469/api/compute/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "yolo-test",
    "entrypoint": "python train.py",
    "backend": "lightning",
    "gpu_required": true
  }'
```

**Response**:
```json
{
  "job_id": "lightning-yolo-test-1724505600",
  "name": "yolo-test",
  "backend": "lightning",
  "status": "succeeded",
  "gpu": "Tesla T4",
  "duration_s": 27.7,
  "logs": "YOLO TRAINING DONE in 27.7s..."
}
```

**Backends disponibles** : `local`, `lightning`, `kaggle`

### GET /api/compute/{job_id}
Statut d'un job soumis via compute.

```bash
curl http://10.0.0.44:9469/api/compute/{job_id}
```

### GET /api/compute/{job_id}/logs
Logs d'execution d'un job.

```bash
curl http://10.0.0.44:9469/api/compute/{job_id}/logs
```

### POST /api/compute/{job_id}/stop
Arrete un job en cours.

```bash
curl -X POST http://10.0.0.44:9469/api/compute/{job_id}/stop
```

---

## Models API

### GET /api/models
Liste les modeles ML disponibles.

```bash
curl http://10.0.0.44:9469/api/models
```

**Response**:
```json
{
  "models": [
    {"id": "yolo-bones-v8.1", "type": "yolo", "size_mb": 250, "created": "2026-07-15T10:30:00Z"},
    {"id": "efficientnet-b0-bones", "type": "efficientnet", "size_mb": 85, "created": "2026-08-01T14:20:00Z"}
  ],
  "total": 2
}
```

---

## Job Templates

Scripts Python autonomes dans `jobs/`, soumis via `POST /api/jobs`.

### bone-recognition (`jobs/bone-recognition/train_efficientnet.py`)

EfficientNet-B0 curriculum learning multi-task.

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-pretrain-'$(date +%s)'",
    "entrypoint": "python jobs/bone-recognition/train_efficientnet.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {"DATA_DIR": "/data/processed", "PHASE": "pretrain", "EPOCHS": "20"}
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Env vars** : DATA_DIR (required), CHECKPOINT_DIR, PHASE (pretrain|train), EPOCHS, BATCH_SIZE, LEARNING_RATE

### bone-annotator (`jobs/bone-annotator/train_yolo.py`)

YOLOv8 detection d'objets.

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-yolo-'$(date +%s)'",
    "entrypoint": "python jobs/bone-annotator/train_yolo.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {"DATASET_YAML": "/data/dataset.yaml", "MODEL_BASE": "yolov8m.pt", "EPOCHS": "100"}
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Env vars** : DATASET_YAML (required), MODEL_BASE, EPOCHS, IMGSZ, BATCH_SIZE, ML_MODELS_DIR

### bone-ml (`jobs/bone-ml/train_multitask.py`)

Dual-Head U-Net (segmentation + landmarks).

```bash
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-multitask-'$(date +%s)'",
    "entrypoint": "python jobs/bone-ml/train_multitask.py",
    "runtime_env": {
      "working_dir": "/opt/onyx/skills/ml-compute",
      "env_vars": {
        "BONE_TYPE": "humerus", "EPOCHS": "100", "BATCH_SIZE": "4",
        "ENCODER_NAME": "resnet34", "PG_PASSWORD": "vault-password"
      }
    },
    "submit_kwargs": {"num_cpus": 8, "num_gpus": 1, "memory": 16000000000}
  }'
```

**Env vars** : BONE_TYPE, EPOCHS, BATCH_SIZE, IMG_SIZE, ENCODER_NAME, PG_PASSWORD (required), PARENT_MODEL (optional)

### bone-ml BoneSeg (`jobs/bone-ml/train_boneseg.py`)

Soumis par bone-ml (`POST /api/boneseg/train`). Entrypoint Ray :

```bash
python jobs/bone-ml/train_boneseg.py
```

**Env vars** : BONE_TYPE, EPOCHS, BATCH_SIZE, IMG_SIZE, BASE_MODEL, RUN_ID, RUN_NAME,
TIERS, PG_HOST/PORT/DB/USER/PASSWORD, LEARNING_RATE, WEIGHT_DECAY, ML_MODELS_DIR

**Sortie** : `{ML_MODELS_DIR}/{RUN_NAME}_best.pt` + update PG `boneseg_training_runs`

### bone-train BoneSeg (`jobs/bone-train/train_boneseg.py`)

Soumis par bone-train (`POST /api/boneseg/train`, port 8210). Contrat Ray :

```json
{
  "entrypoint": "python jobs/bone-train/train_boneseg.py",
  "runtime_env": {
    "working_dir": "/opt/onyx/skills/ml-compute",
    "py_modules": ["/opt/onyx/skills/bone-train"]
  },
  "submit_kwargs": {"num_gpus": 1}
}
```

Ontologie zones label-generator ; gate GOLD ≥ 50 côté bone-train.
A/B vs `jobs/bone-ml/train_boneseg.py` — voir `jobs/bone-train/README.md`.

**Env vars** : BONE_TYPE, EPOCHS, BATCH_SIZE, BASE_MODEL, RUN_NAME, TIERS,
PG_HOST/PORT/DB/USER/PASSWORD, LABEL_GENERATOR_URL, LEARNING_RATE, WEIGHT_DECAY,
ML_MODELS_DIR, BONESTORE_PATH

---

## SAM / MedSAM (HORS SCOPE runtime)

SAM/MedSAM pour segmentation interactive est gere par **bone-annotator**, directement sur OnyxCortex.

```
CVAT (OnyxSynapse) -> Nuclio -> SAM Docker (OnyxCortex:9470) [DIRECT]
```

Ne passe PAS par Ray ni l'API ml-compute. Voir `bone-annotator/API.md`.

Le code source legacy SAM a ete supprime de ml-compute. L'image `sam-inference` est geree par bone-annotator.

### Contrat CVAT `/api/embed` (serveur SAM :9470)

L'interactor CVAT exige `blob` **et** `shape` :

```json
{
  "blob": "<base64 embedding bytes>",
  "shape": [1, 256, 64, 64]
}
```

`SegmentationResponse` expose aussi `detail` pour les erreurs metier (ex: prompts manquants).

```bash
# Health SAM direct (OnyxCortex)
curl http://10.0.0.26:9470/health
```

---

## GPU Management API

Gestion de l'allocation GPU multi-cible. Permet de coordonner les GPU entre training et services d'inference.

**Targets actuelles** :
- `cortex` (defaut) — OnyxCortex RTX 4070S 12 Go — stop/start SAM+MedSAM2 pour training
- `tensor` — OnyxTensor 3× GPU (3080+4060+2060S) 26 Go — training dedié
- ~~`synth`~~ — **RETIRÉ** : OnyxSynth 7 GPU = 100% LLM Qwen3-32B (JAMAIS de training)

### GET /api/gpu/status
Etat actuel du GPU et des containers d'inference.

```bash
curl http://10.0.0.44:9469/api/gpu/status
```

**Response**:
```json
{
  "gpu_name": "NVIDIA GeForce RTX 4070 SUPER",
  "gpu_memory_used_mib": 6035,
  "gpu_memory_total_mib": 12282,
  "gpu_memory_free_mib": 6247,
  "mode": "inference",
  "containers": [
    {"name": "sam-gpu", "running": true, "gpu_mib": 0},
    {"name": "medsam2-gpu", "running": true, "gpu_mib": 0}
  ],
  "acquired_at": null
}
```

### POST /api/gpu/acquire
Arrete SAM et MedSAM2 pour liberer le GPU pour le training.

```bash
curl -X POST http://10.0.0.44:9469/api/gpu/acquire
```

**Response**:
```json
{
  "success": true,
  "mode": "training",
  "stopped_containers": ["sam-gpu", "medsam2-gpu"],
  "gpu_memory_free_mib": 11874,
  "message": "GPU acquired for training. Stopped 2 container(s). Free VRAM: 11874 MiB"
}
```

### POST /api/gpu/release
Relance SAM et MedSAM2 apres un training.

```bash
curl -X POST http://10.0.0.44:9469/api/gpu/release
```

**Response**:
```json
{
  "success": true,
  "mode": "inference",
  "started_containers": ["sam-gpu", "medsam2-gpu"],
  "message": "GPU released to inference. Started 2 container(s)."
}
```

---

## Updates

### [v0.4.0] 2026-11-05
- Module gpu_allocator : allocation exclusive GPU PostgreSQL + file d'attente FIFO
- Endpoints /api/gpu-allocator/status, /release/{job_id}, /queue/{queue_id}
- POST /api/jobs route desormais via gpu_allocator (retourne SUBMITTED ou QUEUED)
- Suppression module Nomad et endpoints /api/nomad/*
- Module serving : Ray Serve apps (base_app, bone_rotation_app)
- Nouveaux endpoints /api/serve/predict/{app_name} et /api/serve/deployments/{name}/status
- OnyxCortex passe en bone training primary (priorité 1, SAM arrêtés, 100% GPU training)
- OnyxTensor = overflow training (priorité 2)

### [v0.3.3] 2026-11-01
- Infrastructure GPU rigs : OnyxTensor (3 GPU, 26 Go) + OnyxSynth (7 GPU, 58 Go)
- LLM local Qwen3-32B-Q8_0 sur OnyxSynth via llama.cpp (6× 2060S, 10.2 tok/s)
- Service systemd `llm-server` (port 8080, API OpenAI compatible)
- Provider `onyx_synth` (model `onyx-qwen3-32b`) ajouté au LLM Router
- OnyxSynth GPU 0 (3080) disponible pour Ray, GPU 1-6 réservées LLM
- OnyxTensor : 3080 (PCIE1 x16) + 4060 + 2060S (risers x1)
- Nettoyage legacy SAM complet (jobs, config), fix tests async
- Compatibilité H510 BTC+ P1.60 documentée (Blackwell incompatible)

### [v0.3.0] 2026-10-27
- Module GPU management : acquire/release GPU sur OnyxCortex (stop/start SAM+MedSAM2)
- Endpoints /api/gpu/status, /api/gpu/acquire, /api/gpu/release
- Suppression modules legacy sam/ et serve_proxy/
- Restart cluster Ray (nouvelle session), NFS montes dans ray-head
- Retrait Glia du cluster (machine hors service)
- Install torch/torchvision/timm/blosc2 dans ray-worker

### [v0.2.7] 2026-10-04
- OnyxCortex ajouté dans la config workers

### [v0.2.4] 2026-08-30
- Job template `jobs/bone-ml/train_boneseg.py` pour entrainement BoneSegNet (bone-ml)

### [v0.2.3] 2026-08-27
- Fix SAM `/api/embed` : reponse `blob` + `shape` pour l'interactor CVAT
- `SegmentationResponse.detail` pour erreurs metier

### [v0.2.2] 2026-08-24
- Module compute_backends : interface unifiee multi-backend (local, Lightning AI, Kaggle)
- Nouveaux endpoints /api/backends et /api/compute/*
- Lightning AI T4 valide (YOLO 3 epochs en 27.7s)

### [v0.2.0] 2026-08-24
- Config YAML centralisee (plus d'IPs hardcodees)
- Code review cleanup (imports absolus, dead code supprime)
- Separation claire SAM/ml-compute documentee

### [v0.1.78] 2026-08-23
- Module Nomad complet (GPU orchestration)
- 5 modules, 32+ tests unitaires

### [v0.1.47] 2026-08-22
- Ray cluster avec workers (OnyxCortex GPU, Glia CPU)
- NFS volumes montes
- Job templates (bone-recognition, bone-annotator, bone-ml)
