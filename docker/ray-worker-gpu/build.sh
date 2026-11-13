#!/usr/bin/env bash
# Build ray-worker-gpu image and export to NFS for distribution.
#
# Usage:
#   ./build.sh              # build + export to NFS
#   ./build.sh --no-export  # build only (local)
#
# The image is exported as a tar.gz on NFS so any new rig can
# simply `docker load` without rebuilding from scratch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_NAME="ray-worker-gpu"
IMAGE_TAG="latest"
NFS_IMAGES="/mnt/ml-store/docker-images"

echo "=== Building $IMAGE_NAME:$IMAGE_TAG ==="
docker build \
    -t "$IMAGE_NAME:$IMAGE_TAG" \
    -f "$SCRIPT_DIR/Dockerfile" \
    "$SCRIPT_DIR"

# Tag with date for rollback
DATE_TAG=$(date +%Y%m%d)
docker tag "$IMAGE_NAME:$IMAGE_TAG" "$IMAGE_NAME:$DATE_TAG"
echo "Tagged: $IMAGE_NAME:$DATE_TAG"

# Export to NFS
if [[ "${1:-}" != "--no-export" ]]; then
    mkdir -p "$NFS_IMAGES"
    EXPORT_PATH="$NFS_IMAGES/${IMAGE_NAME}_${DATE_TAG}.tar.gz"
    LATEST_PATH="$NFS_IMAGES/${IMAGE_NAME}_latest.tar.gz"

    echo "=== Exporting to $EXPORT_PATH ==="
    docker save "$IMAGE_NAME:$IMAGE_TAG" | gzip > "$EXPORT_PATH"
    ln -sf "$(basename "$EXPORT_PATH")" "$LATEST_PATH"

    SIZE=$(du -h "$EXPORT_PATH" | cut -f1)
    echo "=== Done: $EXPORT_PATH ($SIZE) ==="
    echo ""
    echo "To load on a new rig:"
    echo "  docker load < $LATEST_PATH"
else
    echo "=== Build only (skipping NFS export) ==="
fi
