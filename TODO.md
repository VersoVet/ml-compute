# TODO - ml-compute

## Phase 1: Initialisation (EN COURS)

- [x] Créer .gitignore
- [x] Créer backup.json (stratégie modèles ML)
- [x] Créer cron.json (daily-health-check, nodes-health)
- [x] Créer requirements.txt
- [x] Documenter ARCHITECTURE.md
- [x] Documenter API.md
- [ ] Créer src/main.py (FastAPI app)
- [ ] Créer structure modules (jobs, serve, nodes, models)

## Phase 2: FastAPI Core

- [ ] Implémenter main.py (~200 lignes)
  - [ ] Initialiser FastAPI app
  - [ ] Configurer lifespan (Ray client init/cleanup)
  - [ ] Endpoint GET /health
  - [ ] Endpoint GET /ready
  - [ ] Endpoint GET /pages (pour portail)
  
## Phase 3: Modules Ray

- [ ] Module **jobs** (Ray Jobs API proxy)
  - [ ] service.py: submit_job, get_status, get_logs, delete_job
  - [ ] routes.py: POST/GET/DELETE /api/jobs
  - [ ] Tests unitaires

- [ ] Module **nodes** (Monitoring workers)
  - [ ] service.py: query_nodes, get_resource_summary
  - [ ] routes.py: GET /api/nodes
  - [ ] Tests unitaires

- [x] Module **serve** (Ray Serve deployments)
  - [x] service.py: deploy, undeploy, list_deployments, get_serve_status (HTTP Dashboard API)
  - [x] routes.py: GET/POST /api/serve (Pydantic request models)
  - [ ] Tests unitaires

- [ ] Module **models** (Model registry)
  - [ ] service.py: scan_models, get_model_metadata
  - [ ] routes.py: GET /api/models
  - [ ] Tests unitaires

## Phase 4: Infrastructure Ray

- [ ] Créer docker-compose.yml (Ray head + FastAPI)
- [ ] Créer Dockerfile (FastAPI wrapper)
- [ ] Tester connexion workers (OnyxPoint, Glia, Axon)
- [ ] Setup Ray Dashboard (:8265) monitoring

## Phase 5: Validation & Déploiement

- [ ] Valider avec /forge-validate (22 phases)
- [ ] Corriger les erreurs de validation
- [ ] Revue de code multi-LLM avec /forge-review
- [ ] Déployer avec /forge-deploy
- [ ] Vérifier health check sur OnyxSoma

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
