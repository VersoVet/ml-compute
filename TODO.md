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

## Phase 6: Migration Training Code

- [ ] Migrer code training depuis bone-recognition
  - [ ] Architecture EfficientNet-B0
  - [ ] Training loop + curriculum
  - [ ] Loss functions
  
- [ ] Migrer code training depuis bone-annotator
  - [ ] Scripts YOLO training
  
- [ ] Créer job templates dans jobs/

## Phase 7: Tests End-to-End

- [ ] Soumettre job YOLO depuis /api/jobs
- [ ] Monitorer avec /api/jobs/{id}
- [ ] Vérifier nodes avec /api/nodes
- [ ] Tester Ray Serve deployment
- [ ] Health checks cron en production
