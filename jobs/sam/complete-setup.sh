#!/bin/bash
# Complete SAM setup: Deploy Nomad job + Test endpoint + Report status

set -e

NOMAD_ADDR=${NOMAD_ADDR:-http://10.0.0.26:4646}
SAM_HEALTH_URL="http://10.0.0.26:9470/health"
ML_COMPUTE_SAM_URL="http://10.0.0.44:9469/api/serve/sam/interact"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==============================================="
echo "SAM Complete Setup & Test"
echo "==============================================="
echo ""

# Step 1: Deploy Nomad job
echo "[1/5] Deploying SAM Nomad job..."
if bash "$SCRIPT_DIR/deploy.sh"; then
  echo "  ✓ Nomad job deployed"
else
  echo "  ✗ Nomad deployment failed"
  exit 1
fi

# Step 2: Wait for allocation to start
echo ""
echo "[2/5] Waiting for SAM container to start..."
for i in {1..60}; do
  if curl -s -f -X GET "$SAM_HEALTH_URL" >/dev/null 2>&1; then
    echo "  ✓ SAM container is running"
    break
  else
    if [ $i -eq 60 ]; then
      echo "  ✗ Timeout waiting for SAM container"
      exit 1
    fi
    printf "  ⏳ Waiting... ($i/60)\r"
    sleep 5
  fi
done

# Step 3: Test SAM health endpoint
echo ""
echo "[3/5] Testing SAM health endpoint..."
HEALTH_RESPONSE=$(curl -s -X GET "$SAM_HEALTH_URL")
echo "  Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
  echo "  ✓ SAM health check successful"
else
  echo "  ✗ SAM health check failed"
  exit 1
fi

# Step 4: Test ml-compute SAM endpoint
echo ""
echo "[4/5] Testing ml-compute SAM endpoint..."

# Create test request
TEST_REQUEST=$(cat <<'EOF'
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd3PcAAAACElEQVQI12NgAAAAAgABSK+kcQAAAAASUVORK5CYII=",
  "points": [[0, 0]],
  "negative_points": null,
  "box": null
}
EOF
)

SEGMENT_RESPONSE=$(curl -s -X POST "$ML_COMPUTE_SAM_URL" \
  -H "Content-Type: application/json" \
  -d "$TEST_REQUEST")

echo "  Response: $SEGMENT_RESPONSE" | head -c 200
echo "..."

if echo "$SEGMENT_RESPONSE" | grep -q '"status"'; then
  echo ""
  echo "  ✓ SAM segmentation endpoint successful"
else
  echo ""
  echo "  ✗ SAM segmentation endpoint failed"
  exit 1
fi

# Step 5: Final status
echo ""
echo "[5/5] Final Status Report"
echo "  ✓ SAM Nomad job: RUNNING"
echo "  ✓ Container health: OK"
echo "  ✓ ml-compute endpoint: OK"
echo "  ✓ Segmentation API: WORKING"

echo ""
echo "==============================================="
echo "✓ SAM Setup Complete!"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Test with real image:"
echo "   python3 $SCRIPT_DIR/test_sam_endpoint.py /path/to/image.jpg"
echo ""
echo "2. Deploy Nuclio proxy (requires Nuclio):"
echo "   cd $SCRIPT_DIR/../nuclio-sam-proxy"
echo "   nuctl deploy -f function.yaml"
echo ""
echo "3. Integrate with CVAT:"
echo "   See: $SCRIPT_DIR/../CVAT_INTEGRATION.md"
echo ""
echo "SAM Endpoint: $ML_COMPUTE_SAM_URL"
echo ""
