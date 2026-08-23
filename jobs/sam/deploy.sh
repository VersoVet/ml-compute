#!/bin/bash
# Deploy SAM Nomad job after Docker image is ready

set -e

NOMAD_ADDR=${NOMAD_ADDR:-http://10.0.0.26:4646}
JOB_SPEC="$(dirname "$0")/sam_job_spec.json"
IMAGE_NAME="sam-inference:v1"
TIMEOUT=60

echo "==============================================="
echo "SAM Nomad Deployment Script"
echo "==============================================="
echo "Nomad Address: $NOMAD_ADDR"
echo "Job Spec: $JOB_SPEC"
echo "Image: $IMAGE_NAME"
echo ""

# Step 1: Wait for Docker image
echo "[1/4] Checking Docker image availability..."
for i in $(seq 1 $TIMEOUT); do
  if ssh onyx@10.0.0.26 "docker images | grep -q $IMAGE_NAME"; then
    echo "  ✓ Image $IMAGE_NAME is available"
    break
  else
    if [ $i -eq $TIMEOUT ]; then
      echo "  ✗ Timeout waiting for image (${TIMEOUT}s)"
      exit 1
    fi
    echo "  ⏳ Waiting... ($i/${TIMEOUT}s)"
    sleep 5
  fi
done

# Step 2: Stop previous job (if exists)
echo ""
echo "[2/4] Stopping previous job (if exists)..."
if NOMAD_ADDR=$NOMAD_ADDR nomad job status sam-inference >/dev/null 2>&1; then
  echo "  Stopping job..."
  NOMAD_ADDR=$NOMAD_ADDR nomad job stop sam-inference
  sleep 10
  echo "  ✓ Job stopped"
else
  echo "  No previous job found"
fi

# Step 3: Submit new job
echo ""
echo "[3/4] Deploying new job..."
if NOMAD_ADDR=$NOMAD_ADDR nomad job run "$JOB_SPEC"; then
  echo "  ✓ Job submitted successfully"
else
  echo "  ✗ Failed to submit job"
  exit 1
fi

# Step 4: Wait for allocation
echo ""
echo "[4/4] Waiting for allocation..."
sleep 10

ALLOC_STATUS=$(NOMAD_ADDR=$NOMAD_ADDR nomad job status sam-inference | grep -A 5 "Summary" | grep "Running" | awk '{print $2}')

if [ "$ALLOC_STATUS" = "1" ] || [ "$ALLOC_STATUS" -ge 1 ]; then
  echo "  ✓ Allocation is running"
else
  echo "  ⚠ Allocation status unclear. Check with:"
  echo "    NOMAD_ADDR=$NOMAD_ADDR nomad job status sam-inference"
fi

echo ""
echo "==============================================="
echo "✓ Deployment completed!"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Check job status:"
echo "   NOMAD_ADDR=$NOMAD_ADDR nomad job status sam-inference"
echo ""
echo "2. Check container logs:"
echo "   NOMAD_ADDR=$NOMAD_ADDR nomad alloc logs <ALLOC_ID> sam-inference"
echo ""
echo "3. Test health endpoint:"
echo "   curl -X GET http://10.0.0.26:9470/health"
echo ""
echo "4. Test SAM segmentation:"
echo "   curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"image_base64\": \"...\", \"points\": [[100, 100]]}'"
echo ""
