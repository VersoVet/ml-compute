#!/bin/bash
# Deploy Prometheus + Grafana monitoring stack
# Execute on OnyxSoma (10.0.0.44)

set -e

MONITORING_DIR="/opt/onyx/skills/ml-compute/monitoring"
DOCKER_COMPOSE_FILE="docker-compose-monitoring.yml"

echo "=== Deploying Monitoring Stack (Prometheus + Grafana) ==="
echo ""

# 1. Check if monitoring directory exists
if [ ! -d "$MONITORING_DIR" ]; then
    echo "ERROR: $MONITORING_DIR not found"
    exit 1
fi

echo "✓ Monitoring directory found: $MONITORING_DIR"

# 2. Check docker-compose file
COMPOSE_PATH="$MONITORING_DIR/$DOCKER_COMPOSE_FILE"
if [ ! -f "$COMPOSE_PATH" ]; then
    echo "ERROR: $COMPOSE_PATH not found"
    exit 1
fi

echo "✓ Docker Compose file found"

# 3. Check Prometheus config
if [ ! -f "$MONITORING_DIR/prometheus.yml" ]; then
    echo "ERROR: prometheus.yml not found"
    exit 1
fi

echo "✓ Prometheus config found"

# 4. Verify Nomad is accessible
echo ""
echo "Verifying Nomad accessibility..."
if curl -s http://10.0.0.44:4646/v1/status/leader > /dev/null; then
    echo "✓ Nomad API is accessible"
else
    echo "⚠ WARNING: Nomad API not accessible at 10.0.0.44:4646"
fi

# 5. Deploy monitoring stack
echo ""
echo "Starting Prometheus + Grafana..."
cd "$MONITORING_DIR"

# Stop existing containers if any
docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
sleep 2

# Start new stack
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
sleep 3

# 6. Verify services are running
echo ""
echo "Verifying services..."

if docker ps | grep -q prometheus; then
    echo "✓ Prometheus container is running"
    PROM_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' prometheus)
    echo "  IP: $PROM_IP"
else
    echo "❌ ERROR: Prometheus container is not running"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs prometheus | tail -20
    exit 1
fi

if docker ps | grep -q grafana; then
    echo "✓ Grafana container is running"
    GRAFANA_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' grafana)
    echo "  IP: $GRAFANA_IP"
else
    echo "❌ ERROR: Grafana container is not running"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs grafana | tail -20
    exit 1
fi

# 7. Check Prometheus health
echo ""
echo "Checking Prometheus health..."
sleep 2

if curl -s http://10.0.0.44:9090/-/healthy > /dev/null; then
    echo "✓ Prometheus is healthy"
else
    echo "⚠ WARNING: Prometheus may not be fully ready yet"
fi

# 8. Check Grafana health
echo ""
echo "Checking Grafana health..."
GRAFANA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://10.0.0.44:3000/api/health)
if [ "$GRAFANA_STATUS" = "200" ]; then
    echo "✓ Grafana is healthy"
else
    echo "⚠ WARNING: Grafana returned status $GRAFANA_STATUS"
fi

# 9. Display URLs and credentials
echo ""
echo "=== Monitoring Stack Deployed Successfully ==="
echo ""
echo "Access URLs:"
echo "  Prometheus: http://10.0.0.44:9090"
echo "  Grafana:    http://10.0.0.44:3000"
echo ""
echo "Grafana Credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "Next Steps:"
echo "1. Access Grafana at http://10.0.0.44:3000"
echo "2. Verify Prometheus data source is configured"
echo "3. Import or create dashboards for:"
echo "   - Nomad cluster metrics (GPU, CPU, memory)"
echo "   - Ray cluster metrics"
echo "   - Node exporter metrics (system health)"
echo ""
echo "To view logs:"
echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo ""
echo "To stop:"
echo "  docker-compose -f $DOCKER_COMPOSE_FILE down"
