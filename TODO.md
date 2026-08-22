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

## Phase 10: Monitoring Infrastructure (IN PROGRESS)

- [ ] Installer Prometheus + Grafana stack
  - [x] Configuration Prometheus (prometheus.yml)
  - [x] Docker Compose stack (Prometheus + Grafana)
  - [x] Grafana data source provisioning
  - [x] Documentation SETUP.md + README.md
  - [ ] Déployer sur OnyxSoma
  - [ ] Installer Node Exporter sur tous les workers
  - [ ] Installer NVIDIA GPU Exporter sur workers GPU
  - [ ] Créer dashboards Grafana personnalisés
  - [ ] Configurer alertes Prometheus

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
