# ml-compute - Architecture

## Vue d'ensemble

**ml-compute** est un orchestrateur ML centralisé basé sur Ray, déployé sur **OnyxSoma** comme Ray head node. Il fournit une API FastAPI pour soumettre des jobs training/inférence, monitorer les workers GPU/CPU distants, et servir des modèles via Ray Serve.

## Architecture Cluster Ray

```
OnyxSoma (10.0.0.44:9469) — Head Node
├── FastAPI wrapper (:9469)
├── Ray Head (:6379, GCS)
├── Ray Dashboard (:8265)
└── Ray Serve (:8000)

Workers distants (Docker rayproject/ray:2.35.0-py312, --network host)
├── OnyxPoint (10.0.0.86)
│   └── GPU Worker (i5-10400, T1000 8GB, num_cpus=10, num_gpus=1, 23GB RAM)
├── Glia (10.0.0.8)
│   └── CPU Worker (2x Xeon E5-2630, num_cpus=20, 47GB RAM, --shm-size=20g)
└── Axon (10.0.0.21)
    └── CPU Worker (num_cpus=4, Grobid tasks) — non connecté
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
├── jobs/                       # Job templates pré-configurés
│   ├── bone-annotator/
│   │   ├── train_yolo.py       # Training YOLO
│   │   └── predict_batch.py    # Batch inference
│   │
│   └── bone-recognition/       # Migré depuis bone-recognition skill
│       ├── train_efficientnet.py
│       ├── build_shape_model.py
│       └── data/
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

## Dépendances

| Package | Version | Usage |
|---------|---------|-------|
| `ray[default,serve]` | 2.35.0 | Cluster + serving |
| `fastapi` | 0.104.1 | API wrapper |
| `torch`, `torchvision` | 2.1.1 | ML training |
| `ultralytics` | 8.0.220 | YOLO training/inference |
| `onyx-sdk` | 2.1.0 | Intégration Redis/Events |

## Cycle de développement

1. ✅ Docker Compose avec Ray head node
2. ✅ FastAPI wrapper (main.py) + health/nodes endpoints
3. ✅ Module jobs: proxy Ray Jobs API
4. ✅ Workers Ray: OnyxPoint (GPU) et Glia (CPU) connectés via Docker
5. ✅ Module serve: gestion deployments Ray Serve (Dashboard HTTP API, Pydantic models, 13 tests)
6. ⏳ Module models: listing des modèles
7. ⏳ Tests end-to-end: jobs training depuis bone-annotator
8. ⏳ Migration code training depuis bone-recognition

## Principes de développement

- **Modules < 300 lignes**: Chaque fichier service.py et routes.py reste compacts
- **Types explicites**: Annotations complètes (mypy --strict)
- **Docstrings Google**: Chaque fonction publique documentée
- **Tests unitaires**: Par module dans `modules/{nom}/tests/`
- **Async/await**: httpx pour HTTP, asyncio pour parallélisation
- **Pas de credentials en dur**: Tous les secrets via Vault
