# MedSAM2 — Temporal Propagation Server

Segmentation temporelle pour séries fluoroscopie osseuse.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness probe |
| POST | `/propagate` | Propager un masque seed sur toute une série |
| POST | `/segment` | Segmentation 2D single frame |

## Usage principal : Propagation temporelle

```bash
# Annoter 1 frame, propager sur 930 frames
curl -X POST http://10.0.0.26:9473/propagate \
  -H "Content-Type: application/json" \
  -d '{
    "frames": ["<base64 frame0>", "<base64 frame1>", ...],
    "seed_frame_idx": 0,
    "seed_mask": "<base64 binary mask PNG>",
    "score_threshold": 0.0
  }'
```

## Build & Deploy (OnyxCortex)

```bash
# Build
DOCKER_BUILDKIT=1 docker build -t medsam2-server:v1 .

# Run (modèles montés depuis /mnt/ml-store/medsam2-models/)
docker run -d --name medsam2-gpu --gpus all \
  -p 9473:9473 \
  -v /mnt/ml-store/medsam2-models:/models \
  --restart unless-stopped \
  medsam2-server:v1
```

## Checkpoints requis dans /models/

- `MedSAM2_latest.pt` — MedSAM2 fine-tuned (149MB)
- `sam2.1_hiera_tiny.pt` — SAM2 base (149MB, requis par SAM2 lib)

## VRAM

~3-4GB (Hiera Tiny). Cohabite avec SAM vit_h (:9470) sur RTX 4070 12GB.
