# TODO - ml-compute

## Scope du skill

**ml-compute** = orchestrateur ML centralisé. Son rôle est exclusivement :
- Soumettre et monitorer des **jobs de training** via Ray
- Coordonner l'allocation **GPU exclusive** via Nomad (anti-conflit CUDA)
- Exposer l'**API unifiée** pour les skills métier (bone-ml, bone-annotator, bone-recognition)
- Gérer le **registre de modèles** entraînés

**Hors scope** (traité par d'autres skills) :
- SAM/MedSAM inference et CVAT integration : **bone-annotator** (directement sur OnyxCortex, sans passer par Ray)
- Logique métier training : **bone-ml**, **bone-recognition**
- Annotation et labels : **bone-annotator**, **label-generator**

---

## Historique (DONE)

<details>
<summary>Phases 1-12 terminées (cliquer pour détails)</summary>

### Phase 1-3: Init + FastAPI + Modules Ray (DONE)
Création du squelette, modules jobs/nodes/serve/models, tests unitaires (32 tests).

### Phase 4-5: Infrastructure Ray + Deploy (DONE)
Docker Compose Ray head + FastAPI, workers connectés (OnyxCortex, Glia, OnyxPoint).
Déploiement initial v0.1.35 sur OnyxSoma.

### Phase 6-8: Job Templates (DONE)
- `bone-recognition/train_efficientnet.py` : EfficientNet-B0 curriculum learning
- `bone-annotator/train_yolo.py` : YOLOv8 detection
- `bone-ml/train_multitask.py` : Dual-Head U-Net (segmentation + landmarks)

### Phase 9: Cluster Expansion (DONE)
OnyxCortex ajouté comme worker GPU principal (RTX 4070 SUPER 12GB).

### Phase 10: Nomad GPU Coordination (DONE)
Module `nomad/` pour allocation GPU exclusive. Prévention conflits CUDA entre jobs.

### Phase 11: Monitoring (DONE)
Prometheus + Grafana déployés sur OnyxSoma. Node/GPU Exporters sur tous les workers.

### Phase 12: SAM Nomad Integration (DONE)
SAM job spec Nomad, GPU plugin docs. **Note**: SAM est désormais isolé dans bone-annotator.

### Phase 13: SAM isolation (DONE — bone-annotator)
SAM/MedSAM tourne directement sur OnyxCortex via bone-annotator + Nuclio + CVAT.
Ne passe plus par Ray ni ml-compute. Voir bone-annotator/API.md.

### v0.2.0: Code review cleanup (DONE)
Config YAML centralisée, imports absolus, dead code supprimé, StrEnum, datetime.now(UTC).

### v0.2.2: Module compute_backends (DONE)
Interface unifiée multi-backend : local Ray, Lightning AI (T4 validé), Kaggle (T4 en attente GPU).
Endpoints /api/backends et /api/compute/*. Auto-selection local > lightning > kaggle.

</details>

---

## Taches actives

### SAM / CVAT embed (2026-08-27)

- [x] Fix `jobs/sam/sam_server.py` : `/api/embed` retourne `blob` + `shape`
- [x] Ajouter `detail` a `SegmentationResponse`
- [x] Rebuild/restart container `sam-gpu` sur OnyxCortex (image sam-inference v0.2.3)
- [ ] Redeploy fonction MedSAM Nuclio si necessaire (bone-annotator)

### Compute backends — prochaines etapes

- [ ] Kaggle : debloquer GPU (verification telephonique en attente)
- [ ] Lightning AI : optimiser gestion Studio (start/stop automatique, preservation credits)
- [ ] Ajouter backend DigitalOcean (cle API stockee dans Vault)
- [ ] Transfert fichiers : upload datasets / download modeles entre backends
- [ ] Job queue : file d'attente si tous les backends GPU sont occupes

### Nettoyage legacy SAM

- [ ] Supprimer le module `src/modules/sam/` (code legacy, SAM dans bone-annotator)
- [ ] Supprimer le module `src/modules/serve_proxy/` (proxy SAM legacy)
- [ ] Retirer les routers SAM de `main.py`
- [ ] Supprimer `jobs/sam/` et `jobs/nuclio-sam-proxy/` (fichiers reference)
- [ ] Retirer la section SAM de `config/ml-compute.yaml`

### Fix et ameliorations

- [ ] Corriger `src/modules/jobs/tests/test_jobs.py` : mock async broken
- [ ] Connecter Axon (10.0.0.21) comme CPU Worker Ray
- [ ] Dashboard UI frontend (React/Svelte sur `/`)
- [ ] Alerting automatique via email-notification quand un job GPU fail
- [ ] Integration MLflow pour tracking des metrics de training
