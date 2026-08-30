# ml-compute - API

**Base URL** : `http://10.0.0.44:9469`

**Scope** : Orchestration training ML (Ray + Nomad). SAM/MedSAM est gere par bone-annotator (voir bone-annotator/API.md).

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
Soumet un job Ray pour training.

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

**Response** (202 Accepted):
```json
{
  "job_id": "raysubmit_abc123",
  "status": "SUBMITTED",
  "name": "yolo-training-001"
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

## Nomad Orchestration API

### GET /api/nomad/status
Statut global du cluster Nomad (nodes, GPUs, jobs).

```bash
curl http://10.0.0.44:9469/api/nomad/status
```

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

### POST /api/nomad/jobs/submit
Soumet un job a Nomad avec reservation GPU exclusive.

```bash
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-training-001",
    "job_type": "batch",
    "driver": "docker",
    "image": "rayproject/ray:2.35.0-py312",
    "command": "python /app/train_multitask.py",
    "constraints": [{"task_name": "training", "cpu_mhz": 8000, "memory_mb": 16384, "num_gpus": 1}],
    "env_vars": {"EPOCHS": "100", "BATCH_SIZE": "32"},
    "timeout_seconds": 7200
  }'
```

**Response** (202):
```json
{
  "status": "submitted",
  "job_id": "bone-ml-training-001",
  "evaluation_id": "c0e1bdd3-..."
}
```

### GET /api/nomad/jobs/{job_id}
Statut et allocations d'un job Nomad.

```bash
curl http://10.0.0.44:9469/api/nomad/jobs/{job_id}
```

### POST /api/nomad/jobs/{job_id}/stop
Arrete un job en cours.

```bash
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/{job_id}/stop
```

### GET /api/nomad/gpu-status
Etat des GPUs par noeud.

```bash
curl http://10.0.0.44:9469/api/nomad/gpu-status
```

**Response**:
```json
[
  {"node_name": "onyxcortex", "num_gpus": 1, "available_gpus": 0, "in_use": ["bone-ml-001"]},
  {"node_name": "OnyxPoint", "num_gpus": 1, "available_gpus": 1, "in_use": []},
  {"node_name": "onyxglia", "num_gpus": 0, "available_gpus": 0, "in_use": []}
]
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

---

## SAM / MedSAM (HORS SCOPE runtime)

SAM/MedSAM pour segmentation interactive est gere par **bone-annotator**, directement sur OnyxCortex.

```
CVAT (OnyxSynapse) -> Nuclio -> SAM Docker (OnyxCortex:9470) [DIRECT]
```

Ne passe PAS par Ray ni l'API ml-compute. Voir `bone-annotator/API.md`.

Le **code source** du serveur Docker reste dans `jobs/sam/sam_server.py` (image `sam-inference:v3-multimodel`).

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

## Updates

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
