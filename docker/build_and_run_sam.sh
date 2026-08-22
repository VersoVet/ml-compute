#!/bin/bash

# Build and run SAM Docker image on OnyxCortex

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="onyx/sam:latest"
CONTAINER_NAME="sam-service"
SAM_PORT=${SAM_PORT:-9470}
SAM_MODEL_PATH=${SAM_MODEL_PATH:-$HOME/sam-gpu}

echo "=== Building SAM Docker Image ==="
docker build -t "$IMAGE_NAME" \
  --build-arg="DOCKER_BUILDKIT=1" \
  -f "$SCRIPT_DIR/docker/Dockerfile.sam" \
  "$SCRIPT_DIR"

echo "=== Stopping existing SAM container ==="
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "=== Starting SAM container ==="
docker run -d \
  --name "$CONTAINER_NAME" \
  --gpus all \
  --shm-size=10gb \
  -p "$SAM_PORT:9470" \
  -v "$SAM_MODEL_PATH:/root/sam-gpu:ro" \
  -v /mnt/ml-store:/mnt/ml-store:rw \
  -v /mnt/bonestore:/mnt/bonestore:ro \
  -e CUDA_VISIBLE_DEVICES=0 \
  --restart unless-stopped \
  --health-interval=30s \
  --health-timeout=10s \
  --health-start-period=60s \
  --health-retries=3 \
  "$IMAGE_NAME"

echo "=== Waiting for SAM to start ==="
sleep 10

if docker ps | grep -q "$CONTAINER_NAME"; then
  echo "✓ SAM container started successfully"
  echo "✓ Listening on port $SAM_PORT"
  docker logs -n 20 "$CONTAINER_NAME" | tail -10
else
  echo "✗ SAM container failed to start"
  docker logs "$CONTAINER_NAME"
  exit 1
fi
