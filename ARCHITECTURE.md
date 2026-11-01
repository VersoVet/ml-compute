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
OnyxTensor (10.0.0.73) — Rig 1 GPU Training (ACTUEL)
├── Hardware: Celeron G5905, 8GB RAM, PSU 1000W
├── ASRock H510 Pro BTC+ (BIOS P1.60)
├── GPU 0: RTX 3080 10GB (PCIE1 x16) — training principal
├── GPU 1: RTX 4060 8GB (riser x1) — training secondaire
├── GPU 2: RTX 2060 Super 8GB (riser x1) — training
├── Total: 26 GB VRAM, 3 GPUs
└── Config Ray: num_gpus=3 (à connecter)

OnyxCortex (10.0.0.26) — GPU Training + SAM (TRANSITOIRE)
├── Hardware: 16-core i7-10700KF, RTX 4070 SUPER 12GB, 46GB RAM
├── Config: num_cpus=16, num_gpus=1, shm-size=10GB
└── Usage: SAM/MedSAM2 + Ray worker (GPU à migrer vers Tensor)

⚠️  OnyxSynth (10.0.0.78) — Rig 2 LLM DÉDIÉ (HORS CLUSTER RAY)
    7 GPU dont 6 réservées au LLM Qwen3-32B-Q8_0 (llama.cpp)
    GPU 0 (RTX 3080 10GB) isolée, potentiellement disponible pour Ray
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

## Rigs IA — 2× ASRock H510 BTC+ (OPÉRATIONNEL)

### Rig 1 — OnyxTensor (10.0.0.73) — Training — PSU 1000W
```
PCIE1 x16 : RTX 3080 10 Go       → training principal (seul slot compatible 3080)
Riser x1  : RTX 4060 8 Go        → training secondaire
Riser x1  : RTX 2060 Super 8 Go  → training
(1 slot mort, 1 riser libre)
Total : 26 Go VRAM, 3 GPUs
```

**Évolution prévue** : ajouter RTX 4070 Super 12 Go (ex-Cortex) sur riser x1 → 38 Go VRAM.

### Rig 2 — OnyxSynth (10.0.0.78) — LLM Biblio — PSU ?
```
PCIE1 x16 : RTX 3080 10 Go       → ISOLÉE (CUDA_VISIBLE_DEVICES exclut GPU 0)
Riser x1  : RTX 2060 Super 8 Go  ─┐
Riser x1  : RTX 2060 Super 8 Go  ─┤
Riser x1  : RTX 2060 Super 8 Go  ─┤ LLM Qwen3-32B-Q8_0 via llama.cpp
Riser x1  : RTX 2060 Super 8 Go  ─┤ tensor-split 8,8,8,8,8,8
Riser x1  : RTX 2060 Super 8 Go  ─┤ 10.2 tok/s, port 8080
Riser x1  : RTX 2060 Super 8 Go  ─┘
Total : 58 Go VRAM (48 Go LLM + 10 Go isolée)
```

**Service** : systemd `llm-server` (auto-start, restart on failure)
**API** : `http://10.0.0.78:8080/v1/chat/completions` (OpenAI compatible)
**Modèle** : `onyx-qwen3-32b` dans LLM Router

### Compatibilité H510 BTC+ P1.60 (testée)

| Carte | PCIE1 x16 | Riser x1 |
|-------|-----------|----------|
| RTX 2060 Super (175W) | ✅ | ✅ |
| RTX 4060 (115W) | — | ✅ |
| RTX 3080 (320W) | ✅ | ❌ trop gourmande |
| RTX 5060 Ti / 5070 (Blackwell) | ❌ | ❌ incompatible BIOS |

### Migration OnyxCortex → Rigs (en cours)
1. RTX 4070 Super migre de Cortex vers Tensor riser x1 (Ada 200W, devrait passer)
2. RTX 5060 Ti 16 Go teste sur Cortex Z490 (Blackwell compatible UEFI moderne)
3. SAM/MedSAM2 reste sur Cortex (ou migre vers Synth GPU 0)
4. Ray workers : Tensor (training multi-GPU) + Cortex (transitoire)

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
├── OnyxCortex (10.0.0.26) — 1 GPU RTX 4070 SUPER (transitoire)
└── OnyxTensor (10.0.0.73) — 3 GPU (3080 + 4060 + 2060S) — à connecter

Worker hors Nomad
└── OnyxSynth (10.0.0.78) — 7 GPU, LLM dédié (pas de training)
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

**Design actuel — Targets GPU** :

| Target | Machine | GPUs | Mode defaut | Acquire = stop | Usage |
|--------|---------|------|-------------|----------------|-------|
| `cortex` | OnyxCortex .26 | RTX 4070S 12Go | inference (SAM) | SAM+MedSAM2 | training bone-ml |
| `tensor` | OnyxTensor .73 | 3080+4060+2060S 26Go | training | rien | training multi-GPU |
| `synth-spare` | OnyxSynth .78 GPU 0 | RTX 3080 10Go | idle (isolée du LLM) | rien | training overflow |

**Note** : OnyxSynth GPU 1-6 (6×2060S) sont **exclusivement réservées au LLM** (systemd llm-server).
Ne JAMAIS soumettre de jobs Ray sur ces GPU. Seule GPU 0 (3080 isolée) est potentiellement utilisable.

**Workflow training sur Tensor** :
```
1. POST /api/jobs { target: "tensor", num_gpus: 1 }  → training sur 3080 (PCIE1 x16)
2. POST /api/jobs { target: "tensor", num_gpus: 3 }  → training multi-GPU 3080+4060+2060S
3. (monitoring via /api/jobs/{id})
```

**Note**: Les modules legacy `sam/`, `serve_proxy/`, `jobs/sam/` et `jobs/nuclio-sam-proxy/` ont ete supprimes.
SAM est entierement gere par bone-annotator (image `sam-inference` sur OnyxCortex:9470).

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
MONAI SwinUNETR 2D + MC-Dropout — second rideau S3 (hors bone-rotation).
- Entrypoint Ray : `python jobs/bone-train/train_boneseg.py`
- `runtime_env.working_dir` : `/opt/onyx/skills/ml-compute`
- `runtime_env.py_modules` : `[/opt/onyx/skills/bone-train]`
- Ontologie = ZONES label-generator (même mapping que bone-ml multitask)
- Gate GOLD (≥50 frames) côté bone-train — pas de GPU tant qu'insuffisant
- A/B prévu vs `jobs/bone-ml/train_boneseg.py` (ResNet50) — même test_sets
- Voir `jobs/bone-train/README.md`

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
