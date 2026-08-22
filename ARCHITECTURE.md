# ml-compute - Architecture

## Vue d'ensemble

**ml-compute** est un **orchestrateur ML centralisé multi-couche** combinant:
1. **Nomad** — Orchestration des ressources GPU (allocation exclusive, anti-conflit)
2. **Ray** — Jobs training distribués sur workers
3. **FastAPI** — API unifiée pour soumettre jobs

**Architecture en 3 niveaux:**
1. **Nomad Cluster** — Gestion GPU + allocation ressources (OnyxSoma server + workers clients)
2. **Ray Cluster** — Exécution jobs ML (Ray head + workers conteneurisés)
3. **Skills** — Services métier (bone-ml, bone-annotator sur OnyxSynapse)
4. **Infrastructure** — Services transversaux (Axon embeddings, monitoring Prometheus/Grafana)

---

## Architecture Cluster Ray

### Ray Head Node (Administration)
```
OnyxSoma (10.0.0.44) — Ray Head Node + ml-compute API
├── FastAPI wrapper (:9469)          ← Soumettre jobs ML
├── Ray Head/GCS (:6380)             ← Orchestration
├── Ray Dashboard (:8265)            ← Visualisation cluster
└── Ray Serve (:8000)                ← Inference deployments
```

**Rôle**: Administration UNIQUEMENT — pas d'exécution de jobs training ici.

### Ray Workers (Exécution training)
```
ML Workers (Docker rayproject/ray:2.35.0-py312, NFS + Local storage)
├── OnyxCortex (10.0.0.26) — GPU Training ⚡⚡ (PRINCIPAL)
│   ├── Hardware: 16-core i7-10700KF, RTX 4070 SUPER 12GB, 46GB RAM
│   ├── Config: num_cpus=16, num_gpus=1, shm-size=10GB
│   ├── Local Storage: /data/ml (916 GB SSD) ← Training I/O optimized
│   │   ├── /data/ml/datasets   ← High-speed training data
│   │   ├── /data/ml/models     ← Fast model checkpoint I/O
│   │   ├── /data/ml/runs       ← Training outputs cache
│   │   └── /data/ml/training-cache ← Intermediate results
│   └── Usage: Bone-ml Dual-Head U-Net training (GPU-bound)
│
├── Glia (10.0.0.8) — CPU Training ⚡ (FALLBACK)
│   ├── Hardware: 2x Xeon E5-2630, 20 cores, 47GB RAM
│   ├── Config: num_cpus=20, num_gpus=0, shm-size=20GB
│   └── Usage: CPU-only jobs, fallback if Cortex busy
│
└── OnyxPoint (10.0.0.86) — GPU Training (OPTIONNEL)
    ├── Hardware: i5-10400, NVIDIA T1000 8GB, 23GB RAM
    ├── Config: num_cpus=10, num_gpus=1, shm-size=8GB
    └── Usage: Secondary GPU, inference, legacy workloads
```

**Volumes accessibles aux Ray workers**:
- **Local Storage (OnyxCortex only)**
  - `/data/ml` → High-speed training storage (916 GB, direct I/O)
  - Shareable via NFS to other skills for data transfer
- **NFS Volumes (tous les workers)**
  - `/mnt/ml-store` → datasets, models, runs (10.0.0.6:/srv/nas/ml)
  - `/mnt/bonestore` → images fluoroscopiques read-only (10.0.0.52:/srv/bones)

**Installation d'un nouveau worker**: Voir [INSTALLATION.md](./INSTALLATION.md#1-ray-worker-setup)

---

## Orchestration GPU via Nomad

### Problème résolu
**Conflit GPU critique**: Avant Nomad, OnyxCortex exécutait simultanément:
- **SAM Docker** (inference pour annotations) — réserve GPU 1
- **Ray Training Jobs** (bone-ml) — réserve GPU 1
→ **Crash CUDA: 2 processus sur 1 GPU = OOM + segfault**

### Solution: Nomad + Coordonnée GPU
**Nomad** (HashiCorp orchestrator) manage l'allocation GPU **au niveau OS**, garantissant:
- **Isolation GPU**: Chaque job (SAM ou Training) obtient des GPUs **exclusives**
- **Prévention de conflit**: Si SAM utilise GPU 1, Ray jobs attendent sa libération
- **Scheduling intelligent**: Nomad choisit le worker optimal en fonction des ressources libres

### Architecture Nomad
```
OnyxSoma (10.0.0.44) — Nomad Server
├── Raft consensus (leader automátique)
├── Job scheduler
├── State machine (allocation tracking)
└── HTTP API (:4646) ← ml-compute queries

Workers Nomad Clients (Rejisters au Server)
├── OnyxCortex (10.0.0.26) — Client + 1 GPU RTX 4070 SUPER
├── OnyxPoint (10.0.0.86) — Client + 1 GPU T1000 8GB
└── Glia (10.0.0.8) — Client (CPU-only)

Coordination SAM ↔ Ray:
┌─────────────────────────────────────────┐
│ SAM Annotation (Docker)                 │
│ ✓ Acquiert GPU via Nomad                │
│ Exécute inférence pendant 2-5 min        │
│ ✓ Libère GPU en fin                     │
└────────────────────┬────────────────────┘
                     │ GPU libre? (Nomad checks)
                     ▼
┌─────────────────────────────────────────┐
│ Ray Training Job soumis                 │
│ ✓ Nomad vérifie GPU disponible          │
│ ✓ Alloue GPU exclusif au job            │
│ Exécute training bone-ml pendant 1-2h   │
│ ✓ Libère GPU en fin                     │
└─────────────────────────────────────────┘
```

### Module Nomad dans ml-compute
```
src/modules/nomad/
├── service.py — NomadManager
│   ├── connect() / disconnect()
│   ├── submit_job(NomadJobRequest) → job_id
│   ├── get_job_status(job_id) → NomadJobStatus
│   ├── stop_job(job_id)
│   ├── get_cluster_status() → nodes_ready, gpus_total, gpus_available
│   └── get_gpu_status() → per-node GPU allocation
│
├── models.py — Pydantic Models
│   ├── NomadJobRequest (name, image, driver, num_gpus, env_vars, volumes)
│   ├── NomadJobStatus (status, allocations)
│   ├── GPUStatus (node_id, num_gpus, available_gpus, in_use)
│   └── NomadClusterStatus (nodes_ready, gpus_total, gpus_available, jobs_running)
│
└── routes.py — FastAPI Endpoints
    ├── GET /api/nomad/status → Cluster status
    ├── POST /api/nomad/jobs/submit → Submit job
    ├── GET /api/nomad/jobs/{job_id} → Job status
    ├── POST /api/nomad/jobs/{job_id}/stop → Stop job
    └── GET /api/nomad/gpu-status → GPU allocation per node
```

**Endpoints clés**:
```bash
# Cluster status (3 nœuds, 2 GPUs)
curl http://10.0.0.44:9469/api/nomad/status
# {"nodes_ready": 3, "gpus_total": 2, "gpus_available": 2, "jobs_running": 0}

# Soumettre un job avec GPU
curl -X POST http://10.0.0.44:9469/api/nomad/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bone-ml-training-001",
    "image": "rayproject/ray:2.35.0-py312",
    "driver": "docker",
    "constraints": [{"task_name": "training", "cpu_mhz": 8000, "memory_mb": 16384, "num_gpus": 1}],
    "command": "python /app/train.py",
    "env_vars": {"EPOCHS": "100", "BATCH_SIZE": "32"}
  }'

# GPU status (vérifie qui utilise les GPUs)
curl http://10.0.0.44:9469/api/nomad/gpu-status
# [
#   {"node_name": "onyxcortex", "num_gpus": 1, "available_gpus": 0, "in_use": ["bone-ml-001"]},
#   {"node_name": "onyxpoint", "num_gpus": 1, "available_gpus": 1, "in_use": []}
# ]
```

---

### Infrastructure Services (Hors Ray Cluster)
```
OnyxSynapse (10.0.0.59) — Bone Skills Hub
├── bone-ml (:9463)          ← Training orchestration
├── bone-annotator (:9464)   ← Annotation API
├── PostgreSQL (:5432)       ← Annotations + labels
├── Qdrant (:6333)          ← Vector search
└── CVAT                     ← Labeling interface

Axon (10.0.0.?) — Embeddings & Bibliography
├── Ollama axon (:11434)     ← Local embeddings (Qdrant)
└── Bibliography             ← Papers, articles indexing

Monitoring Infrastructure
├── Prometheus (:9090) — Metrics collection (OnyxSoma)
└── Grafana (:3000) — Visualisation (OnyxSoma)
    └── Scrapes: Node Exporter, GPU Exporter, Ray Dashboard
```

**Ces services ne font PAS partie du Ray cluster** — ils communiquent via API HTTP avec les Ray jobs.

---

## Ajouter un nouveau Worker ML au Cluster

**Procédure standardisée pour intégrer une nouvelle machine ML (GPU ou CPU):**

1. **Lire** [INSTALLATION.md — Section 1: Ray Worker Setup](./INSTALLATION.md#1-ray-worker-setup)
2. **Adapter les specs** pour votre machine (CPU cores, GPU count, RAM)
3. **Configurer NFS** (Section 1.5) — Monter `/mnt/ml-store` et `/mnt/bonestore`
4. **Installer Exporters** (Section 2) — Node Exporter + GPU Exporter si GPU
5. **Vérifier la connexion** (Section 1.4) — `curl http://10.0.0.44:9469/api/nodes`

**Résultat attendu** : Machine apparaît dans `ray status` et Prometheus scrape ses métriques dans Grafana.

**Template specs** pour différents types de machines:
```bash
# GPU Worker (comme OnyxCortex)
NUM_CPUS=16
NUM_GPUS=1
RAY_MEMORY=46000000000
--shm-size=10gb

# CPU Worker (comme Glia)
NUM_CPUS=20
NUM_GPUS=0
RAY_MEMORY=47000000000
--shm-size=20gb

# Lightweight GPU (comme OnyxPoint)
NUM_CPUS=10
NUM_GPUS=1
RAY_MEMORY=23000000000
--shm-size=8gb
```

---

## Modules

### 0. **nomad** (`src/modules/nomad/`) ⭐ NEW
Orchestration GPU via Nomad. Prévient les conflits GPU en garantissant allocation exclusive aux jobs.

**Fichiers**:
- `service.py`: NomadManager avec Nomad HTTP API client
- `models.py`: NomadJobRequest, NomadJobStatus, GPUStatus, NomadClusterStatus
- `routes.py`: Endpoints `/api/nomad/*`

**Endpoints**:
- `GET /api/nomad/status`: Cluster status (nodes ready, GPUs total/available)
- `POST /api/nomad/jobs/submit`: Submit job avec reservation GPU
- `GET /api/nomad/jobs/{job_id}`: Job status + allocations
- `POST /api/nomad/jobs/{job_id}/stop`: Stop job + libère GPU
- `GET /api/nomad/gpu-status`: GPU allocation per node (qui utilise quelle GPU)

**Intégration SAM**:
- SAM Docker démarre → acquiert GPU via Nomad
- Pendant SAM actif → Ray jobs voient GPU occupée
- SAM termine → libère GPU automatiquement
- Prochain Ray job → Nomad alloue GPU libérée

### 1. **jobs** (`src/modules/jobs/`)
Proxy vers Ray Jobs API. Gère la soumission, le suivi et l'arrêt des jobs ML.

**Fichiers**:
- `service.py`: Logique métier (submit_job, get_status, get_logs, delete_job)
- `routes.py`: Endpoints FastAPI (/api/jobs, /api/jobs/{id})

**Endpoints**:
- `POST /api/jobs`: Soumettre un job
- `GET /api/jobs`: Lister les jobs
- `GET /api/jobs/{id}`: Statut + logs
- `DELETE /api/jobs/{id}`: Arrêter un job

### 2. **serve** (`src/modules/serve/`)
Gestion des déploiements Ray Serve (modèles d'inférence). Implémentation complète via appels HTTP async (httpx) au Ray Dashboard REST API (port 8265), utilisant l'API Serve v2 (applications-based).

**Fichiers**:
- `service.py`: Logique métier via Ray Dashboard HTTP API (list_deployments, get_serve_status, deploy_model, undeploy_model, _resolve_import_path). Appels: GET/PUT/DELETE sur `/api/serve/applications/`.
- `routes.py`: Endpoints FastAPI (/api/serve/*) avec modeles Pydantic de validation (DeployRequest, UndeployRequest).
- `tests/test_serve.py`: 13 tests unitaires couvrant service et routes.

**Endpoints**:
- `GET /api/serve/deployments`: Lister les modèles servis (via GET /api/serve/applications/ sur Ray Dashboard)
- `GET /api/serve/status`: Statut global Ray Serve (nombre d'applications, proxy location)
- `POST /api/serve/deploy`: Deployer un modele (via PUT /api/serve/applications/ sur Ray Dashboard). Accepte un `DeployRequest` (name, type, model, num_replicas, num_gpus, gpu_memory_utilization). Retourne 202.
- `POST /api/serve/undeploy`: Retirer un modele (via DELETE /api/serve/applications/{name} sur Ray Dashboard). Accepte un `UndeployRequest` (name). Retourne 204.

### 3. **nodes** (`src/modules/nodes/`)
Monitoring des workers Ray (GPU, CPU, RAM, status).

**Fichiers**:
- `service.py`: Requête Ray Cluster API pour état des nodes
- `routes.py`: Endpoint GET /api/nodes

**Endpoint**:
- `GET /api/nodes`: Ressources par worker (name, num_cpus, num_gpus, memory)

### 4. **models** (`src/modules/models/`)
Listing et gestion des modèles ML disponibles (stockés dans /opt/onyx/skills/ml-compute/models/).

**Fichiers**:
- `service.py`: Scan filesystem pour modèles
- `routes.py`: Endpoint GET /api/models

**Endpoint**:
- `GET /api/models`: Modèles disponibles avec metadata

## Structure des répertoires

```
ml-compute/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI (~200 lignes)
│   ├── models.py               # Modèles Pydantic
│   │
│   └── modules/
│       ├── __init__.py
│       ├── nomad/
│       │   ├── __init__.py
│       │   ├── service.py      # Nomad orchestration client
│       │   ├── models.py       # Job + GPU status models
│       │   ├── routes.py       # FastAPI routes
│       │   └── tests/
│       │       └── test_nomad.py
│       │
│       ├── jobs/
│       │   ├── __init__.py
│       │   ├── service.py      # Ray Jobs API proxy
│       │   ├── routes.py       # FastAPI routes
│       │   └── tests/
│       │       └── test_jobs.py
│       │
│       ├── serve/
│       │   ├── __init__.py
│       │   ├── service.py      # Ray Serve management (Dashboard HTTP API)
│       │   ├── routes.py       # Routes + Pydantic models (DeployRequest, UndeployRequest)
│       │   └── tests/
│       │       └── test_serve.py  # 13 tests unitaires
│       │
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── service.py      # Node monitoring
│       │   ├── routes.py
│       │   └── tests/
│       │
│       └── models/
│           ├── __init__.py
│           ├── service.py      # Model registry
│           ├── routes.py
│           └── tests/
│
├── jobs/                       # Job templates Ray (soumis via /api/jobs)
│   ├── __init__.py
│   ├── bone-annotator/
│   │   ├── __init__.py
│   │   ├── train_yolo.py       # YOLOv8 training (ultralytics)
│   │   └── README.md            # Comment soumettre le job
│   │
│   ├── bone-recognition/       # EfficientNet-B0 training (Phase A+B)
│   │   ├── __init__.py
│   │   ├── train_efficientnet.py # BoneTrainer multi-task
│   │   └── README.md             # Comment soumettre le job
│   │
│   └── bone-ml/               # Dual-Head U-Net multitask training
│       ├── __init__.py
│       ├── train_multitask.py  # U-Net segmentation + landmarks
│       └── README.md            # Comment soumettre le job
│
├── models/                     # Stockage modèles entraînés
│   ├── bone-annotator/
│   └── bone-recognition/
│
├── docker-compose.yml          # Ray head + API
├── Dockerfile                  # FastAPI wrapper
├── manifest.json               # Config Forge
├── cron.json                   # Tasks de santé
├── backup.json                 # Stratégie sauvegarde
└── requirements.txt            # Dépendances Python
```

## Monitoring Stack

**Prometheus + Grafana** pour monitoring temps-réel du cluster Ray.

```
OnyxSoma (10.0.0.44) — Monitoring Central
├── Prometheus (:9090)
│   ├── Scrape interval: 15s
│   ├── Retention: 30 days
│   └── Scrapes les targets:
│       ├── node-exporter (:9100) sur tous les workers
│       ├── gpu-exporter (:9445) sur workers GPU
│       └── Ray Dashboard API (:8265)
│
└── Grafana (:3000)
    ├── Login: admin / PYjAtvTXDy6ZHRm
    └── Dashboards:
        ├── 1860 — Node Exporter Full (CPU, Memory, Disk, Network)
        ├── 7752 — NVIDIA GPU Metrics (GPU util, memory, temperature)
        └── 3662 — Prometheus Stats (health, scrape performance)
    
ML Workers — Metrics Export
├── OnyxCortex (10.0.0.26)
│   ├── Node Exporter (:9100) — Systemd service
│   └── GPU Exporter (:9445) — nvidia-smi script (every 15s)
│
├── Glia (10.0.0.8)
│   └── Node Exporter (:9100) — System metrics (no GPU)
│
└── OnyxPoint (10.0.0.86)
    ├── Node Exporter (:9100) — System metrics
    └── GPU Exporter (:9445) — GPU metrics (T1000 legacy)
```

**Accès Monitoring**:
- Prometheus: `http://10.0.0.44:9090` (queries, targets, alerts)
- Grafana: `http://10.0.0.44:3000` (dashboards, visualisation)

**Pour ajouter monitoring à un nouveau worker**: Voir [INSTALLATION.md — Section 2](./INSTALLATION.md#2-monitoring-exporters)

## Dépendances

| Package | Version | Usage |
|---------|---------|-------|
| `ray[default,serve]` | 2.35.0 | Cluster + serving |
| `fastapi` | 0.104.1 | API wrapper |
| `torch`, `torchvision` | 2.1.1 | ML training |
| `ultralytics` | 8.0.220 | YOLO training/inference |
| `onyx-sdk` | 2.1.0 | Intégration Redis/Events |

## Job Templates

### bone-recognition Training (`jobs/bone-recognition/train_efficientnet.py`)
Script Ray Job pour entraîner EfficientNet-B0 avec curriculum learning multi-task.
- **Phase A**: Pre-training angle (self-supervised, 20 epochs)
- **Phase B**: Supervised training (multi-task : classification, density, landmarks, triplet loss)
- Support DDP, AMP, MLflow tracking
- Paramètres via env vars : DATA_DIR, CHECKPOINT_DIR, PHASE, EPOCHS, BATCH_SIZE

### bone-annotator Training (`jobs/bone-annotator/train_yolo.py`)
Script Ray Job pour entraîner YOLOv8 détection d'objets.
- Modèles : yolov8n/s/m/l/x (configurable)
- Sauvegarde best.pt dans ML_MODELS_DIR
- Logging métriques (mAP50, mAP50-95)
- Paramètres via env vars : DATASET_YAML, MODEL_BASE, EPOCHS, BATCH_SIZE

### bone-ml Multitask Training (`jobs/bone-ml/train_multitask.py`)
Script Ray Job pour entraîner Dual-Head U-Net (segmentation + landmarks).
- **Segmentation Head**: Zones anatomiques (os)
- **Landmarks Head**: Gaussian heatmaps avec SGR (Segmentation-Guided Refinement)
- Encodeur partagé : ResNet34/50/Swin (pretrained ImageNet)
- Données depuis label-generator API + PostgreSQL (annotations validées)
- Support fine-tuning via PARENT_MODEL
- Paramètres via env vars : BONE_TYPE, EPOCHS, BATCH_SIZE, ENCODER_NAME, PG_PASSWORD, etc.

Soumettre via : `curl -X POST http://10.0.0.44:9469/api/jobs -d '{...}'`
(Voir `jobs/{skeleton}/README.md` pour exemples complets)

## Cycle de développement

1. ✅ Docker Compose avec Ray head node
2. ✅ FastAPI wrapper (main.py) + health/nodes endpoints
3. ✅ Module jobs: proxy Ray Jobs API
4. ✅ Workers Ray: OnyxPoint (GPU) et Glia (CPU) connectés via Docker
5. ✅ Module serve: gestion deployments Ray Serve (Dashboard HTTP API, Pydantic models, 13 tests)
6. ✅ Job templates Phase A: bone-recognition (EfficientNet) et bone-annotator (YOLO)
7. ⏳ Job templates Phase B: predict_batch, inference endpoints
8. ⏳ Tests end-to-end: soumettre jobs via /api/jobs

---

## Communication & Data Flow

### Ray Jobs Workflow
```
1. Utilisateur soumet un job via API
   POST /api/jobs
   ↓
2. ml-compute (OnyxSoma) envoie au Ray Head
   ↓
3. Ray Head distribue aux workers disponibles (OnyxCortex, Glia, OnyxPoint)
   ↓
4. Worker exécute le job dans un container Docker
   ├─ Accès NFS: /mnt/ml-store, /mnt/bonestore
   ├─ Accès PostgreSQL: label-generator API (OnyxSynapse:9466)
   └─ Accès Qdrant: vector search (OnyxSynapse:6333)
   ↓
5. Job logs + metrics retournés via /api/jobs/{id}
```

### Service Dependencies
```
Ray Workers ──httpx──> PostgreSQL (OnyxSynapse:5432)
                     ├─ Fetch validated annotations
                     └─ Store training metadata

Ray Workers ──httpx──> label-generator (OnyxSynapse:9466)
                     └─ Fetch training labels by bone type

Ray Workers ──httpx──> Qdrant (OnyxSynapse:6333)
                     └─ Vector search (if needed)

bone-ml (OnyxSynapse) ──http──> ml-compute API (OnyxSoma:9469)
                              └─ Submit training jobs to Ray

Monitoring ──scrape──> Node Exporter (:9100)
           ├─────────> GPU Exporter (:9445)
           └─────────> Ray Dashboard (:8265)
```

### NFS Access Pattern
**Tous les Ray workers doivent accéder aux mêmes volumes NFS** :
```
/mnt/ml-store  (read-write)
├── datasets/     ← Training data
├── models/       ← Pretrained models
└── runs/         ← Training outputs

/mnt/bonestore (read-only)
└── X-ray images  ← Fluoroscopic images
```

Ces volumes sont **bind-mountés dans les containers Docker** (voir `start-ray-worker.sh`).

---

## Principes de développement

- **Modules < 300 lignes**: Chaque fichier service.py et routes.py reste compacts
- **Types explicites**: Annotations complètes (mypy --strict)
- **Docstrings Google**: Chaque fonction publique documentée
- **Tests unitaires**: Par module dans `modules/{nom}/tests/`
- **Async/await**: httpx pour HTTP, asyncio pour parallélisation
- **Pas de credentials en dur**: Tous les secrets via Vault
- **NFS critical**: Tous les workers doivent avoir accès aux mêmes NFS volumes
- **Network access**: Ray workers peuvent appeler services externes via httpx
