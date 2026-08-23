# Installation du Plugin GPU NVIDIA pour Nomad

## Vue d'ensemble

Pour que Nomad puisse gérer et allouer les GPUs NVIDIA aux jobs, le plugin GPU NVIDIA doit être installé et configuré sur chaque node worker avec GPU.

## Prérequis

- Nomad v1.1+ installé et en cours d'exécution
- NVIDIA drivers installés sur le worker
- `nvidia-smi` disponible et fonctionnel
- Accès root/sudo sur le worker

## Procédure Installation

### 1. SSH sur le worker

```bash
# OnyxCortex (RTX 4070 SUPER, 12GB)
ssh root@10.0.0.26

# OnyxPoint (T1000, 8GB)
ssh root@10.0.0.86
```

### 2. Exécuter le script d'installation

```bash
curl -s http://10.0.0.44:9469/scripts/install-gpu-plugin.sh | bash
```

Ou manuellement:

```bash
# Vérifier nvidia-smi
nvidia-smi

# Vérifier Nomad
nomad version

# Créer la configuration du plugin
sudo mkdir -p /etc/nomad.d
sudo tee /etc/nomad.d/gpu-plugin.hcl > /dev/null << 'EOF'
plugin "nvidia_gpu" {
  enabled = true
  config {
    fingerprint_period = "30s"
  }
}
EOF

# Redémarrer Nomad pour charger le plugin
sudo systemctl restart nomad

# Attendre 30 secondes que le plugin détecte les GPUs
sleep 30

# Vérifier la détection
nomad node status -json | jq '.NodeResources.Devices[] | select(.Type=="gpu")'
```

### 3. Vérifier la détection

#### Via Nomad CLI (sur le worker)

```bash
nomad node status -json | jq '.NodeResources'
```

#### Via ml-compute API (depuis OnyxSoma)

```bash
curl http://10.0.0.44:9469/api/nomad/gpu-status | jq '.'
```

Attendu (après installation):

```json
[
  {
    "node_id": "...",
    "node_name": "onyxcortex",
    "num_gpus": 1,
    "available_gpus": 1,
    "in_use": []
  },
  {
    "node_id": "...",
    "node_name": "OnyxPoint",
    "num_gpus": 1,
    "available_gpus": 1,
    "in_use": []
  },
  {
    "node_id": "...",
    "node_name": "onyxglia",
    "num_gpus": 0,
    "available_gpus": 0,
    "in_use": []
  }
]
```

## Dépannage

### Le plugin ne se charge pas

1. Vérifier les logs Nomad:
```bash
journalctl -u nomad -f
```

2. Vérifier que le fichier config est syntaxiquement correct:
```bash
nomad config validate /etc/nomad.d/gpu-plugin.hcl
```

3. Vérifier la présence de NVIDIA drivers:
```bash
nvidia-smi
lsmod | grep nvidia
```

### Les GPUs ne sont pas détectées

1. Vérifier que le plugin est chargé:
```bash
nomad node status -json | jq '.Plugins'
```

2. Redémarrer le client Nomad et attendre 60 secondes:
```bash
systemctl restart nomad
sleep 60
nomad node status -json | jq '.NodeResources.Devices'
```

### Conflits avec autres configurations

Si `nvidia_gpu` est déjà dans `/etc/nomad.d/nomad.hcl`, nettoyer:

```bash
sudo sed -i '/plugin "nvidia_gpu"/,/^}/d' /etc/nomad.d/nomad.hcl
sudo tee /etc/nomad.d/gpu-plugin.hcl > /dev/null << 'EOF'
plugin "nvidia_gpu" {
  enabled = true
}
EOF
sudo systemctl restart nomad
```

## Statut Installation

| Worker | GPU | Drivers | Nomad | Plugin | Status |
|--------|-----|---------|-------|--------|--------|
| OnyxCortex | RTX 4070 | ✓ | ✓ | ⏳ | À installer |
| OnyxPoint | T1000 | ✓ | ✓ | ⏳ | À installer |
| onyxglia | Aucune | ✓ | ✓ | N/A | CPU-only |

> **Note**: L'installation du plugin GPU NVIDIA sur les workers Nomad doit être faite manuellement par l'administrateur système ayant accès SSH aux machines. Une fois configuré, Nomad détectera automatiquement les GPUs et les allouera aux jobs.

## Références

- [Nomad NVIDIA GPU Plugin](https://developer.hashicorp.com/nomad/tools/devices/nvidia-gpu)
- [Nomad Device Plugins](https://developer.hashicorp.com/nomad/docs/devices)
- [NVIDIA CUDA Installation](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
