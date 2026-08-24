# Monitoring Nomad + GPU via Prometheus + Grafana

Ce guide configure un **monitoring complet** du cluster Nomad avec focus sur:
- GPU allocation et utilization
- Job status tracking (SAM + Ray training)
- GPU conflict detection
- Alerts en cas de problème

## 1. Prerequisites

```bash
# Vérifier que les services sonts accessibles
curl -s http://10.0.0.44:4646/v1/status/leader | jq .
curl -s http://10.0.0.44:9469/api/nomad/status | jq .
```

## 2. Installation Prometheus

### Option A: Docker Compose (Recommandé)

```yaml
# docker-compose.yml sur OnyxSoma
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./nomad-alerts.yml:/etc/prometheus/nomad-alerts.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_SECURITY_ADMIN_USER=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:
```

### Option B: Systemd Services

```bash
# Prometheus
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Download + install
curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | \
  jq -r '.assets[] | select(.name | contains("linux-amd64")) | .browser_download_url' | \
  head -1 | xargs curl -sL -o /tmp/prometheus.tar.gz
tar -xzf /tmp/prometheus.tar.gz -C /tmp/
sudo cp /tmp/prometheus-*/prometheus /usr/local/bin/
```

## 3. Configuration

### Step 1: Update prometheus.yml

```bash
cd /home/onyx/projects/skills/ml-compute
cp /tmp/prometheus-nomad.yml /etc/prometheus/nomad-scrape.yml
```

Append to `/etc/prometheus/prometheus.yml`:
```yaml
# Include Nomad metrics
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'nomad-server'
    metrics_path: '/v1/metrics'
    params:
      format: ['prometheus']
    static_configs:
      - targets: ['10.0.0.44:4646']

  - job_name: 'nomad-clients'
    metrics_path: '/v1/metrics'
    params:
      format: ['prometheus']
    static_configs:
      - targets:
          - '10.0.0.26:4646'
          - '10.0.0.86:4646'
          - '10.0.0.8:4646'

  - job_name: 'ml-compute'
    static_configs:
      - targets: ['10.0.0.44:9469']

# Alert Rules
rule_files:
  - '/etc/prometheus/nomad-alerts.yml'
```

### Step 2: Copy Alert Rules

```bash
sudo cp /tmp/nomad-alerts.yml /etc/prometheus/
sudo chown prometheus:prometheus /etc/prometheus/nomad-alerts.yml
```

### Step 3: Restart Prometheus

```bash
# If systemd
sudo systemctl restart prometheus

# If Docker
docker-compose -f /opt/nomad-monitoring/docker-compose.yml restart prometheus
```

## 4. Grafana Setup

### Access Grafana

```
http://10.0.0.44:3000
Login: admin / admin (change password!)
```

### Add Prometheus Data Source

1. Settings → Data Sources → Add
2. URL: `http://prometheus:9090`
3. Save & Test

### Import Dashboard

1. Create → Import
2. Upload `/tmp/nomad-grafana-dashboard.json`
3. Or create manual panels:

**Panel: GPU Utilization**
```
Select: nvidia_smi_utilization_gpu
Group by: job, node
```

**Panel: Job Status**
```
Select: nomad_job_running_count
Gauge chart
```

**Panel: SAM vs Training GPU Allocation**
```
Query 1: nomad_allocation_memory_used{job=~'sam.*'}
Query 2: nomad_allocation_memory_used{job=~'bone-ml.*'}
```

## 5. Key Metrics to Monitor

| Metric | Query | Alert Threshold |
|--------|-------|-----------------|
| GPU Utilization | `nvidia_smi_utilization_gpu{}` | > 95% for 5m |
| VRAM Usage | `nvidia_smi_memory_used_mb{}` | > 11000 (OnyxCortex) |
| Job Status | `nomad_job_status{status='failed'}` | Any failed job |
| Node Connectivity | `nomad_node_status{status='connected'}` | < 3 nodes |
| GPU Conflicts | SAM + Training on same node | Alert immediately |

## 6. Querying via API

### Query Nomad Metrics

```bash
# Get all metrics from Nomad server
curl 'http://10.0.0.44:4646/v1/metrics?format=prometheus'

# Filter by job
curl 'http://10.0.0.44:4646/v1/metrics?format=prometheus' | grep 'sam'
```

### Query Prometheus

```bash
# Current GPU utilization
curl 'http://10.0.0.44:9090/api/v1/query?query=nvidia_smi_utilization_gpu'

# Time range query (last 1 hour)
curl 'http://10.0.0.44:9090/api/v1/query_range' \
  --data-urlencode 'query=nomad_job_running_count' \
  --data-urlencode 'start=2026-08-23T00:00:00Z' \
  --data-urlencode 'end=2026-08-23T01:00:00Z' \
  --data-urlencode 'step=60s'
```

## 7. Alerting Configuration

### AlertManager (Optional)

Pour envoyer alerts à Slack/email:

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  receiver: 'gpu-alerts'
  group_by: ['alertname', 'node']

receivers:
  - name: 'gpu-alerts'
    slack_configs:
      - channel: '#ml-compute-alerts'
        title: 'GPU Alert: {{ .GroupLabels.node }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## 8. Common Queries

### SAM Running?
```promql
count(nomad_allocation_status{job=~'sam.*', status='running'})
```

### All GPUs Busy?
```promql
count(nomad_allocation_resources_gpu{}) == 2
```

### Training Jobs Queued
```promql
count(nomad_allocation_status{job=~'bone.*', status='pending'})
```

### Node Health
```promql
nomad_node_status{status=~'ready|connecting'}
```

## 9. Troubleshooting

### Prometheus not scraping Nomad
```bash
# Check target status
curl http://10.0.0.44:9090/api/v1/targets

# Verify Nomad metrics endpoint
curl http://10.0.0.44:4646/v1/metrics?format=prometheus | head
```

### No GPU metrics showing
```bash
# Check nvidia-smi available
ssh onyx@10.0.0.26 nvidia-smi

# Check nvidia_smi exporter running
curl http://10.0.0.26:9445/metrics | grep nvidia_smi
```

### Grafana can't reach Prometheus
```bash
# From Grafana container
docker exec grafana curl http://prometheus:9090/-/healthy
```

## 10. Next Steps

1. ✓ Nomad cluster operational
2. ✓ Monitoring setup (this guide)
3. → Deploy Prometheus + Grafana stack
4. → Create GPU conflict detection alerts
5. → Add ml-compute metrics export
6. → Build SAM + Training coordination tests
