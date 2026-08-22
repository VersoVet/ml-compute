# ml-compute Cluster Installation Guide

**Chaîne d'installation standardisée** pour intégrer de nouveaux workers ML au cluster Ray + Monitoring.

Cette documentation doit être suivie **identiquement** pour tous les workers ML pour garantir l'alignement et la cohérence du cluster.

---

## Table of Contents

1. [Ray Worker Setup](#1-ray-worker-setup) — Tous les workers ML
2. [Monitoring Exporters](#2-monitoring-exporters) — Node Exporter + GPU Exporter
3. [Prometheus Deployment](#3-prometheus-deployment) — Centralisé sur OnyxSoma
4. [Grafana Dashboards](#4-grafana-dashboards) — Visualisation et alerting

---

## 1. Ray Worker Setup

### 1.1 Prerequisites

- Docker installé et fonctionnel
- GPU CUDA driver installé (pour GPU workers)
- SSH accès à OnyxSoma pour tester la connexion

### 1.2 Create Systemd Service (Permanent Ray Worker)

Sur **CHAQUE machine ML** (OnyxCortex, Glia, OnyxPoint, future workers...):

```bash
# SSH dans la machine worker
ssh onyx@<WORKER_IP>

# Créer le script de démarrage Ray worker
sudo tee /usr/local/bin/start-ray-worker.sh > /dev/null <<'EOF'
#!/bin/bash

# Ray Worker Startup Script
# Connecte le worker au Ray head node sur OnyxSoma (10.0.0.44:6380)

WORKER_NAME=$(hostname)
RAY_HEAD_ADDRESS="10.0.0.44:6380"
RAY_MEMORY=46000000000  # Adapter selon la RAM disponible
RAY_OBJECT_STORE=10000000000
NUM_CPUS=16  # Adapter selon les CPU disponibles
NUM_GPUS=1   # 0 pour CPU-only, 1 pour GPU workers

# Nettoyer les containers anciens
docker rm -f ray-worker 2>/dev/null || true

# Démarrer le Ray worker
# NOTE: NFS volumes (ml-store, bonestore) sont bind-mountés pour accès aux datasets/modèles
docker run -d \
  --name ray-worker \
  --network host \
  --gpus all \
  --shm-size=10gb \
  --restart unless-stopped \
  -v /mnt/ml-store:/mnt/ml-store:rw \
  -v /mnt/bonestore:/mnt/bonestore:ro \
  -e RAY_memory=$RAY_MEMORY \
  -e RAY_object_store_memory=$RAY_OBJECT_STORE \
  rayproject/ray:2.35.0-py312 \
  bash -c "ray start --address=$RAY_HEAD_ADDRESS --num-cpus=$NUM_CPUS --num-gpus=$NUM_GPUS --object-store-memory=$RAY_OBJECT_STORE && sleep infinity"

# Attendre que le worker se connecte
sleep 10

# Vérifier la connexion
echo "Ray worker started on $WORKER_NAME"
echo "Checking connection to Ray head at $RAY_HEAD_ADDRESS..."
docker exec ray-worker ray status || echo "Warning: Could not verify connection immediately"
EOF

sudo chmod +x /usr/local/bin/start-ray-worker.sh

# Créer le systemd service
sudo tee /etc/systemd/system/ray-worker.service > /dev/null <<'EOF'
[Unit]
Description=Ray Worker for ml-compute Cluster
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/start-ray-worker.sh

# Restart policy
Restart=on-failure
RestartSec=10

# Health check
ExecHealthCheck=/bin/bash -c 'docker exec ray-worker ray status >/dev/null 2>&1 || exit 1'
HealthCheckInterval=30s
HealthCheckTimeout=10s
HealthCheckStartPeriod=60s
HealthCheckRetries=3

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable ray-worker
sudo systemctl start ray-worker

# Vérifier le statut
sudo systemctl status ray-worker
docker ps | grep ray-worker
```

### 1.3 Customize for Your Machine

**Éditer le script selon les specs de votre machine** :

```bash
# Pour OnyxCortex (16 CPU, 1 GPU, 46GB RAM):
RAY_MEMORY=46000000000
NUM_CPUS=16
NUM_GPUS=1
--shm-size=10gb

# Pour Glia (20 CPU, 0 GPU, 47GB RAM):
RAY_MEMORY=47000000000
NUM_CPUS=20
NUM_GPUS=0
--shm-size=20gb

# Pour OnyxPoint (10 CPU, 1 GPU, 23GB RAM):
RAY_MEMORY=23000000000
NUM_CPUS=10
NUM_GPUS=1
--shm-size=8gb
```

### 1.4 Verify Ray Worker is Connected

```bash
# Depuis OnyxSoma, vérifier que le worker est connecté
curl http://10.0.0.44:9469/api/nodes | jq '.nodes[] | select(.status=="alive")'

# Vous devriez voir le worker dans la liste avec ses ressources
```

### 1.5 NFS Volume Mounts (Critiques pour training jobs)

**Les Ray jobs doivent accéder aux NFS volumes** :
- `/mnt/ml-store` — datasets, models, runs (partagé depuis 10.0.0.6)
- `/mnt/bonestore` — images fluoroscopiques read-only (partagé depuis 10.0.0.52)

**Le script docker run (section 1.2) include** :
```bash
-v /mnt/ml-store:/mnt/ml-store:rw \
-v /mnt/bonestore:/mnt/bonestore:ro \
```

**Vérifier que les volumes sont bien accessibles** :
```bash
# À l'intérieur du container Ray
docker exec ray-worker ls -la /mnt/ml-store/
docker exec ray-worker ls -la /mnt/bonestore/

# Devrait afficher les répertoires datasets/, models/, runs/ (ml-store)
# et les dossiers d'images (bonestore)
```

**Note**: Les NFS doivent être montés sur l'hôte **AVANT** de démarrer Ray worker :
```bash
# Sur chaque worker ML
sudo mkdir -p /mnt/ml-store /mnt/bonestore
sudo mount -t nfs 10.0.0.6:/srv/nas/ml /mnt/ml-store
sudo mount -t nfs 10.0.0.52:/srv/bones /mnt/bonestore
```

---

## 2. Monitoring Exporters

### 2.1 Node Exporter (Tous les workers)

Sur **CHAQUE machine ML** :

```bash
# Download et installer Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xzf node_exporter-1.7.0.linux-amd64.tar.gz
sudo cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/
rm -rf node_exporter-*

# Créer user Prometheus
sudo useradd -rs /bin/false prometheus 2>/dev/null || true

# Créer répertoire pour custom metrics
sudo mkdir -p /var/lib/node_exporter/textfile_collector
sudo chown -R prometheus:prometheus /var/lib/node_exporter

# Créer systemd service
sudo tee /etc/systemd/system/node-exporter.service > /dev/null <<'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/node_exporter --collector.textfile.directory=/var/lib/node_exporter/textfile_collector
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node-exporter
sudo systemctl start node-exporter

# Vérifier
curl http://localhost:9100/metrics | head -20
```

### 2.2 NVIDIA GPU Exporter (GPU workers only)

Sur **OnyxCortex et OnyxPoint** uniquement :

```bash
# Option A: Docker container (recommandé)
docker run -d \
  --name nvidia-gpu-exporter \
  --gpus all \
  --restart unless-stopped \
  -p 9445:9445 \
  utkuozdemir/nvidia_gpu_prometheus_exporter:latest

# Option B: Custom script avec nvidia-smi
sudo tee /usr/local/bin/nvidia-smi-exporter.sh > /dev/null <<'EOF'
#!/bin/bash

while true; do
  nvidia-smi --query-gpu=index,utilization.gpu,utilization.memory,memory.used,memory.free,temperature.gpu \
    --format=csv,noheader,nounits | while IFS=',' read -r index gpu_util mem_util mem_used mem_free temp; do
    
    echo "# NVIDIA GPU Metrics"
    echo "nvidia_gpu_utilization_percent{gpu=\"$index\"} $gpu_util"
    echo "nvidia_memory_utilization_percent{gpu=\"$index\"} $mem_util"
    echo "nvidia_memory_used_mb{gpu=\"$index\"} $mem_used"
    echo "nvidia_memory_free_mb{gpu=\"$index\"} $mem_free"
    echo "nvidia_gpu_temperature_celsius{gpu=\"$index\"} $temp"
  done > /var/lib/node_exporter/textfile_collector/nvidia.prom.tmp
  
  mv /var/lib/node_exporter/textfile_collector/nvidia.prom.tmp \
     /var/lib/node_exporter/textfile_collector/nvidia.prom
  
  sleep 15
done
EOF

sudo chmod +x /usr/local/bin/nvidia-smi-exporter.sh

# Systemd service pour le script
sudo tee /etc/systemd/system/nvidia-smi-exporter.service > /dev/null <<'EOF'
[Unit]
Description=NVIDIA GPU Exporter
After=node-exporter.service

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/nvidia-smi-exporter.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable nvidia-smi-exporter
sudo systemctl start nvidia-smi-exporter

# Vérifier
curl http://localhost:9445/metrics | head -20  # Option A
cat /var/lib/node_exporter/textfile_collector/nvidia.prom  # Option B
```

---

## 3. Prometheus Deployment

### 3.1 Deploy sur OnyxSoma (une seule fois)

```bash
# Sur OnyxSoma (10.0.0.44)
cd /opt/onyx/skills/ml-compute/monitoring

# Vérifier que prometheus.yml existe et a les bons targets
cat prometheus.yml

# Lancer la stack Prometheus + Grafana
docker-compose -f docker-compose-monitoring.yml up -d

# Vérifier
docker-compose -f docker-compose-monitoring.yml ps
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .job, instance: .labels.instance, health: .health}'
```

### 3.2 Add New Worker to Prometheus

Quand vous ajoutez un nouveau worker ML, mettez à jour `monitoring/prometheus.yml` :

```yaml
# Ajouter dans la section scrape_configs:

  - job_name: 'node-exporter-<worker-name>'
    static_configs:
      - targets: ['<WORKER_IP>:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: '<WorkerName>'

  # Si GPU worker, ajouter aussi:
  - job_name: 'nvidia-gpu-<worker-name>'
    static_configs:
      - targets: ['<WORKER_IP>:9445']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: '<WorkerName>-GPU'
```

Puis redémarrer Prometheus :
```bash
docker-compose -f docker-compose-monitoring.yml restart prometheus
```

---

## 4. Grafana Dashboards

### 4.1 Access Grafana

```
URL: http://10.0.0.44:3000
Username: admin
Password: admin
```

### 4.2 Pre-Built Dashboards (Import)

Dans Grafana UI:
1. Go to **Dashboards** → **Import**
2. Enter dashboard ID and click Load
3. Select Prometheus data source
4. Click Import

#### Dashboard 1: Node Exporter Full (System Metrics)
- **ID**: `1860`
- **What it shows**: CPU, Memory, Disk, Network, Processes for all nodes
- **Import link**: https://grafana.com/grafana/dashboards/1860

#### Dashboard 2: NVIDIA GPU Metrics
- **ID**: `7752`
- **What it shows**: GPU utilization, memory, temperature, power
- **Import link**: https://grafana.com/grafana/dashboards/7752

#### Dashboard 3: Prometheus Stats
- **ID**: `3662`
- **What it shows**: Prometheus health, scrape performance, storage usage
- **Import link**: https://grafana.com/grafana/dashboards/3662

### 4.3 Custom Dashboard: ml-compute Cluster Overview

Créer manuellement dans Grafana :

**Panels to create:**

1. **Cluster Status** (Stat panel)
   ```promql
   count(up{job=~"node-exporter.*"})
   ```

2. **CPU Usage by Worker** (Graph)
   ```promql
   100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
   ```

3. **Memory Available** (Graph)
   ```promql
   node_memory_MemAvailable_bytes / 1024^3
   ```

4. **GPU Utilization** (Graph)
   ```promql
   nvidia_gpu_utilization_percent
   ```

5. **Ray Workers Connected** (Stat)
   ```promql
   count(rate(container_last_seen{name="ray-worker"}[1m])) by (host)
   ```

### 4.4 Useful Query Library

**All CPU Usage**:
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage (GB)**:
```promql
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024^3
```

**Disk Usage (%)**:
```promql
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100
```

**GPU Memory (MB)**:
```promql
nvidia_memory_used_mb
```

**GPU Temperature (°C)**:
```promql
nvidia_gpu_temperature_celsius
```

**Network RX (MB/s)**:
```promql
rate(node_network_receive_bytes_total[1m]) / 1024 / 1024
```

---

## Verification Checklist

- [ ] Ray worker systemd service running: `sudo systemctl status ray-worker`
- [ ] Worker connected to cluster: `curl http://10.0.0.44:9469/api/nodes | jq`
- [ ] Node Exporter running: `curl http://localhost:9100/metrics`
- [ ] GPU Exporter running (GPU workers): `curl http://localhost:9445/metrics`
- [ ] Prometheus scraping targets: `http://10.0.0.44:9090/api/v1/targets`
- [ ] Grafana dashboards displaying data: `http://10.0.0.44:3000`

---

## Troubleshooting

**Ray worker can't connect to head node:**
```bash
# Vérifier connectivité réseau
timeout 5 bash -c "</dev/tcp/10.0.0.44/6380" && echo "Connected" || echo "Failed"

# Vérifier les logs du container
docker logs ray-worker | tail -50
```

**Node Exporter not exporting metrics:**
```bash
# Vérifier le service
sudo systemctl status node-exporter

# Vérifier les metrics
curl http://localhost:9100/metrics
```

**Prometheus not scraping target:**
```bash
# Vérifier la config
curl http://10.0.0.44:9090/api/v1/targets

# Tester la connectivité depuis Prometheus container
docker exec prometheus curl http://<WORKER_IP>:9100/metrics
```

**Grafana dashboards showing no data:**
- Vérifier que Prometheus scrape les targets (section 4.3)
- Vérifier la data source Prometheus dans Grafana settings
- Vérifier le time range (last 1h, last 24h, etc.)

---

## Future ML Workers Template

Quand vous installez un nouveau worker ML, suivez cette séquence :

```bash
# 1. SSH dans la machine
ssh onyx@<NEW_WORKER_IP>

# 2. Setup Ray Worker (section 1.2-1.3)
# 3. Setup Node Exporter (section 2.1)
# 4. Setup GPU Exporter si GPU (section 2.2)
# 5. Update Prometheus config (section 3.2)
# 6. Verify (Checklist)
```

Tous les workers sont alors **identiquement configurés** et **auto-maintenus** par systemd.
