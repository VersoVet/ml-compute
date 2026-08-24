# TODO - ml-compute

## Phase 1: Initialisation (DONE)

- [x] Créer .gitignore
- [x] Créer backup.json (stratégie modèles ML)
- [x] Créer cron.json (daily-health-check, nodes-health)
- [x] Créer requirements.txt
- [x] Documenter ARCHITECTURE.md
- [x] Documenter API.md
- [x] Créer src/main.py (FastAPI app)
- [x] Créer structure modules (jobs, serve, nodes, models)

## Phase 2: FastAPI Core (DONE)

- [x] Implémenter main.py (~285 lignes)
  - [x] Initialiser FastAPI app
  - [x] Configurer lifespan (Ray HTTP client init/cleanup)
  - [x] Endpoint GET /health
  - [x] Endpoint GET /ready
  - [x] Endpoint GET /pages (pour portail)
  
## Phase 3: Modules Ray (DONE)

- [x] Module **jobs** (Ray Jobs API proxy)
  - [x] service.py: submit_job, get_status, get_logs, delete_job
  - [x] routes.py: POST/GET/DELETE /api/jobs
  - [x] Tests unitaires (9 tests)

- [x] Module **nodes** (Monitoring workers via HTTP Dashboard API)
  - [x] service.py: query_nodes, get_resource_summary
  - [x] routes.py: GET /api/nodes, GET /api/nodes/summary
  - [x] Tests unitaires (5 tests)

- [x] Module **serve** (Ray Serve via HTTP Dashboard API)
  - [x] service.py: deploy, undeploy, list_deployments, get_serve_status
  - [x] routes.py: GET/POST /api/serve (Pydantic request models)
  - [x] Tests unitaires (13 tests)

- [x] Module **models** (Model registry)
  - [x] service.py: scan_models, get_model_by_id
  - [x] routes.py: GET /api/models
  - [x] Tests unitaires (5 tests)

## Phase 4: Infrastructure Ray (DONE)

- [x] Créer docker-compose.yml (Ray head py312 + FastAPI py312)
- [x] Créer Dockerfile (FastAPI wrapper python:3.12-slim)
- [x] Connecter OnyxPoint (10.0.0.86) — GPU T1000 8GB, num_cpus=10, num_gpus=1
- [x] Connecter Glia (10.0.0.8) — CPU 2x Xeon E5-2630, num_cpus=20, 47GB RAM
- [ ] Connecter Axon (10.0.0.21) — CPU Worker
- [x] Ray Dashboard (:8265) accessible

## Phase 5: Validation & Déploiement (DONE)

- [x] Valider avec /forge-validate-full (0 erreurs)
- [x] Déployer avec /forge-deploy (v0.1.35)
- [x] Health check OK sur OnyxSoma
- [x] Créer config/ml-compute.yaml

## Phase 6: Job Templates (DONE)

- [x] Créer structure jobs/
- [x] Créer job template bone-recognition
  - [x] train_efficientnet.py (Phase A + B via BoneTrainer)
  - [x] README.md avec exemples curl
- [x] Créer job template bone-annotator
  - [x] train_yolo.py (ultralytics YOLO)
  - [x] README.md avec exemples curl
- [x] Mettre à jour ARCHITECTURE.md avec job templates
- [x] Tester les jobs avec pytest (11/11 PASS)
- [x] Valider avec /forge-validate-full (VALID, 0E/10W)

## Phase 7: Tests End-to-End (DONE)

- [x] Créer tests unitaires pour job templates
  - [x] tests/test_job_templates.py (11 tests)
  - [x] Valider payloads JSON (bone-recognition A/B, bone-annotator YOLO n/m)
  - [x] Vérifier existence fichiers templates + READMEs
  - [x] Tester env vars requises et optionnelles
- [x] Test production : Soumettre job YOLO via /api/jobs
  - [x] Monitorer avec /api/jobs/{id}
  - [x] Vérifier list_jobs et delete_job
- [x] Fix Ray 2.35.0 JobSubmissionClient async/await compatibility
  - [x] Remove await from synchronous methods (submit_job, get_job_status, list_jobs, delete_job)
  - [x] Filter unsupported kwargs (num_cpus, num_gpus, memory)
  - [x] Fix Pydantic model validation (submission_time optional)
  - [x] Deploy and verify job submission works end-to-end

## Phase 8: Additional Job Templates (DONE)

- [x] Créer job template bone-ml Dual-Head U-Net
  - [x] train_multitask.py (~320 lignes) — Dual-Head U-Net with SGR
  - [x] README.md avec exemples curl et doc complète
  - [x] Mettre à jour ARCHITECTURE.md
  - [x] Mettre à jour API.md
  - [x] Valider avec /forge-validate-full (VALID, 0E, 9W)
  - [x] Déployer avec /forge-deploy (v0.1.40)
  - [x] Tester soumission via /api/jobs (successful submission)

## Phase 9: Cluster Expansion & Architecture Clarification (DONE)

## Phase 10: GPU Resource Coordination via Nomad (DONE)

### Problem Solved
- **Conflit GPU critique**: SAM Docker + Ray Training sur même GPU = CUDA crash
- **Solution**: Nomad orchestration avec allocation GPU exclusive

### Implementation Complete
- [x] Installer Nomad 1.9.0 sur cluster (OnyxSoma server + 3 workers)
- [x] Configurer clients Nomad sur workers (RPC registration, plugin support)
- [x] Créer module `src/modules/nomad/`
  - [x] `service.py`: NomadManager (submit_job, get_status, gpu_status)
  - [x] `models.py`: NomadJobRequest, NomadJobStatus, GPUStatus, NomadClusterStatus
  - [x] `routes.py`: Endpoints `/api/nomad/*` (status, submit, stop, gpu-status)
- [x] Intégrer Nomad dans `main.py` (lifespan connect/disconnect, router inclusion)
- [x] Mettre à jour ARCHITECTURE.md (sections Nomad + GPU coordination)
- [x] Valider et déployer ml-compute v0.1.58
- [x] Vérifier cluster Nomad (3 nœuds ready, 2 GPUs détectées)

### Endpoints Working
- `GET /api/nomad/status` → Cluster status (3 nodes, 2 GPUs)
- `POST /api/nomad/jobs/submit` → Submit job with GPU reservation
- `GET /api/nomad/gpu-status` → Per-node GPU allocation
- `GET /api/nomad/jobs/{job_id}` → Job status + allocations
- `POST /api/nomad/jobs/{job_id}/stop` → Stop job + cleanup

## Phase 10.5: SAM + Monitoring Implementation (DONE)

### SAM Nomad Job Template
- [x] Créer jobs/sam/ avec documentation complète
- [x] Créer sam_job_spec.json (template job Nomad)
- [x] Documentation SAM deployment, ressources requises, performance

### Monitoring Infrastructure
- [x] MONITORING_SETUP.md (guide complet installation Prometheus + Grafana)
- [x] Prometheus scrape config Nomad cluster metrics
- [x] Alert rules (GPU conflicts, job failures, hardware errors)
- [x] Grafana dashboard templates
- [x] monitor_nomad.py (CLI monitoring script avec conflict detection)

### Status
- ✓ SAM ready for Nomad deployment
- ✓ Monitoring infrastructure documented
- ✓ GPU conflict detection implemented in script
- ✓ Prometheus + Grafana stack ready to deploy

## Phase 11: Monitoring Infrastructure Deployment (DONE)

- [x] Installer Prometheus + Grafana stack
  - [x] Configuration Prometheus (prometheus.yml)
  - [x] Docker Compose stack (Prometheus + Grafana)
  - [x] Grafana data source provisioning
  - [x] Documentation SETUP.md + README.md
  - [x] Déployer sur OnyxSoma
  - [x] Installer Node Exporter sur tous les workers
  - [x] Installer NVIDIA GPU Exporter sur workers GPU
  - [x] Créer dashboards Grafana personnalisés (Ray metrics + Nomad metrics)
  - [x] Configurer alertes Prometheus

## Phase 12: SAM Nomad Integration & Monitoring Deployment (DONE)

### 1. NVIDIA GPU Device Plugin Installation (DONE)
- [x] Créer guide d'installation GPU_PLUGIN_SETUP.md
- [x] Créer script install-gpu-plugin.sh pour configuration Nomad
- [x] Documenter procédure pour OnyxCortex (RTX 4070) et OnyxPoint (T1000)
- [ ] Exécuter sur workers (nécessite accès SSH root)

### 2. SAM Nomad Integration (DONE)
- [x] Créer SAM FastAPI server (sam_server.py) avec model inference
- [x] Créer Nomad job spec pour SAM deployment (sam_job_spec.json)
- [x] Intégrer SAM manager avec Nomad API (deploy/status/undeploy)
- [x] Endpoints SAM: POST /deploy, GET /status, DELETE /undeploy
- [x] Mettre à jour serve_proxy pour utiliser Nomad backend
- [x] Documentation SAM deployment (jobs/sam/README.md)
- [x] DIAGRAM.md avec architecture Nomad + Ray

### 3. Monitoring Prometheus + Grafana (DONE)
- [x] Configuration Prometheus avec scrape Nomad metrics
- [x] Docker Compose stack (Prometheus :9090, Grafana :3000)
- [x] Grafana data source provisioning
- [x] Script de déploiement deploy-monitoring.sh
- [x] Déployer stack sur OnyxSoma
- [x] Installer Node Exporter sur workers
- [x] Installer NVIDIA GPU Exporter sur workers GPU
- [x] Créer dashboards Grafana (Nomad + Ray)
- [x] Configurer alertes Prometheus

## Phase 9: Cluster Expansion & Architecture Clarification (DONE)

- [x] Ajouter OnyxCortex (10.0.0.26) au cluster Ray
  - [x] Ray worker container lancé avec ray:2.35.0-py312
  - [x] GPU NVIDIA RTX 4070 SUPER (12GB VRAM) connectée
  - [x] 16 CPU cores + 46GB RAM détectés par Ray
  - [x] Prêt pour bone-ml training (Swin-T @1340×1340, batch=4)

- [x] Clarifier rôles des machines dans l'architecture
  - [x] OnyxSoma: Administration + Ray Head (orchestration only)
  - [x] OnyxCortex: ML GPU worker (primary training)
  - [x] Glia: ML CPU worker (fallback + CPU jobs)
  - [x] Axon: Infrastructure services (Grobid, Ollama embedding)
  - [x] OnyxPoint: Legacy/archive (available if needed)
  - [x] Mise à jour ARCHITECTURE.md avec clarification
  - [x] Mise à jour DIAGRAM.md avec separation nette

## Phase 13: SAM OOM Fix + Nuclio Proxy (DONE — traité par bone-annotator)

> SAM deployment, Nuclio proxy et intégration CVAT sont désormais gérés par le skill **bone-annotator**.
> Les fichiers templates dans `jobs/sam/` et `jobs/nuclio-sam-proxy/` restent comme référence.
