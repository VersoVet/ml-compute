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

### Infrastructure GPU Rigs (2026-11-01 — EN COURS)

**Rig 1 — OnyxTensor** (10.0.0.73) — Training :
- [x] Assemblage ASRock H510 BTC+, flash BIOS P1.60
- [x] RTX 3080 10 Go validée sur PCIE1 x16
- [x] RTX 4060 8 Go + RTX 2060 Super 8 Go sur risers x1
- [x] Driver NVIDIA 580.196.07 installé
- [x] WOL configuré (MAC a8:a1:59:97:e1:bf)
- [ ] Installer Docker + NVIDIA Container Toolkit
- [ ] Connecter comme Ray worker (num_gpus=3)
- [ ] Ajouter RTX 4070 Super 12 Go (ex-Cortex) sur riser x1

**Rig 2 — OnyxSynth** (10.0.0.78) — LLM DÉDIÉ (HORS CLUSTER RAY) :
- [x] Assemblage ASRock H510 BTC+, flash BIOS P1.60
- [x] 7 GPU : RTX 3080 (PCIE1) + 6× RTX 2060 Super (risers)
- [x] Driver NVIDIA 580.178.04, Docker + NVIDIA toolkit
- [x] llama.cpp compilé avec CUDA (sm_75 + sm_86)
- [x] Qwen3-32B-Q8_0 téléchargé et opérationnel
- [x] Service systemd `llm-server` (port 8080, auto-start)
- [x] 7 GPU dédiées LLM (tensor-split 10,8,8,8,8,8,8)
- [x] WOL configuré (MAC a8:a1:59:97:e6:9c)
- [x] Swap 20 Go (4+16)
- ~~Connecter GPU 0 comme Ray worker~~ → **ANNULÉ** : les 7 GPU restent LLM

**LLM Router** :
- [x] Provider `onyx_synth` ajouté (onyx-qwen3-32b, http://10.0.0.78:8080)
- [x] Task routing mis à jour : biblio, extraction, summarization → onyx_synth prioritaire
- [ ] Redéployer llm-router sur OnyxSoma (docs obsolètes bloquent)

**Paper-reader** :
- [x] Config mise à jour : provider onyx_synth, model onyx-qwen3-32b
- [ ] Redéployer paper-reader sur OnyxAxon (docs obsolètes bloquent)
- [ ] Test lecture article scientifique via LLM local

### OnyxCortex (Gigabyte Z490M, i7-10700KF, 46 Go RAM)

- [x] RTX 4070 Super 12 Go en place (slot x16)
- [x] RTX 5060 Ti testée — **incompatible Z490M** (ne boot pas)
- [ ] RTX 4060 non disponible (déjà sur Tensor)
- [ ] Cortex reste mono-GPU (4070S), acquire/release pour training vs SAM

### BoneSeg training job

- [x] Script `jobs/bone-ml/train_boneseg.py` (BoneSegNet, tier-weighted loss, PG update)
- [x] Script `jobs/bone-train/train_boneseg.py` (SwinUNETR — ship 2026-10-29)
- [x] README A/B + zones label-generator
- [ ] Deploy ml-compute pour publier `jobs/bone-train/` sur OnyxSoma
- [ ] A/B GPU réel vs bone-ml — après GOLD ≥ 50

### Fix et ameliorations

- [x] Corriger `src/modules/jobs/tests/test_jobs.py` : mock async → sync
- [x] Nettoyage legacy SAM complet (modules, jobs, config)
- [x] Connecter OnyxTensor comme Ray worker (Docker + NVIDIA toolkit + ray-worker container, 2026-11-08)
- ~~Connecter OnyxSynth GPU 0 comme Ray worker~~ → ANNULÉ (7 GPU = LLM)
- [ ] Installer torch+timm+blosc2 dans ray-worker Tensor (même chose que Cortex — bloqueur pour Serve)
- [ ] Image Docker custom `ray-worker-gpu` avec deps pré-installées (éviter pip install au restart)
- [ ] Connecter Axon (10.0.0.21) comme CPU Worker Ray
- [ ] Dashboard UI frontend (React/Svelte sur `/`)
- [ ] Alerting automatique via email-notification quand un job GPU fail

---

## Ressources GPU disponibles (état au 2026-11-01)

### Ray Cluster (training)

| Worker | GPU | VRAM | Status |
|--------|-----|------|--------|
| OnyxTensor (.73) | 3080 + 4060 + 2060S | 26 Go | à connecter |
| OnyxCortex (.26) | 4070 Super | 12 Go | actif |
| **Total Ray** | **4 GPU** | **38 Go** | |

### LLM dédié (hors Ray — JAMAIS de training)

| Machine | GPU | Modèle | Débit |
|---------|-----|--------|-------|
| OnyxSynth (.78) | 7 GPU (3080 + 6×2060S) 58 Go | Qwen3-32B-Q8_0 | ~10 tok/s |

**API** : `http://10.0.0.78:8080/v1/chat/completions` — model `onyx-qwen3-32b`

### Cartes spare

| Carte | Raison |
|-------|--------|
| RTX 4080 Super 16 Go | VBIOS corrompu (Subsystem ID 0000) |
| RTX 5060 Ti 16 Go | Incompatible H510 BTC+, test Cortex Z490 prévu |
| RTX 5070 12 Go | Incompatible H510 BTC+ |
