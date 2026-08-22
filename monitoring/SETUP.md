# ml-compute Cluster Monitoring Setup

Setup Prometheus + Grafana pour monitorer le cluster Ray ml-compute.

**Machines à monitorer** :
- OnyxSoma (10.0.0.44) — Head node
- OnyxCortex (10.0.0.26) — GPU worker (RTX 4070 SUPER)
- Glia (10.0.0.8) — CPU worker
- OnyxPoint (10.0.0.86) — Legacy/Archive worker

---

## 1. Install Exporters on ML Workers

### On each ML worker (OnyxCortex, Glia, OnyxPoint):

```bash
# Install Node Exporter (CPU, Memory, Disk, Network metrics)
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xzf node_exporter-1.7.0.linux-amd64.tar.gz
sudo cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/node-exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/node_exporter --collector.textfile.directory=/var/lib/node_exporter/textfile_collector

[Install]
WantedBy=multi-user.target
EOF

sudo useradd -rs /bin/false prometheus 2>/dev/null || true
sudo mkdir -p /var/lib/node_exporter/textfile_collector
sudo chown -R prometheus:prometheus /var/lib/node_exporter
sudo systemctl daemon-reload
sudo systemctl enable --now node-exporter
```

### On GPU machines (OnyxCortex, OnyxPoint only):

```bash
# Install NVIDIA GPU Exporter
git clone https://github.com/utkuozdemir/nvidia_gpu_prometheus_exporter.git
cd nvidia_gpu_prometheus_exporter
docker build -t nvidia-gpu-exporter .

# Or use pre-built image:
docker run -d --name nvidia-gpu-exporter --gpus all \
  -p 9445:9445 \
  utkuozdemir/nvidia_gpu_prometheus_exporter:latest
```

Or manually with nvidia-smi:

```bash
# Create custom exporter script
sudo tee /usr/local/bin/nvidia-smi-exporter.sh > /dev/null <<'EOF'
#!/bin/bash
while true; do
  nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.free,temperature.gpu \
    --format=csv,noheader,nounits | while IFS=',' read -r gpu_util mem_util mem_used mem_free temp; do
    echo "nvidia_gpu_utilization_percent $gpu_util"
    echo "nvidia_memory_utilization_percent $mem_util"
    echo "nvidia_memory_used_mb $((mem_used))"
    echo "nvidia_memory_free_mb $((mem_free))"
    echo "nvidia_gpu_temperature_celsius $temp"
  done
  sleep 15
done > /var/lib/node_exporter/textfile_collector/nvidia.prom.tmp
mv /var/lib/node_exporter/textfile_collector/nvidia.prom.tmp \
   /var/lib/node_exporter/textfile_collector/nvidia.prom
EOF

sudo chmod +x /usr/local/bin/nvidia-smi-exporter.sh

# Create systemd service
sudo tee /etc/systemd/system/nvidia-smi-exporter.service > /dev/null <<EOF
[Unit]
Description=NVIDIA GPU Exporter
After=node-exporter.service

[Service]
Type=simple
ExecStart=/usr/local/bin/nvidia-smi-exporter.sh

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now nvidia-smi-exporter
```

---

## 2. Deploy Prometheus + Grafana on OnyxSoma

On OnyxSoma (10.0.0.44):

```bash
# Copy monitoring stack to OnyxSoma
cd /opt/onyx/skills/ml-compute/monitoring

# Start Prometheus + Grafana
docker-compose -f docker-compose-monitoring.yml up -d

# Verify
docker-compose -f docker-compose-monitoring.yml ps
```

**Access**:
- **Prometheus**: http://10.0.0.44:9090
- **Grafana**: http://10.0.0.44:3000 (login: admin/admin)

---

## 3. Configure Grafana Data Source

1. Login to Grafana: http://10.0.0.44:3000
2. Go to **Configuration** → **Data Sources**
3. Add **Prometheus**:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
   - Click **Save & Test**

---

## 4. Import Grafana Dashboards

### Dashboard 1: Cluster Overview (Node Exporter Full)

```bash
# Import dashboard ID 1860 from Grafana Lab
# Via UI: Dashboards → Import → Enter ID 1860
```

### Dashboard 2: NVIDIA GPU Metrics

```bash
# Import dashboard ID 7752 from Grafana Lab
# Via UI: Dashboards → Import → Enter ID 7752
```

### Dashboard 3: Custom Ray Cluster Dashboard

Create custom dashboard with panels:

**Panel 1: GPU Utilization**
```promql
nvidia_gpu_utilization_percent{job="nvidia-gpu-cortex"}
nvidia_gpu_utilization_percent{job="nvidia-gpu-onyxpoint"}
```

**Panel 2: Memory Usage (Nodes)**
```promql
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
```

**Panel 3: CPU Usage**
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Panel 4: Ray Job Status (from Ray Dashboard API)**
```promql
ray_dashboard_job_status{status="RUNNING"}
```

---

## 5. Verify Metrics Collection

**Check Prometheus targets**:
```bash
curl http://10.0.0.44:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .job, instance: .labels.instance, health: .health}'
```

**Expected output**:
```json
{
  "job": "node-exporter-soma",
  "instance": "OnyxSoma",
  "health": "up"
}
{
  "job": "node-exporter-cortex",
  "instance": "OnyxCortex",
  "health": "up"
}
{
  "job": "nvidia-gpu-cortex",
  "instance": "OnyxCortex-GPU",
  "health": "up"
}
{
  "job": "node-exporter-glia",
  "instance": "Glia",
  "health": "up"
}
{
  "job": "node-exporter-onyxpoint",
  "instance": "OnyxPoint",
  "health": "up"
}
{
  "job": "nvidia-gpu-onyxpoint",
  "instance": "OnyxPoint-GPU",
  "health": "up"
}
```

---

## 6. Query Examples

**GPU Memory Usage (all workers)**:
```promql
nvidia_memory_used_mb
```

**CPU Utilization by Worker**:
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Available Memory**:
```promql
node_memory_MemAvailable_bytes
```

**Disk Usage**:
```promql
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100
```

---

## 7. Troubleshooting

**Prometheus can't scrape a target**:
```bash
# Check connectivity from OnyxSoma
curl http://10.0.0.26:9100/metrics  # OnyxCortex
curl http://10.0.0.8:9100/metrics   # Glia
curl http://10.0.0.86:9100/metrics  # OnyxPoint
```

**GPU exporter not working**:
```bash
# Verify nvidia-smi is installed and working
nvidia-smi

# Check exporter output
curl http://10.0.0.26:9445/metrics  # OnyxCortex GPU
```

**Grafana dashboards not showing data**:
1. Check Prometheus is scraping targets
2. Verify data source connection in Grafana
3. Check time range in dashboard (last 1h, last 24h, etc.)

---

## 8. Maintenance

**Backup Grafana dashboards**:
```bash
# Export all dashboards
curl -s http://localhost:3000/api/search | jq '.[].id' | while read id; do
  curl -s http://localhost:3000/api/dashboards/uid/$(curl -s http://localhost:3000/api/dashboards/id/$id | jq -r .dashboard.uid) > dashboard-$id.json
done
```

**Prometheus retention**:
- Default: 30 days
- Edit in `prometheus.yml`: `--storage.tsdb.retention.time=30d`

**Restart monitoring**:
```bash
docker-compose -f docker-compose-monitoring.yml restart
```
