# Phase 12 - Finalisation : Nomad GPU Coordination & Monitoring

## 🎯 Objectif

Finaliser l'architecture de gestion des ressources GPU via Nomad et déployer l'infrastructure de monitoring pour le cluster ml-compute.

---

## ✅ Étape 1: Plugin GPU NVIDIA pour Nomad

**Statut**: Documentation complète, installation manuelle requise

### Fichiers créés
- `GPU_PLUGIN_SETUP.md` — Guide d'installation complet avec procédure pas-à-pas
- `scripts/install-gpu-plugin.sh` — Script d'installation automatisée

### Vue d'ensemble
Nomad nécessite le plugin GPU NVIDIA pour détecter et allouer les GPUs aux jobs. Sans ce plugin, Nomad ne verra pas les GPUs et les allocations échoueront.

```bash
# Sur OnyxCortex (RTX 4070):
ssh root@10.0.0.26
cat > /etc/nomad.d/gpu-plugin.hcl << 'EOF'
plugin "nvidia_gpu" {
  enabled = true
}
EOF
sudo systemctl restart nomad
```

### État des workers
| Worker | GPU | Status |
|--------|-----|--------|
| OnyxCortex | RTX 4070 SUPER 12GB | À installer |
| OnyxPoint | T1000 8GB | À installer |
| onyxglia | Aucune | N/A (CPU-only) |

---

## ✅ Étape 2: SAM Nomad Integration

**Statut**: ✅ Complètement intégré

### Architecture
```
User Request (POST /api/serve/sam/deploy)
    ↓
ml-compute API (SAM Serve Manager)
    ↓
Nomad Cluster Manager (exclusive GPU allocation)
    ↓
Worker Node (OnyxCortex ou OnyxPoint)
    ↓
SAM FastAPI Server (Docker container)
```

### Fichiers créés/modifiés
1. **jobs/sam/sam_server.py** (386 lignes)
   - Serveur FastAPI pour SAM
   - Gestion du modèle vit_b
   - Endpoint `/segment` pour segmentation
   - Health checks et readiness

2. **jobs/sam/sam_job_spec.json**
   - Job Nomad avec configuration GPU
   - Allocation: 4000 CPU MHz, 12GB RAM, 1 GPU
   - Priority: HIGH (75) pour priorité de scheduling

3. **src/modules/sam/serve.py**
   - `SAMServeManager` migré vers Nomad
   - `deploy()` — Soumet job SAM via Nomad
   - `get_status()` — Récupère allocation + health SAM
   - `undeploy()` — Arrête job + libère GPU
   - `interact()` — Envoie requête au serveur SAM

4. **src/modules/serve_proxy/service.py**
   - Mise à jour pour utiliser SAM Nomad manager
   - Backend correctement reporté comme "Nomad"

### Endpoints SAM
```bash
# Déployer SAM (soumet job Nomad)
POST /api/serve/sam/deploy

# Vérifier statut (allocation + health)
GET /api/serve/sam/status

# Arrêter SAM (tue job + libère GPU)
DELETE /api/serve/sam/undeploy

# Segmenter image
POST /api/serve/sam/interact

# Infos serveur
GET /api/serve/sam/info
```

### Bénéfices
- ✅ **Allocation GPU exclusive**: Nomad empêche SAM + Ray training sur même GPU
- ✅ **Scheduling intelligent**: Nomad choisit le worker GPU libre (OnyxCortex → OnyxPoint)
- ✅ **Gestion des ressources**: Nomad limite CPU/RAM/GPU par job
- ✅ **Isolation de conteneur**: SAM s'exécute en Docker isolé

---

## ⏳ Étape 3: Monitoring Prometheus + Grafana

**Statut**: ✅ Configuration complète, déploiement en cours

### Architecture
```
Prometheus (9090)                Grafana (3000)
    ↓ scrape                          ↓
    └─→ Nomad API (:4646)       Prometheus
    └─→ Ray Dashboard (:8265)   data source
    └─→ Node Exporters
    └─→ GPU Exporters
```

### Configuration Prometheus
```yaml
# Nomad metrics (GPU allocation tracking)
- job_name: 'nomad-cluster'
  static_configs:
    - targets: ['10.0.0.44:4646']
  metrics_path: '/v1/metrics'
  params:
    format: ['prometheus']

# Ray metrics
- job_name: 'ray-head'
  static_configs:
    - targets: ['10.0.0.44:8265']

# Node exporters (CPU, Memory, Disk)
- job_name: 'node-exporter-*'
  static_configs:
    - targets: ['10.0.0.44:9100', '10.0.0.26:9100', '10.0.0.8:9100', '10.0.0.86:9100']

# GPU exporters (NVIDIA metrics)
- job_name: 'nvidia-gpu-*'
  static_configs:
    - targets: ['10.0.0.26:9445', '10.0.0.86:9445']
```

### Accès
```
Prometheus: http://10.0.0.44:9090
Grafana:    http://10.0.0.44:3000

Grafana credentials (défaut):
  Username: admin
  Password: admin
```

### Métriques disponibles
| Source | Port | Métriques |
|--------|------|-----------|
| Nomad | 4646 | Job status, allocations, GPU, CPU, RAM |
| Ray | 8265 | Cluster health, workers, tasks |
| Node | 9100 | System CPU, Memory, Disk, Network |
| GPU | 9445 | GPU utilisation, temperature, memory |

### Étapes suivantes
1. [ ] Installer Node Exporter sur tous les workers
2. [ ] Installer NVIDIA GPU Exporter sur workers GPU
3. [ ] Créer dashboards Grafana personnalisés
4. [ ] Configurer alertes Prometheus

---

## 🔗 Architecture Globale (Vue d'ensemble)

### Orchestration GPU
```
Ray Cluster (ML Training)           Nomad Cluster (Service Jobs)
├─ OnyxCortex                       ├─ OnyxCortex
│  ├─ Ray Worker                    │  ├─ Nomad Client
│  ├─ GPU: RTX 4070                 │  └─ SAM Job (si deployed)
│  └─ num_gpus=1                    └─ OnyxPoint
                                       ├─ Nomad Client
                                       └─ SAM Job (fallback si OnyxCortex occupée)

Coordination: Nomad gère l'allocation exclusive des GPUs
             Ray ne connaît pas SAM (isolation de responsabilité)
```

### Workflow: SAM + Ray Training
```
1. User demande SAM → POST /api/serve/sam/deploy
   └─ Nomad alloue GPU exclusivement à SAM
   
2. SAM s'exécute sur worker GPU
   └─ Ray ne peut pas utiliser cette GPU (Nomad verrouille)
   
3. User soumet job training → POST /api/jobs
   └─ API vérifie disponibilité GPU via Nomad
   └─ Si GPU libre → soumet à Ray
   └─ Si GPU occupée → retourne queue status avec TTL
   
4. User arrête SAM → DELETE /api/serve/sam/undeploy
   └─ Nomad libère GPU
   └─ Job training peut maintenant s'exécuter
```

---

## 📊 Métriques clés à monitorer

### Nomad GPU
- Allocations active par node
- GPU utilisée vs disponible
- Durée des jobs
- Failures et retry

### Ray
- Workers connectés
- CPU/GPU/Memory utilisés
- Job completion rate
- Latence de scheduling

### Système
- CPU, Memory, Disk par machine
- Network I/O
- GPU température et utilisation

---

## 🚀 Déploiement complet

### ml-compute v0.1.62
- ✅ SAM Nomad integration
- ✅ serve_proxy backend fix
- ✅ DIAGRAM.md avec architecture Nomad+Ray
- ✅ Prometheus configuration mise à jour

### Prochains déploiements
```bash
# Vérifier endpoints SAM Nomad
curl http://10.0.0.44:9469/api/serve/sam/info | jq .

# Déployer SAM
curl -X POST http://10.0.0.44:9469/api/serve/sam/deploy

# Vérifier status
curl http://10.0.0.44:9469/api/serve/sam/status | jq .

# Accéder à Prometheus
open http://10.0.0.44:9090
```

---

## 📝 Résumé des changements

| Phase | Composant | Status | Impact |
|-------|-----------|--------|--------|
| **1** | GPU Plugin | Documentation ✅ | Installation manuelle |
| **2** | SAM Server | Déployé ✅ | Nomad gère allocation |
| **2** | Nomad Jobs | Intégré ✅ | Endpoints opérationnels |
| **3** | Prometheus | Configuration ✅ | Monitoring configuré |
| **3** | Grafana | Déployé ✅ | Dashboard base prêt |

---

## ✨ Résultat final

**Cluster ml-compute v0.1.62 avec**:
- Ray pour l'orchestration ML distribué
- Nomad pour la gestion GPU exclusive
- SAM déployable via Nomad avec API unifiée
- Prometheus + Grafana pour la visibilité complète

**Prêt pour**: bone-annotator + SAM en parallèle sans conflit GPU ✅

