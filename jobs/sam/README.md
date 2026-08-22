# SAM (Segment Anything Model) Deployment via Ray Serve

Deploy the Segment Anything Model (vit_b) on OnyxCortex GPU worker.

## Prerequisites

- Ray cluster running (tested on Ray 2.35.0)
- Model file: `~/sam-gpu/sam_vit_b_01ec64.pth` on OnyxCortex
- GPU: RTX 4070 SUPER (12GB VRAM)
- Python packages: `segment-anything`, `opencv-python`, `Pillow`

## Usage

### Option 1: Deploy as Ray Job

```bash
# Submit deployment job to Ray cluster
curl -X POST http://10.0.0.44:9469/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sam-serve-deploy",
    "entrypoint": "python /opt/onyx/skills/ml-compute/jobs/sam/deploy_serve.py --ray-address http://10.0.0.44:8265 --serve-port 9470",
    "runtime_env": {
      "pip": [
        "segment-anything",
        "opencv-python",
        "Pillow",
        "torch",
        "torchvision",
        "numpy"
      ],
      "working_dir": "/opt/onyx/skills/ml-compute"
    }
  }'
```

### Option 2: Deploy as Systemd Service

```bash
# Create systemd service on OnyxSoma
sudo tee /etc/systemd/system/sam-serve.service > /dev/null <<'EOF'
[Unit]
Description=SAM Ray Serve Deployment
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=onyx
WorkingDirectory=/opt/onyx/skills/ml-compute
Environment="RAY_HEAD_ADDRESS=http://10.0.0.44:8265"
ExecStart=/usr/bin/python3 /opt/onyx/skills/ml-compute/jobs/sam/deploy_serve.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now sam-serve
```

## API Endpoint

**URL**: `POST http://10.0.0.44:9470/api/interact`

**Request body**:
```json
{
  "image": "base64_encoded_image_or_uint8_array",
  "positive_points": [[x1, y1], [x2, y2]],
  "negative_points": [[x3, y3]],
  "prompt_labels": [1, 1, 0]
}
```

**Response**:
```json
{
  "mask": "base64_encoded_png_mask",
  "area": 12345,
  "status": "success",
  "image_shape": [1080, 1920, 3]
}
```

## Testing

```bash
# Test with a sample image
python3 <<'PYTHON'
import base64
import cv2
import requests

# Load test image
image = cv2.imread("test.jpg")
_, buffer = cv2.imencode(".png", image)
image_base64 = base64.b64encode(buffer).decode("utf-8")

# Send request
response = requests.post(
    "http://10.0.0.44:9470/api/interact",
    json={
        "image": image_base64,
        "positive_points": [[100, 100], [200, 200]],
        "negative_points": []
    }
)

print(response.json())
PYTHON
```

## Scheduling

The deployment uses `num_gpus=1` which schedules it to run on OnyxCortex (the GPU worker).

- Head node (OnyxSoma): No GPUs reserved → runs head infrastructure
- Worker (OnyxCortex): 1 GPU reserved → runs SAM predictor

## Notes

- Model loading takes ~2-3 seconds first time
- Predictions take ~500ms-1s depending on image size
- Max image size: 1024x1024 recommended for RTX 4070 SUPER
- Keep alive: Ray Serve keeps the deployment alive permanently
