# ml-compute Monitoring Stack

Complete monitoring solution for ml-compute Ray cluster with Prometheus + Grafana.

## Components

### Prometheus
- **Central metrics collector** running on OnyxSoma (10.0.0.44:9090)
- Scrapes metrics from all cluster nodes every 30 seconds
- Stores metrics for 30 days
- Provides REST API for queries

### Grafana
- **Visualization dashboards** running on OnyxSoma (10.0.0.44:3000)
- Pre-configured Prometheus data source
- Supports custom dashboards and alerts

### Node Exporter
- Installed on all ML workers (OnyxCortex, Glia, OnyxPoint)
- Collects system metrics: CPU, memory, disk, network, processes
- Exposes metrics on port 9100

### NVIDIA GPU Exporter
- Installed on GPU machines (OnyxCortex, OnyxPoint)
- Collects GPU metrics: utilization, memory, temperature
- Exposes metrics on port 9445

## Quick Start

### 1. Install Exporters on ML Workers

See `SETUP.md` → Section 1 for detailed installation on:
- OnyxCortex (10.0.0.26) — GPU + Node exporter
- Glia (10.0.0.8) — Node exporter only
- OnyxPoint (10.0.0.86) — GPU + Node exporter

### 2. Deploy Monitoring on OnyxSoma

```bash
cd /opt/onyx/skills/ml-compute/monitoring
docker-compose -f docker-compose-monitoring.yml up -d
```

### 3. Access Dashboards

- **Prometheus**: http://10.0.0.44:9090
- **Grafana**: http://10.0.0.44:3000 (admin/admin)

## Monitored Machines

| Machine | Role | Exporters | Metrics |
|---------|------|-----------|---------|
| **OnyxSoma** (10.0.0.44) | Head/Admin | Node | CPU, Memory, Disk, Network |
| **OnyxCortex** (10.0.0.26) | GPU Worker | Node + NVIDIA | CPU, Memory, Disk, GPU (RTX 4070 SUPER) |
| **Glia** (10.0.0.8) | CPU Worker | Node | CPU, Memory, Disk, Network |
| **OnyxPoint** (10.0.0.86) | Legacy/Archive | Node + NVIDIA | CPU, Memory, Disk, GPU (T1000 8GB) |

## Configuration Files

- `prometheus.yml` — Scrape targets and job definitions
- `docker-compose-monitoring.yml` — Prometheus + Grafana containers
- `grafana/provisioning/datasources/prometheus.yml` — Auto-configure data source
- `SETUP.md` — Complete installation guide

## Dashboards

### Built-in (Grafana Lab)
- **1860**: Node Exporter Full (system metrics)
- **7752**: NVIDIA GPU Metrics (GPU utilization, memory, temp)

### Custom (to create)
- Cluster overview (all workers summary)
- Ray jobs status and performance
- GPU utilization per worker
- Resource allocation vs availability

## Metrics Collected

### Node Exporter Metrics
- `node_cpu_seconds_total` — CPU time per mode (user, system, idle, etc.)
- `node_memory_MemAvailable_bytes` — Available memory
- `node_memory_MemTotal_bytes` — Total memory
- `node_filesystem_avail_bytes` — Disk available space
- `node_network_receive_bytes_total` — Network RX
- `node_network_transmit_bytes_total` — Network TX
- And 100+ more system metrics...

### NVIDIA GPU Exporter Metrics
- `nvidia_gpu_utilization_percent` — GPU compute utilization
- `nvidia_memory_utilization_percent` — GPU memory utilization
- `nvidia_memory_used_mb` — GPU VRAM used
- `nvidia_memory_free_mb` — GPU VRAM free
- `nvidia_gpu_temperature_celsius` — GPU temperature

### Ray Metrics (from Dashboard API)
- `ray_dashboard_job_status` — Job submission status
- Cluster health and node state

## Query Examples

**GPU Memory Usage on OnyxCortex**:
```promql
nvidia_memory_used_mb{instance="OnyxCortex-GPU"}
```

**CPU Utilization (all workers)**:
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Available Memory on Glia**:
```promql
node_memory_MemAvailable_bytes{instance="Glia"} / 1024^3
```

**GPU Temperature on OnyxPoint**:
```promql
nvidia_gpu_temperature_celsius{instance="OnyxPoint-GPU"}
```

## Troubleshooting

See `SETUP.md` → Section 7 for common issues and solutions.

## Maintenance

- **Backup Grafana dashboards**: See `SETUP.md` → Section 8
- **Retention policy**: Default 30 days, configurable
- **Restart monitoring**: `docker-compose -f docker-compose-monitoring.yml restart`

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Node Exporter Metrics](https://github.com/prometheus/node_exporter)
- [NVIDIA GPU Exporter](https://github.com/utkuozdemir/nvidia_gpu_prometheus_exporter)
