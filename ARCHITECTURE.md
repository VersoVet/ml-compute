# ml-compute - Architecture

## Vue d'ensemble

**ml-compute** est un orchestrateur ML centralisé basé sur Ray. Le **Ray Head** est déployé sur **OnyxSoma** (machine d'administration système), qui fournit une API FastAPI pour soumettre des jobs training/inférence aux workers ML distants (OnyxCortex GPU, Glia CPU), monitorer les ressources, et servir des modèles via Ray Serve.

## Architecture Cluster Ray

```
OnyxSoma (10.0.0.44) — Administration & Ray Head (Orchestration Only)
├── FastAPI wrapper (:9469)
├── Ray Head Node (:6380 GCS)
├── Ray Dashboard (:8265)
└── Ray Serve (:8000)

ML Workers (Docker rayproject/ray:2.35.0-py312, --network host)
├── OnyxCortex (10.0.0.26) — GPU Training ⚡
│   └── 16-core i7-10700KF @ 3.8GHz, RTX 4070 SUPER 12GB, num_cpus=16, num_gpus=1, 46GB RAM, shm-size=10GB
│       ├─ bone-ml multitask training (Swin-T @1340×1340)
│       └─ GPU jobs preferred
└── Glia (10.0.0.8) — CPU Training
    └── 2x Xeon E5-2630, num_cpus=20, 47GB RAM, --shm-size=20g
        ├─ CPU-bound jobs
        └─ Fallback for GPU jobs if Cortex busy

Infrastructure Services (Not in Ray cluster)
├── Axon (10.0.0.21)
│   ├── Grobid (PDF extraction)
│   └── Ollama (Embedding models for bibliography)
└── OnyxPoint (10.0.0.86) — Legacy/Archive
    └── i5-10400, NVIDIA T1000 8GB (available if needed)
```

## Modules

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

**Prometheus + Grafana** pour monitoring du cluster Ray (voir `monitoring/README.md`).

```
OnyxSoma (10.0.0.44)
├── Prometheus (:9090)
│   └── Scrapes: node-exporter (9100), gpu-exporter (9445), Ray Dashboard (8265)
└── Grafana (:3000)
    └── Visualizes Prometheus metrics + Ray cluster health
    
ML Workers
├── OnyxCortex (10.0.0.26)
│   ├── Node Exporter (:9100) — CPU, Memory, Disk, Network
│   └── NVIDIA GPU Exporter (:9445) — GPU util, memory, temperature
├── Glia (10.0.0.8)
│   └── Node Exporter (:9100) — CPU, Memory, Disk, Network
└── OnyxPoint (10.0.0.86)
    ├── Node Exporter (:9100) — CPU, Memory, Disk, Network
    └── NVIDIA GPU Exporter (:9445) — GPU util, memory, temperature
```

**Accès** :
- Prometheus: `http://10.0.0.44:9090`
- Grafana: `http://10.0.0.44:3000` (admin/admin)

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

## Principes de développement

- **Modules < 300 lignes**: Chaque fichier service.py et routes.py reste compacts
- **Types explicites**: Annotations complètes (mypy --strict)
- **Docstrings Google**: Chaque fonction publique documentée
- **Tests unitaires**: Par module dans `modules/{nom}/tests/`
- **Async/await**: httpx pour HTTP, asyncio pour parallélisation
- **Pas de credentials en dur**: Tous les secrets via Vault
