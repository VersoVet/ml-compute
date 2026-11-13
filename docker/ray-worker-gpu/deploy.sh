#!/usr/bin/env bash
# Deploy ray-worker-gpu on one or all GPU workers.
#
# Usage:
#   ./deploy.sh tensor           # deploy on OnyxTensor only
#   ./deploy.sh cortex           # deploy on OnyxCortex only
#   ./deploy.sh all              # deploy on all workers
#   ./deploy.sh 10.0.0.73        # deploy by IP
#
# To add a new rig:
#   1. Add an entry in WORKERS below
#   2. Run: ./deploy.sh <name>

set -euo pipefail

IMAGE_NAME="ray-worker-gpu"
NFS_IMAGE="/mnt/ml-store/docker-images/${IMAGE_NAME}_latest.tar.gz"
CONTAINER_NAME="ray-worker"
RAY_HEAD="10.0.0.44:6380"

# ====== WORKER REGISTRY ======
# Add new rigs here: name|ip|num_cpus|num_gpus|shm_size
declare -A WORKERS
WORKERS=(
    [tensor]="10.0.0.73|2|3|4g"
    [cortex]="10.0.0.26|16|1|10g"
    # [newrig]="10.0.0.XX|cpus|gpus|shm"
)
# ==============================

deploy_worker() {
    local name="$1"
    local config="${WORKERS[$name]}"
    IFS='|' read -r ip cpus gpus shm <<< "$config"

    echo ""
    echo "=== Deploying $name ($ip) — ${gpus} GPU, ${cpus} CPU ==="

    # Load image from NFS
    echo "  Loading image..."
    ssh "onyx@$ip" "docker load < $NFS_IMAGE" 2>&1 | tail -1

    # Stop old container
    echo "  Stopping old container..."
    ssh "onyx@$ip" "docker stop $CONTAINER_NAME 2>/dev/null; docker rm $CONTAINER_NAME 2>/dev/null" || true

    # Start new container
    echo "  Starting ray-worker..."
    ssh "onyx@$ip" "docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        --network host \
        --gpus all \
        --shm-size $shm \
        -v /mnt/ml-store:/mnt/ml-store:rw \
        -v /mnt/bonestore:/mnt/bonestore:ro \
        -e RAY_HEAD_ADDRESS=$RAY_HEAD \
        -e NUM_CPUS=$cpus \
        -e NUM_GPUS=$gpus \
        -e OBJECT_STORE_MEMORY=2000000000 \
        $IMAGE_NAME:latest"

    # Wait and verify
    sleep 5
    local status
    status=$(ssh "onyx@$ip" "docker exec $CONTAINER_NAME python -c 'import torch; print(f\"torch={torch.__version__} cuda={torch.cuda.is_available()} gpus={torch.cuda.device_count()}\")'" 2>&1)
    echo "  Verify: $status"
    echo "  $name OK"
}

# Parse target
TARGET="${1:?Usage: $0 <tensor|cortex|all|IP>}"

if [[ "$TARGET" == "all" ]]; then
    for name in "${!WORKERS[@]}"; do
        deploy_worker "$name"
    done
elif [[ -v "WORKERS[$TARGET]" ]]; then
    deploy_worker "$TARGET"
else
    # Try to match by IP
    for name in "${!WORKERS[@]}"; do
        ip=$(echo "${WORKERS[$name]}" | cut -d'|' -f1)
        if [[ "$ip" == "$TARGET" ]]; then
            deploy_worker "$name"
            exit 0
        fi
    done
    echo "ERROR: Unknown worker '$TARGET'. Available: ${!WORKERS[*]}"
    exit 1
fi

echo ""
echo "=== Deploy complete ==="
