# Plan de Déploiement SAM + Nuclio Proxy

**Statut**: En cours (build Docker SAM en background)  
**Date**: 2026-08-23

## Tâche 1: Fixer SAM Nomad ✓ EN COURS

### Problème Diagnostiqué
- Job Nomad SAM échoue avec "OOM Killed" (exit code 137)
- Cause: Installation de dépendances (pip install torch) au démarrage du container
- PyTorch 526 MB + décompression > mémoire disponible après système de base

### Solution Implémentée
1. **Dockerfile pré-compilé**:
   - Base: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`
   - Installe Python 3, pip dans le Dockerfile
   - PyTorch wheels depuis index officiel (pré-compilés)
   - Image compilée une fois, exécution rapide

2. **sam_server.py corrigé**:
   - PIL pour décodage d'image correct (base64 → PNG/JPG)
   - Pillow ajouté aux dépendances

3. **jobspec.json mis à jour**:
   - Image locale: `sam-inference:v1` (au lieu de nvidia/cuda + runtime install)

### Étapes de Déploiement

**[ÉTAPE 1] Build Docker** (EN COURS)
```bash
Status: En cours sur OnyxCortex
Commande: ssh onyx@10.0.0.26 "cd /tmp/sam-build && docker build -t sam-inference:v1 ."
Durée estimée: 30-45 minutes
Monitoring: Actif (affichage quand l'image est complétée)
```

**[ÉTAPE 2] Redéployer job Nomad** (ATTENTE)
```bash
# Une fois l'image disponible:
NOMAD_ADDR=http://10.0.0.26:4646 nomad job run jobs/sam/sam_job_spec.json

# Vérifier le statut:
NOMAD_ADDR=http://10.0.0.26:4646 nomad job status sam-inference

# Vérifier les logs:
NOMAD_ADDR=http://10.0.0.26:4646 nomad alloc logs <ALLOC_ID> sam-inference
```

**[ÉTAPE 3] Tester SAM** (ATTENTE)
```bash
# Health check:
curl -X GET http://10.0.0.26:9470/health

# Test segmentation:
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "...",
    "points": [[100, 100]],
    "negative_points": null,
    "box": null
  }'
```

---

## Tâche 2: Déployer Nuclio Proxy (PRÊT)

### Fichiers Créés
- `jobs/nuclio-sam-proxy/model_handler.py` - Handler HTTP pour proxy
- `jobs/nuclio-sam-proxy/function.yaml` - Configuration Nuclio
- `jobs/nuclio-sam-proxy/requirements.txt` - Dépendances (requests, numpy)
- `jobs/nuclio-sam-proxy/test_proxy.py` - Tests du proxy
- `jobs/nuclio-sam-proxy/README.md` - Documentation complète

### Architecture
```
[CVAT/Client] 
    ↓
[Nuclio Proxy] (OnyxSynapse 10.0.0.59:9070)
    ↓
[ml-compute SAM] (OnyxSoma 10.0.0.44:9469)
```

### Déploiement (À FAIRE APRÈS SAM FIXÉ)

**Option 1: Via nuctl CLI**
```bash
nuctl deploy \
  --project-name ml-compute \
  --function-name sam-proxy \
  --file jobs/nuclio-sam-proxy/function.yaml
```

**Option 2: Via API REST Nuclio**
```bash
# Créer un archive
cd jobs/nuclio-sam-proxy
zip -r sam-proxy.zip model_handler.py requirements.txt function.yaml

# Déployer
curl -X POST http://10.0.0.59:8070/api/functions \
  -H "Content-Type: multipart/form-data" \
  -F "function=@sam-proxy.zip"
```

**Option 3: Vérifier que Nuclio est disponible**
```bash
# Tester la connectivité
curl http://10.0.0.59:8070/api/versions

# Créer un test
cd jobs/nuclio-sam-proxy
python3 test_proxy.py
```

### Format Requête Proxy
```json
{
  "image_base64": "iVBORw0KGgoAAAANS...",
  "points": [[100, 100], [200, 200]],
  "negative_points": null,
  "box": null
}
```

### Format Réponse Proxy
```json
{
  "status": "success",
  "masks": [[0, 0, 1, 1, ...]],
  "iou_predictions": [0.95, 0.87]
}
```

---

## Timeline Estimée

| Étape | Durée | Statut |
|-------|-------|--------|
| Build Docker SAM | 30-45 min | ✓ EN COURS |
| Redéployer Nomad | 2 min | ⏳ ATTENTE |
| Test SAM | 5 min | ⏳ ATTENTE |
| Déployer Nuclio | 5 min | ⏳ ATTENTE |
| Test Nuclio Proxy | 5 min | ⏳ ATTENTE |
| **TOTAL** | **~50 min** | **EN COURS** |

---

## Checklist de Validation

- [ ] Image docker `sam-inference:v1` compilée et disponible sur OnyxCortex
- [ ] Job Nomad `sam-inference` en statut "running" (allocation active)
- [ ] Container SAM healthy (curl /health → 200 OK)
- [ ] Endpoint `/api/serve/sam/interact` accessible et répond
- [ ] Fonction Nuclio `sam-proxy` déployée sur OnyxSynapse
- [ ] Proxy forward les requêtes vers ml-compute sans erreur
- [ ] Test end-to-end: CVAT → Nuclio → SAM → résultat segmentation

---

## Notes

### Build Docker
- **Image de base**: nvidia/cuda:12.1.0-runtime-ubuntu22.04 (~2 GB)
- **PyTorch wheels**: torch==2.1.0 torchvision==0.16.0 (~2-3 GB)
- **Dépendances**: segment-anything, fastapi, uvicorn, pillow
- **Taille finale**: ~6-8 GB

### Problèmes Potentiels
1. **Connexion réseau lente**: Téléchargement PyTorch peut être long
2. **Espace disque insuffisant**: Vérifier `/tmp` sur OnyxCortex
3. **Timeout health check**: Augmenter `start-period` dans jobspec si nécessaire
4. **GPU pas accessible**: Vérifier que NVIDIA plugin est installé (déjà fait)

---

## Contacts / Ressources

- **OnyxCortex**: 10.0.0.26 (SAM Nomad)
- **OnyxSoma**: 10.0.0.44 (ml-compute backend)
- **OnyxSynapse**: 10.0.0.59 (Nuclio proxy)
- **Nomad UI**: http://10.0.0.26:4646
- **Nuclio UI**: http://10.0.0.59:8070
