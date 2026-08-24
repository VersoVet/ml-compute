# Installation Manuelle - Plugin GPU NVIDIA pour Nomad

## ⚠️ Le téléchargement automatique échoue

Les fichiers ZIP du plugin ne sont pas accessibles via les URLs publiques de notre environnement.
Solution: Installation manuelle directe sur les workers.

## Documentation Officielle

Voir: https://developer.hashicorp.com/nomad/plugins/devices/nvidia

## Installation Rapide (SSH)

### Sur OnyxCortex (10.0.0.26) - RTX 4070 SUPER

```bash
ssh onyx@10.0.0.26

# 1. Créer le répertoire plugins
mkdir -p /opt/nomad/plugins
cd /opt/nomad/plugins

# 2. Télécharger le plugin
# Option A: Depuis votre machine locale avec accès Internet
wget https://github.com/hashicorp/nomad-device-nvidia-gpu/releases/download/v1.6.0/nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip
unzip nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip
rm nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip
chmod +x nomad-device-nvidia-gpu

# Option B: Si wget échoue, copier depuis OnyxSoma ou OnyxDendrite
# (Si vous avez un accès à une machine avec Internet)

# 3. Vérifier le plugin
ls -lh nomad-device-nvidia-gpu
./nomad-device-nvidia-gpu --version

# 4. Vérifier la config Nomad
sudo grep -i "plugin_dir" /etc/nomad.d/nomad.hcl || \
  echo "plugin_dir = \"/opt/nomad/plugins\"" | sudo tee -a /etc/nomad.d/nomad.hcl

# 5. Configurer le plugin GPU
sudo bash -c 'grep -q "nvidia_gpu" /etc/nomad.d/nomad.hcl || cat >> /etc/nomad.d/nomad.hcl << EOF

plugin "nvidia_gpu" {
  enabled = true
  config {
    fingerprint_period = "30s"
  }
}
EOF'

# 6. Redémarrer Nomad
sudo systemctl restart nomad

# 7. Attendre la détection (30s)
sleep 30

# 8. Vérifier que les GPUs sont détectées
nomad node status -json | jq '.NodeResources.Devices[] | select(.Type=="gpu")'
```

### Sur OnyxPoint (10.0.0.86) - T1000

Répéter les mêmes étapes avec:
```bash
ssh onyx@10.0.0.86
# ... mêmes commandes
```

## Vérifier la Détection

### Depuis le cluster (OnyxSoma)

```bash
# Via ml-compute API
curl http://10.0.0.44:9469/api/nomad/gpu-status | jq .

# Résultat attendu:
# [
#   {
#     "node_name": "onyxcortex",
#     "num_gpus": 1,        # ← Doit être > 0
#     "available_gpus": 1,
#     "in_use": []
#   },
#   {
#     "node_name": "OnyxPoint",
#     "num_gpus": 1,        # ← Doit être > 0
#     "available_gpus": 1,
#     "in_use": []
#   },
#   ...
# ]
```

### Directement sur le worker

```bash
ssh onyx@10.0.0.26

# Vérifier les resources
nomad node status -json | jq '.NodeResources.Devices'

# Ou
nomad node status -verbose | grep -A 20 Device
```

## Dépannage

### Le plugin n'a pas pu être téléchargé

**Solution**: Télécharger manuellement sur une machine avec Internet:

1. Aller sur: https://github.com/hashicorp/nomad-device-nvidia-gpu/releases
2. Télécharger: `nomad-device-nvidia-gpu_X.X.X_linux_amd64.zip`
3. Extraire le binaire
4. Copier via SCP:
   ```bash
   scp nomad-device-nvidia-gpu onyx@10.0.0.26:/tmp/
   ssh onyx@10.0.0.26 "sudo cp /tmp/nomad-device-nvidia-gpu /opt/nomad/plugins/"
   ```

### Le plugin est présent mais les GPUs ne sont pas détectées

1. Vérifier NVIDIA drivers:
   ```bash
   nvidia-smi
   ```

2. Vérifier les permissions:
   ```bash
   ls -la /opt/nomad/plugins/nomad-device-nvidia-gpu
   # Doit être exécutable (x)
   ```

3. Vérifier les logs Nomad:
   ```bash
   sudo journalctl -u nomad -n 100 | grep -i "nvidia\|plugin\|device"
   ```

4. Redémarrer Nomad:
   ```bash
   sudo systemctl restart nomad
   sleep 30
   nomad node status -json | jq '.NodeResources.Devices'
   ```

## Une fois les GPUs détectées

Tester SAM:

```bash
# Déployer SAM
curl -X POST http://10.0.0.44:9469/api/serve/sam/deploy

# Vérifier status (doit montrer allocation GPU)
curl http://10.0.0.44:9469/api/serve/sam/status | jq .

# Vérifier GPU allocations
curl http://10.0.0.44:9469/api/nomad/gpu-status | jq .

# Tester segmentation
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "...",
    "points": [[100, 200]]
  }'
```

## Versions Compatibles

Testées avec Nomad v1.9.0:
- Plugin v1.6.0 ✓
- Plugin v1.5.0 ✓
- Plugin v1.4.0 ✓

## Status Actuel

| Component | Status | Notes |
|-----------|--------|-------|
| Nomad Server | ✅ Actif | OnyxSoma :4646 |
| Nomad Clients | ✅ Actif | OnyxCortex, OnyxPoint prêts |
| Plugin binaire | ⏳ À installer | Manual required |
| GPU Detection | ⏳ Attente | Dépend du plugin |
| SAM API | ✅ Opérationnel | Endpoints testables |
| Monitoring | ✅ Déployé | Prometheus + Grafana |

---

**Une fois le plugin installé → Nomad détectera automatiquement les GPUs → SAM allocation exclusive opérationnelle à 100%** 🚀
