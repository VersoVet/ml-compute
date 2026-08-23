#!/bin/bash
# Installation du Plugin GPU NVIDIA pour Nomad
# À exécuter sur chaque worker Nomad avec GPU
# Usage: bash install-gpu-plugin.sh

set -e

echo "=== Nomad NVIDIA GPU Plugin Installation ==="

# 1. Vérifier nvidia-smi
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ ERROR: nvidia-smi not found. NVIDIA drivers not installed."
    exit 1
fi

echo "✓ NVIDIA drivers detected"
GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader | head -1)
GPU_NAMES=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
echo "  Found: $GPU_COUNT GPU(s) - $GPU_NAMES"

# 2. Vérifier Nomad
if ! command -v nomad &> /dev/null; then
    echo "❌ ERROR: nomad not found. Install Nomad first."
    exit 1
fi

echo "✓ Nomad detected"
NOMAD_VERSION=$(nomad version 2>/dev/null | grep Nomad | awk '{print $2}')
echo "  Version: $NOMAD_VERSION"

# 3. Vérifier la configuration Nomad
NOMAD_CONFIG_DIR="/etc/nomad.d"
if [ ! -d "$NOMAD_CONFIG_DIR" ]; then
    echo "❌ ERROR: Nomad config directory not found: $NOMAD_CONFIG_DIR"
    exit 1
fi

echo "✓ Nomad config directory: $NOMAD_CONFIG_DIR"

# 4. Créer/mettre à jour la configuration du plugin GPU
GPU_PLUGIN_CONFIG="$NOMAD_CONFIG_DIR/gpu-plugin.hcl"

cat > "$GPU_PLUGIN_CONFIG" << 'EOF'
# Nomad NVIDIA GPU Device Plugin Configuration
# Auto-installed by ml-compute v0.1.60

plugin "nvidia_gpu" {
  enabled = true

  # Optional: Fingerprint interval (default: 30s)
  config {
    fingerprint_period = "30s"

    # Optional: Enable memory management
    manage_nvidia_display_device = false
  }
}
EOF

echo "✓ GPU plugin config created: $GPU_PLUGIN_CONFIG"

# 5. Vérifier que le plugin ne soit pas déjà dans le config principal
MAIN_CONFIG="$NOMAD_CONFIG_DIR/nomad.hcl"
if [ -f "$MAIN_CONFIG" ] && grep -q "nvidia_gpu" "$MAIN_CONFIG"; then
    echo "⚠️  GPU plugin already in main config ($MAIN_CONFIG)"
    echo "  Removing to use separate config file..."
    sed -i '/plugin "nvidia_gpu"/,/^}/d' "$MAIN_CONFIG"
fi

# 6. Redémarrer Nomad pour charger le plugin
echo "Restarting Nomad..."
if command -v systemctl &> /dev/null; then
    systemctl restart nomad
    sleep 3

    # Vérifier le statut
    if systemctl is-active --quiet nomad; then
        echo "✓ Nomad restarted successfully"
    else
        echo "❌ ERROR: Nomad failed to start"
        systemctl status nomad --no-pager
        exit 1
    fi
else
    echo "❌ ERROR: systemctl not found. Cannot restart Nomad."
    exit 1
fi

# 7. Vérifier que le plugin est chargé
echo ""
echo "Verifying GPU detection..."
sleep 2

# Le plugin doit être chargé maintenant - essayer de soumettre une job test
# (optionnel, juste pour vérifier)
if command -v nomad &> /dev/null; then
    NODE_NAME=$(nomad node metadata | grep -i hostname | cut -d= -f2 | head -1 || echo "unknown")
    echo "✓ Node hostname: $NODE_NAME"

    # Afficher les détails du node
    nomad node status -json 2>/dev/null | jq '.Attributes.driver | select(. != null)' || echo "  (node info unavailable)"
fi

echo ""
echo "=== Installation Complete ==="
echo "The GPU plugin is now configured and Nomad has been restarted."
echo "GPUs should appear in 'nomad node status' within 30 seconds."
echo ""
echo "To verify on Nomad HEAD node:"
echo "  curl http://10.0.0.44:9469/api/nomad/gpu-status | jq ."
