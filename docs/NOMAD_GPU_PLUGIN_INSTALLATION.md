# Nomad GPU Plugin Installation Guide

## ⚠️ CRITICAL: Manual Installation Required

The NVIDIA GPU plugin for Nomad is an external binary that must be manually installed on each worker node. This cannot be automated via jobs because Nomad needs to restart to load the plugin.

## Prerequisites

- SSH access to worker nodes (root)
- NVIDIA drivers installed (`nvidia-smi` working)
- Nomad client binary already installed

## Installation Steps

### Step 1: Download NVIDIA GPU Plugin

**On each worker node (OnyxCortex + OnyxPoint):**

```bash
ssh root@10.0.0.26   # OnyxCortex
# or
ssh root@10.0.0.86   # OnyxPoint
```

### Step 2: Create plugin directory (if not exists)

```bash
sudo mkdir -p /opt/nomad/plugins
cd /opt/nomad/plugins
```

### Step 3: Download and install NVIDIA GPU plugin

```bash
# Download the latest NVIDIA GPU plugin (Nomad 1.9.0 compatible)
# Check: https://github.com/hashicorp/nomad-gpu-nvidia/releases

# Example for v1.6.0 (compatible with Nomad 1.9.0):
wget https://releases.hashicorp.com/nomad-device-nvidia-gpu/1.6.0/nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip

# Unzip
unzip nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip

# Verify plugin is executable
chmod +x nomad-device-nvidia-gpu
ls -la nomad-device-nvidia-gpu
```

### Step 4: Update Nomad client configuration

**Add GPU plugin config to `/etc/nomad.d/nomad.hcl` or create `/etc/nomad.d/gpu-plugin.hcl`:**

```hcl
# GPU Device Plugin Configuration
plugin "nvidia_gpu" {
  enabled = true
  
  config {
    # Optional: Fingerprint interval (default: 30s)
    fingerprint_period = "30s"
    
    # Optional: Enable memory management
    manage_nvidia_display_device = false
  }
}
```

### Step 5: Restart Nomad client

```bash
sudo systemctl restart nomad

# Wait for client to re-register
sleep 10

# Verify Nomad is active
sudo systemctl status nomad

# Check logs for GPU detection
sudo journalctl -u nomad -n 50
```

### Step 6: Verify GPU detection

**On Nomad server (OnyxSoma):**

```bash
# Check if GPUs appear in node status
nomad node status -json | jq '.NodeResources.Devices[] | select(.Type=="gpu")'

# Or via HTTP API:
curl http://10.0.0.44:4646/v1/node/<node-id> | jq '.NodeResources.Devices'
```

**Via ml-compute API:**

```bash
curl http://10.0.0.44:9469/api/nomad/gpu-status | jq .

# Expected output:
# [
#   {
#     "node_name": "onyxcortex",
#     "num_gpus": 1,           # ← Should be 1 after installation
#     "available_gpus": 1,
#     "in_use": []
#   },
#   ...
# ]
```

## Troubleshooting

### Plugin not detected

```bash
# Check if plugin binary exists and is executable
ls -la /opt/nomad/plugins/nomad-device-nvidia-gpu

# Check Nomad logs for plugin load errors
sudo journalctl -u nomad | grep -i "nvidia\|plugin\|gpu" | tail -20
```

### GPU not detected even with plugin installed

1. **Verify NVIDIA drivers:**
   ```bash
   nvidia-smi
   lsmod | grep nvidia
   ```

2. **Check NVIDIA device permissions:**
   ```bash
   ls -la /dev/nvidia*
   ```

3. **Restart Nomad again:**
   ```bash
   sudo systemctl restart nomad
   sleep 30
   nomad node status -verbose | grep -A 5 "Device"
   ```

### Fingerprinting slow

GPU fingerprinting may take up to 60 seconds. Check logs:

```bash
sudo journalctl -u nomad -f | grep -i "fingerprint\|device"
```

## Automated Deployment (Optional)

If you have Ansible or similar, you can use the ansible-nomad role:

```bash
# Example Ansible playbook
- hosts: nomad_workers
  tasks:
    - name: Download NVIDIA GPU plugin
      get_url:
        url: https://releases.hashicorp.com/nomad-device-nvidia-gpu/1.6.0/nomad-device-nvidia-gpu_1.6.0_linux_amd64.zip
        dest: /tmp/nomad-device-nvidia-gpu.zip

    - name: Install plugin
      unarchive:
        src: /tmp/nomad-device-nvidia-gpu.zip
        dest: /opt/nomad/plugins/
        remote_src: yes

    - name: Add GPU config
      copy:
        content: |
          plugin "nvidia_gpu" {
            enabled = true
          }
        dest: /etc/nomad.d/gpu-plugin.hcl

    - name: Restart Nomad
      service:
        name: nomad
        state: restarted
```

## Verification Checklist

- [ ] SSH to OnyxCortex (10.0.0.26)
- [ ] Download NVIDIA GPU plugin binary
- [ ] Place in `/opt/nomad/plugins/`
- [ ] Add GPU config to Nomad
- [ ] Restart Nomad client
- [ ] Verify `nomad node status` shows GPU
- [ ] Repeat for OnyxPoint (10.0.0.86)
- [ ] Verify via `curl http://10.0.0.44:9469/api/nomad/gpu-status`

## Next Steps After GPU Detection

Once GPUs are detected:

```bash
# 1. Deploy SAM via Nomad
curl -X POST http://10.0.0.44:9469/api/serve/sam/deploy

# 2. Verify allocation
curl http://10.0.0.44:9469/api/serve/sam/status | jq .

# 3. Check GPU allocation
curl http://10.0.0.44:9469/api/nomad/gpu-status | jq .

# 4. Test segmentation
curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"...", "points":[[100,200]]}'
```

---

**Status**: Awaiting manual installation on workers

**Timeline**: Once completed → GPU detection (~30s) → SAM operational ✓
