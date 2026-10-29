# ml-compute - Architecture

## Vue d'ensemble

**ml-compute** est un **orchestrateur ML centralisé** :
1. **Compute Backends** — Interface unifiee multi-backend (local Ray, Lightning AI, Kaggle)
2. **Ray** — Soumission et monitoring de jobs training distribues sur workers GPU/CPU
3. **Nomad** — Allocation exclusive des GPUs (anti-conflit CUDA entre jobs)
4. **FastAPI** — API unifiee pour les skills metier (bone-ml, bone-annotator, bone-recognition)

5. **GPU Management** — Acquire/release GPU sur OnyxCortex (stop/start SAM+MedSAM2 pour liberer VRAM)

**Hors scope** : SAM/MedSAM inference et CVAT sont geres directement par **bone-annotator** sur OnyxCortex, sans passer par Ray ni ml-compute (voir section "Separation SAM"). Cependant ml-compute gere l'allocation GPU via les endpoints `/api/gpu/*` (arret/relance des containers SAM pour liberer la VRAM avant training).

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
OnyxCortex (10.0.0.26) — GPU Training (ACTUEL, transitoire)
├── Hardware: 16-core i7-10700KF, RTX 4070 SUPER 12GB, 46GB RAM
├── Config: num_cpus=16, num_gpus=1, shm-size=10GB
├── Local Storage: /data/ml (916 GB SSD) <- Training I/O optimized
└── Usage: bone-rotation, bone-ml training (GPU-bound)
    GPU partagé avec SAM/MedSAM2 via /api/gpu/acquire|release

⚠️  Glia (10.0.0.8) — RETIRÉE DU CLUSTER (machine hors service)
⚠️  OnyxPoint (10.0.0.86) — MACHINE DÉDIÉE GROBID (HORS CLUSTER RAY)
```

### Contrainte d'extension GPU OnyxPoint

Audit matériel du 2026-10-29 : Lenovo ThinkCentre M70s SFF (type 11EX), Core i5-10400.

- L'unique slot PCIe 3.0 x16 low-profile est occupé par la NVIDIA T1000 8 Go (50 W).
- Il reste un slot PCIe 3.0 x1 low-profile ; ce n'est pas un second slot GPU x16.
- Le châssis accepte des cartes de moins de 155 mm de long et 68 mm de haut : aucune carte
  pleine hauteur ne peut être installée directement.
- Les deux autres ouvertures arrière sont des supports factices, sans connecteur PCIe.
- Un montage x1 avec riser, carte et alimentation externes serait un bricolage hors châssis,
  limité en bande passante et non retenu pour la production.

**Décision** : conserver OnyxPoint avec sa seule T1000 pour GROBID. Installer toute GPU
supplémentaire pleine hauteur dans les rigs ASRock H510 BTC+ prévus à cet effet.

### Volumes NFS (tous les workers)
```
/mnt/ml-store  (read-write) — datasets, models, runs (10.0.0.6:/srv/nas/ml)
/mnt/bonestore (read-only)  — images fluoroscopiques (10.0.0.52:/srv/bones)
```

---

## Rigs IA (FUTUR — 3× ASRock H510 BTC+)

Infrastructure GPU dediee en cours d'assemblage (3 cartes meres, 9 GPU recues, 5 a venir).
Remplacera OnyxCortex comme worker principal. VRAM totale : 168 Go.

### Rig 1 — Puissance (LLM + Training PARTAGÉ) — PSU 1200W
```
Slot x16 : RTX 3090 24 Go ─┐ vLLM Qwen2.5 72B Q4 (tensor parallel)
Slot 2   : RTX 3090 24 Go ─┘ → MODE PAR DEFAUT: LLM biblio (paper-reader, label-generator)
                              → MODE TRAINING: stop vLLM → DataParallel 2×3090 (48 Go)
Slot 3   : RTX 4070 Super 12 Go → training léger/fine-tuning (sans stopper vLLM)
Slots 4+ : futures cartes (4080S 16Go, 5070 12Go, 5060Ti 16Go, 4060 8Go)
```

**Scheduling partagé 3090** :
- **Défaut** : vLLM Qwen 72B Q4 sur 2×3090 (tensor parallel) — sert paper-reader,
  label-generator, extraction formules SymPy, toute la bibliographie
- **Training** : `POST /api/gpu/acquire?target=rig1` → stop vLLM → training ML
  DataParallel sur 2×3090 (bone-rotation, bone-ml, bone-train) → release → restart vLLM
- **Fallback** : RTX 4070 Super 12 Go pour jobs legers sans interrompre vLLM

### Rig 2 — Services always-on (Inference) — PSU 850W
```
Slot 1 : RTX 2060 Super 8 Go → Ollama bge-m3 embeddings (dédié)
Slot 2 : RTX 2060 Super 8 Go → SAM/MedSAM2 (CVAT annotation)
Slot 3 : RTX 2060 Super 8 Go → bone-rotation + bone-ml inference
Slot 4 : RTX 2060 Super 8 Go → Qwen2.5-VL 7B (OCR documents)
Slot 5 : RTX 2060 Super 8 Go → spare
Slot 6 : RTX 2060 Super 8 Go → spare
```

### Rig 3 — Expansion
Vide, pour les cartes a venir.

### Migration OnyxCortex → Rigs
Quand les rigs sont assembles :
1. RTX 4070 Super migre de Cortex vers rig 1 slot 3
2. SAM/MedSAM2 migre de Cortex vers rig 2 slot 2
3. Ray workers pointent vers rig 1 (multi-GPU) + rig 2 (inference)
4. OnyxCortex libéré (CPU worker ou retiré du cluster)

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

Workers Nomad Clients (actuel)
└── OnyxCortex (10.0.0.26) — 1 GPU RTX 4070 SUPER

Workers Nomad Clients (futur — rigs assembles)
├── Rig 1 — 2× RTX 3090 + 1× RTX 4070 SUPER (training)
└── Rig 2 — 6× RTX 2060 SUPER (inference always-on)
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

### 7. **gpu** (`src/modules/gpu/`)
Gestion de l'allocation GPU multi-cible. Arret/relance de services GPU pour liberer la VRAM avant training.

- `service.py`: get_gpu_status, acquire_gpu, release_gpu (via Docker API TCP)
- `models.py`: GPUStatusResponse, GPUAcquireResponse, GPUReleaseResponse, GPUMode
- `routes.py`: GET /api/gpu/status, POST /api/gpu/acquire, POST /api/gpu/release

**Implémenté (OnyxCortex)** :
- `POST /api/gpu/acquire` → stop SAM+MedSAM2 → libere ~6 Go VRAM sur Cortex
- `POST /api/gpu/release` → restart SAM+MedSAM2

**Design futur (Rig 1 — 3090 partagées LLM/Training)** :

Le meme pattern acquire/release sera etendu pour gerer les 2×RTX 3090 du rig 1 :

```
POST /api/gpu/acquire?target=rig1
  → stop vLLM (Qwen 72B tensor parallel sur 2×3090)
  → libere 48 Go VRAM
  → training DataParallel 2×3090 (bone-rotation, bone-ml, bone-train)

POST /api/gpu/release?target=rig1
  → restart vLLM
  → biblio, paper-reader, label-generator operationnels

GET /api/gpu/status?target=rig1
  → mode (llm | training | idle), VRAM par GPU, vLLM running, jobs en cours
```

**Targets supportees** (a implementer quand rigs assembles) :

| Target | GPUs | Mode defaut | Acquire = stop | Usage training |
|--------|------|-------------|----------------|----------------|
| `cortex` | RTX 4070S 12Go | inference (SAM) | SAM+MedSAM2 | bone-rotation, bone-ml |
| `rig1` | 2×3090 48Go + 4070S 12Go | llm (vLLM) | vLLM Qwen 72B | DataParallel 2×3090 |
| `rig1-light` | 4070S 12Go (rig1 slot 3) | idle | rien | fine-tuning sans stopper vLLM |

**Workflow type training lourd** :
```
1. POST /api/gpu/acquire?target=rig1     → stop vLLM, 48Go libres
2. POST /api/jobs { num_gpus: 2 }        → training DataParallel 2×3090
3. (monitoring via /api/jobs/{id})
4. POST /api/gpu/release?target=rig1     → restart vLLM
```

**Note**: Les modules legacy `sam/` et `serve_proxy/` ont ete supprimes (SAM gere par bone-annotator).
Le serveur Docker SAM reste dans `jobs/sam/sam_server.py` (image `sam-inference` sur OnyxCortex:9470).

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

### bone-ml BoneSeg (`jobs/bone-ml/train_boneseg.py`)
BoneSegNet (smp U-Net + MC-Dropout, ResNet50) pour segmentation osseuse multi-classe.
- Entrypoint Ray : `python jobs/bone-ml/train_boneseg.py`
- `runtime_env.working_dir` : `/opt/onyx/skills/ml-compute`
- Soumis par bone-ml via `POST /api/jobs` (module boneseg)
- Annotations PG `bone_annotations` avec tiers gold/silver/pseudo
- Loss tier-weighted (CE + Dice), early stopping, checkpoint avec metadonnees
- Update `boneseg_training_runs` en fin de job

### bone-train BoneSeg (`jobs/bone-train/train_boneseg.py`)
MONAI SwinUNETR 2D + MC-Dropout pour segmentation osseuse multi-classe.
- Entrypoint Ray : `python jobs/bone-train/train_boneseg.py`
- `runtime_env.working_dir` : `/opt/onyx/skills/ml-compute`
- `runtime_env.py_modules` : `[/opt/onyx/skills/bone-train]`
- Le wrapper ml-compute execute le job canonique `bone-train/jobs/train_boneseg.py` ;
  le modele, les datasets MONAI, les transforms et la boucle de training restent geres par bone-train
- Ray transfere le working directory et le module Python depuis OnyxSoma vers le driver GPU OnyxCortex

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
│       └── gpu/                # GPU management (acquire/release)
│           ├── service.py     # Docker API calls to Cortex:2375
│           ├── models.py      # GPUMode, GPUStatusResponse
│           └── routes.py      # /api/gpu/*
│
├── jobs/                       # Job templates Ray
│   ├── bone-annotator/         # YOLO training
│   ├── bone-recognition/       # EfficientNet training
│   ├── bone-ml/                # Dual-Head U-Net + BoneSegNet training
│   └── bone-train/             # MONAI SwinUNETR training
│
├── models/                     # Stockage modeles entraines
├── config/ml-compute.yaml      # Configuration centralisee
├── docker-compose.yml          # Ray head + API
├── Dockerfile                  # FastAPI wrapper
├── manifest.json               # Config Forge (v0.2.3)
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
