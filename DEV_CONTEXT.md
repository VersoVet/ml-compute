# Contexte de développement — ml-compute

## Objectif

Orchestrateur ML centralisé basé sur Ray. Déployé sur Soma (10.0.0.44) comme Ray head node, il coordonne les workers ML distants pour le training et l'inférence GPU/CPU. Thin wrapper FastAPI devant Ray Jobs API et Ray Serve.

## Architecture

```
Soma (10.0.0.44) — Head Node (orchestration pure, --num-cpus=0)
│
├── ml-compute :9469 (FastAPI wrapper Forge)
├── Ray Head :6379 (GCS)
├── Ray Dashboard :8265
├── Ray Serve :8000
│
Workers (rejoignent le cluster via ray start --address=10.0.0.44:6379)
│
├── OnyxPoint (10.0.0.86) — GPU Worker
│   ├── T1000 8GB (num_gpus=1, VRAM_GB=8)
│   ├── YOLO training/inference
│   ├── PyTorch training/inference
│   └── (futur) vLLM serving
│
├── Glia — CPU Worker
│   ├── Preprocessing datasets (num_cpus=8)
│   ├── Batch augmentation
│   └── CPU-only inference
│
└── Axon (10.0.0.21) — CPU Worker
    ├── Grobid (extraction PDF, déjà installé)
    ├── Preprocessing texte (num_cpus=4, grobid=1)
    └── CPU-only tasks
```

## Type Forge : docker

Ce skill est de type `docker` dans le manifest. Le déploiement crée un Docker Compose sur Soma avec :
- Container `ray-head` : image `rayproject/ray-ml:2.35.0-py312`
- Container `api` : FastAPI wrapper

Les workers sont installés nativement sur chaque machine (pas dockerisés) via :
```bash
# OnyxPoint
pip install ray[default] && ray start --address=10.0.0.44:6379 --num-gpus=1 --resources='{"VRAM_GB": 8}' --node-name=onyxpoint

# Glia
pip install ray[default] && ray start --address=10.0.0.44:6379 --num-cpus=8 --node-name=glia

# Axon
pip install ray[default] && ray start --address=10.0.0.44:6379 --num-cpus=4 --resources='{"grobid": 1}' --node-name=axon
```

## Code à créer (pas de migration — tout est nouveau)

### Structure
```
ml-compute/
├── docker-compose.yml          # Ray head + API
├── Dockerfile                  # FastAPI wrapper
├── src/
│   ├── main.py                 # FastAPI app (~200 lignes)
│   ├── modules/
│   │   ├── jobs/
│   │   │   ├── service.py      # Proxy Ray Jobs API
│   │   │   └── routes.py       # POST/GET/DELETE /api/jobs
│   │   ├── serve/
│   │   │   ├── service.py      # Proxy Ray Serve deployments
│   │   │   └── routes.py       # /api/serve/*
│   │   ├── nodes/
│   │   │   ├── service.py      # Monitoring workers (GPU, CPU, RAM)
│   │   │   └── routes.py       # GET /api/nodes
│   │   └── models/
│   │       ├── service.py      # Gestion stockage modèles
│   │       └── routes.py       # GET /api/models
│   └── lib/
│       └── ray_client.py       # Client Ray Jobs SDK
├── jobs/                       # Scripts de jobs pré-configurés
│   ├── bone-annotator/
│   │   ├── train_yolo.py       # Training YOLO (migré de bone-ml)
│   │   └── predict_batch.py    # Batch inference YOLO
│   └── bone-recognition/
│       ├── train_efficientnet.py  # Training EfficientNet (migré de bone-recognition)
│       └── build_shape_model.py  # Construction modèle de forme
└── models/                     # Stockage modèles entraînés
    ├── bone-annotator/
    └── bone-recognition/
```

### Code modèle/training à migrer depuis bone-recognition

Le code de modèle EfficientNet-B0 et ses scripts de training deviennent des job templates dans `jobs/bone-recognition/` :

| Source bone-recognition | Destination | Description |
|------------------------|-------------|-------------|
| `src/model/architecture.py` | `jobs/bone-recognition/model/architecture.py` | EfficientNet-B0 multi-task (502 lignes) |
| `src/model/trainer.py` | `jobs/bone-recognition/model/trainer.py` | Training loop curriculum (516 lignes) |
| `src/model/losses.py` | `jobs/bone-recognition/model/losses.py` | Loss functions (122 lignes) |
| `src/model/attention.py` | `jobs/bone-recognition/model/attention.py` | CBAM attention (92 lignes) |
| `src/data/preprocessing.py` | `jobs/bone-recognition/data/preprocessing.py` | Prétraitement images (95 lignes) |
| `src/data/augmentation.py` | `jobs/bone-recognition/data/augmentation.py` | Augmentation données (162 lignes) |
| `src/data/dataset.py` | `jobs/bone-recognition/data/dataset.py` | PyTorch Dataset (283 lignes) |
| `scripts/train.py` | `jobs/bone-recognition/train.py` | Script CLI training (244 lignes) |
| `scripts/generate_pseudo_labels.py` | `jobs/bone-recognition/generate_pseudo_labels.py` | Génération pseudo-labels (199 lignes) |
| `scripts/populate_qdrant.py` | `jobs/bone-recognition/populate_qdrant.py` | Insertion embeddings Qdrant (139 lignes) |
| `scripts/build_shape_model.py` | `jobs/bone-recognition/build_shape_model.py` | Construction modèle PCA (135 lignes) |

## API endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Santé cluster Ray + workers connectés |
| `/api/nodes` | GET | État des workers (GPU, CPU, RAM par node) |
| `/api/jobs` | POST | Soumettre un job Ray |
| `/api/jobs` | GET | Lister les jobs (filtres: status, skill, node) |
| `/api/jobs/{id}` | GET | Statut + logs d'un job |
| `/api/jobs/{id}` | DELETE | Arrêter un job |
| `/api/serve/deployments` | GET | Lister les modèles servis (Ray Serve) |
| `/api/serve/deploy` | POST | Déployer un modèle via Ray Serve |
| `/api/serve/undeploy` | POST | Retirer un modèle |
| `/api/models` | GET | Modèles disponibles |

## Positionnement par rapport à llm-router

| | llm-router (10.0.0.44:8055) | ml-compute (10.0.0.44:9469) |
|---|---|---|
| **Quoi** | Routage appels API LLM cloud | Compute ML local (training + inférence) |
| **Durée** | <5min | Minutes à heures |
| **Ressource** | APIs (Groq, Claude, Gemini...) | GPU/CPU locaux (Ray cluster) |
| **À terme** | Route vers ml-compute pour LLM locaux (vLLM) | Expose vLLM comme provider pour llm-router |

## Interface vLLM (futur)

```python
# Déployer un LLM via Ray Serve + vLLM
POST /api/serve/deploy
{
    "name": "llama-3.3-8b",
    "type": "vllm",
    "model": "meta-llama/Llama-3.3-8B",
    "gpu_memory_utilization": 0.7,
    "node": "onyxpoint"
}
```
llm-router pourra router vers `http://10.0.0.44:8000/llama-3.3-8b`.

## Dépendances

- `ray[default,serve]>=2.35.0` (cluster + serving)
- `fastapi`, `uvicorn`, `httpx` (API wrapper)
- Workers doivent installer : `ultralytics` (YOLO), `torch`/`torchvision` (PyTorch)

## Ordre de développement suggéré

1. Docker Compose avec Ray head node sur Soma
2. FastAPI wrapper (`src/main.py`) avec endpoints health et nodes
3. Module jobs : proxy vers Ray Jobs API (submit, status, logs)
4. Installer Ray sur OnyxPoint et vérifier que le worker rejoint le cluster
5. Migrer les scripts de training depuis bone-recognition et bone-ml dans `jobs/`
6. Module serve : gestion des déploiements Ray Serve
7. Module models : stockage et listing des modèles entraînés
8. Tests end-to-end : soumettre un job YOLO training depuis bone-annotator
