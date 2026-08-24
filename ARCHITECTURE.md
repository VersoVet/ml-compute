# ml-compute - Architecture

## Vue d'ensemble

**ml-compute** est un **orchestrateur ML centralisé** :
1. **Compute Backends** — Interface unifiee multi-backend (local Ray, Lightning AI, Kaggle)
2. **Ray** — Soumission et monitoring de jobs training distribues sur workers GPU/CPU
3. **Nomad** — Allocation exclusive des GPUs (anti-conflit CUDA entre jobs)
4. **FastAPI** — API unifiee pour les skills metier (bone-ml, bone-annotator, bone-recognition)

**Hors scope** : SAM/MedSAM inference et CVAT sont geres directement par **bone-annotator** sur OnyxCortex, sans passer par Ray ni ml-compute (voir section "Separation SAM").

---

## Architecture Cluster

### Ray Head Node (Administration)
```
OnyxSoma (10.0.0.44) — Ray Head Node + ml-compute API
├── FastAPI wrapper (:9469)          <- Soumettre jobs ML
├── Ray Head/GCS (:6380)             <- Orchestration
├── Ray Dashboard (:8265)            <- Visualisation cluster
└── Ray Serve (:8000)                <- Inference deployments
```

**Role**: Administration UNIQUEMENT — pas d'execution de jobs training ici.

### Ray Workers (Execution training)
```
OnyxCortex (10.0.0.26) — GPU Training PRINCIPAL
├── Hardware: 16-core i7-10700KF, RTX 4070 SUPER 12GB, 46GB RAM
├── Config: num_cpus=16, num_gpus=1, shm-size=10GB
├── Local Storage: /data/ml (916 GB SSD) <- Training I/O optimized
└── Usage: bone-ml Dual-Head U-Net training (GPU-bound)

Glia (10.0.0.8) — CPU Training FALLBACK
├── Hardware: 2x Xeon E5-2630, 20 cores, 47GB RAM
├── Config: num_cpus=20, num_gpus=0, shm-size=20GB
└── Usage: CPU-only jobs, fallback if Cortex busy

OnyxPoint (10.0.0.86) — GPU Training SECONDAIRE
├── Hardware: i5-10400, NVIDIA T1000 8GB, 23GB RAM
├── Config: num_cpus=10, num_gpus=1, shm-size=8GB
└── Usage: Jobs GPU legers, YOLO inference
```

### Volumes NFS (tous les workers)
```
/mnt/ml-store  (read-write) — datasets, models, runs (10.0.0.6:/srv/nas/ml)
/mnt/bonestore (read-only)  — images fluoroscopiques (10.0.0.52:/srv/bones)
```

---

## Orchestration GPU via Nomad

### Probleme resolu
**Conflit GPU critique**: Plusieurs jobs GPU (training, inference) lances simultanément sur le meme GPU = CUDA OOM crash.

### Solution
**Nomad** gere l'allocation GPU au niveau OS :
- **Isolation GPU**: Chaque job obtient des GPUs exclusives
- **Prevention de conflit**: Si un job utilise le GPU, les suivants attendent
- **Scheduling intelligent**: Nomad choisit le worker optimal

### Architecture Nomad
```
OnyxSoma (10.0.0.44) — Nomad Server
├── HTTP API (:4646)
├── Job scheduler
└── GPU allocation tracking

Workers Nomad Clients
├── OnyxCortex (10.0.0.26) — 1 GPU RTX 4070 SUPER
├── OnyxPoint (10.0.0.86)  — 1 GPU T1000 8GB
└── Glia (10.0.0.8)        — CPU-only
```

---

## Separation SAM / ml-compute

### Avant (legacy)
```
CVAT -> Nuclio -> ml-compute API -> Ray Serve -> SAM Docker (OnyxCortex)
```
Problemes : latence elevee, complexite, conflit GPU avec training jobs.

### Maintenant (actuel)
```
CVAT -> Nuclio -> SAM/MedSAM Docker (OnyxCortex:9470) [DIRECT]
```
- **SAM/MedSAM** tourne comme container Docker **autonome** sur OnyxCortex
- Gere par **bone-annotator** (start/stop/status)
- **Ne passe PAS par Ray** ni par ml-compute
- La coordination GPU entre SAM et training est manuelle (stop SAM -> launch training)
- Voir `bone-annotator/API.md` pour les endpoints SAM

### Pourquoi cette separation
1. **Simplicite** : SAM n'a pas besoin de l'orchestration Ray (c'est un service, pas un job)
2. **Latence** : Appel direct OnyxCortex vs proxy via OnyxSoma
3. **Responsabilite claire** : bone-annotator gere l'annotation (CVAT + SAM), ml-compute gere le training

---

## Modules

### 1. **jobs** (`src/modules/jobs/`)
Proxy vers Ray Jobs API. Soumission, suivi et arret des jobs ML.

- `service.py`: submit_job, get_status, get_logs, delete_job
- `routes.py`: POST/GET/DELETE /api/jobs
- Tests: 9 tests unitaires

### 2. **nodes** (`src/modules/nodes/`)
Monitoring des workers Ray (GPU, CPU, RAM, status).

- `service.py`: query_nodes, get_resource_summary
- `routes.py`: GET /api/nodes, GET /api/nodes/summary
- Tests: 5 tests unitaires

### 3. **serve** (`src/modules/serve/`)
Gestion des deployments Ray Serve (modeles d'inference).

- `service.py`: deploy, undeploy, list_deployments, get_serve_status
- `routes.py`: GET/POST /api/serve
- Tests: 13 tests unitaires

### 4. **models** (`src/modules/models/`)
Registre des modeles ML disponibles sur le filesystem.

- `service.py`: scan_models, get_model_by_id
- `routes.py`: GET /api/models
- Tests: 5 tests unitaires

### 5. **nomad** (`src/modules/nomad/`)
Orchestration GPU via Nomad. Allocation exclusive, prevention conflits CUDA.

- `service.py`: NomadManager (submit_job, get_status, gpu_status)
- `models.py`: NomadJobRequest, NomadJobStatus, GPUStatus, NomadClusterStatus
- `routes.py`: Endpoints /api/nomad/*
- `utils.py`: build_job_spec, count_gpus

### 6. **compute_backends** (`src/modules/compute_backends/`)
Interface unifiee multi-backend pour soumettre des jobs ML sur differentes plateformes.

- `service.py`: BackendManager (auto-select, routing, job tracking)
- `models.py`: ComputeJobRequest, ComputeJobResponse, BackendType, JobStatus
- `routes.py`: Endpoints /api/backends, /api/compute/*
- `backends/base.py`: ComputeBackend ABC (interface commune)
- `backends/local.py`: Ray cluster (OnyxCortex GPU, Glia CPU)
- `backends/lightning.py`: Lightning AI Studios (T4 GPU, SDK Python)
- `backends/kaggle.py`: Kaggle Notebooks (T4 GPU, CLI API)
- Tests: 8 tests unitaires

**Auto-selection** : local (si healthy) > lightning > kaggle

**Flow** :
```
skill client → POST /api/compute/submit → BackendManager
                                            ├── local: Ray Dashboard API
                                            ├── lightning: Studio SDK → T4 GPU
                                            └── kaggle: kernels push → T4 GPU
```

### 7. **sam/** et **serve_proxy/** (LEGACY)
Modules proxy SAM historiques. SAM est desormais gere par bone-annotator.
Ces modules sont conserves temporairement mais seront supprimes.

---

## Job Templates

### bone-recognition (`jobs/bone-recognition/train_efficientnet.py`)
EfficientNet-B0 avec curriculum learning multi-task.
- Phase A : Pre-training angle (self-supervised)
- Phase B : Supervised training (classification, density, landmarks)

### bone-annotator (`jobs/bone-annotator/train_yolo.py`)
YOLOv8 detection d'objets pour annotation de bones.
- Modeles : yolov8n/s/m/l/x (configurable)
- Sauvegarde best.pt dans ML_MODELS_DIR

### bone-ml (`jobs/bone-ml/train_multitask.py`)
Dual-Head U-Net pour segmentation + landmarks heatmaps.
- Segmentation Head : zones anatomiques
- Landmarks Head : Gaussian heatmaps avec SGR
- Encodeur : ResNet34/50/Swin (pretrained ImageNet)

---

## Monitoring

```
OnyxSoma (10.0.0.44)
├── Prometheus (:9090) — scrape 15s, retention 30 jours
└── Grafana (:3000) — dashboards Node/GPU/Ray

Workers — Metrics
├── OnyxCortex — Node Exporter (:9100) + GPU Exporter (:9445)
├── Glia — Node Exporter (:9100)
└── OnyxPoint — Node Exporter (:9100) + GPU Exporter (:9445)
```

---

## Structure des repertoires

```
ml-compute/
├── src/
│   ├── config.py               # Chargement config/ml-compute.yaml
│   ├── main.py                 # FastAPI app (~279 lignes)
│   ├── models.py               # Modeles Pydantic
│   └── modules/
│       ├── jobs/               # Ray Jobs API proxy
│       ├── nodes/              # Worker monitoring
│       ├── serve/              # Ray Serve management
│       ├── models/             # Model registry
│       ├── nomad/              # Nomad GPU orchestration
│       │   ├── service.py
│       │   ├── models.py
│       │   ├── routes.py
│       │   └── utils.py
│       ├── compute_backends/   # Multi-backend job submission
│       │   ├── service.py     # BackendManager
│       │   ├── models.py      # Pydantic models
│       │   ├── routes.py      # /api/backends, /api/compute/*
│       │   └── backends/      # local, lightning, kaggle
│       ├── sam/                # [LEGACY] Proxy SAM
│       └── serve_proxy/        # [LEGACY] Proxy SAM routes
│
├── jobs/                       # Job templates Ray
│   ├── bone-annotator/         # YOLO training
│   ├── bone-recognition/       # EfficientNet training
│   └── bone-ml/                # Dual-Head U-Net training
│
├── models/                     # Stockage modeles entraines
├── config/ml-compute.yaml      # Configuration centralisee
├── docker-compose.yml          # Ray head + API
├── Dockerfile                  # FastAPI wrapper
├── manifest.json               # Config Forge (v0.2.0)
├── cron.json                   # Health checks
└── backup.json                 # Strategie sauvegarde
```

## Dependances

| Package | Version | Usage |
|---------|---------|-------|
| `ray[default,serve]` | 2.35.0 | Cluster + serving |
| `fastapi` | 0.104.1 | API wrapper |
| `httpx` | 0.25.0 | HTTP async |
| `pydantic` | 2.5.0 | Validation |
| `pyyaml` | 6.0.1 | Config loader |
| `onyx-sdk` | 2.1.0 | Integration Redis/Events |
| `lightning-sdk` | latest | Lightning AI Studios |
| `kaggle` | latest | Kaggle Notebooks API |

## Principes

- **Modules < 300 lignes** chacun
- **Types explicites** (mypy --strict)
- **Docstrings Google** sur toutes les fonctions publiques
- **Config YAML** pour toutes les URLs/constantes (pas de hardcode)
- **Async/await** httpx pour tous les appels HTTP
- **Secrets via Vault** (pas de credentials en dur)
