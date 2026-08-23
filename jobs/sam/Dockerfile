# syntax=docker/dockerfile:1
# SAM Inference Server
# Base: PyTorch 2.4.1 + CUDA 12.4 + cuDNN 9 + Python 3.11 pré-installés
# Build time: ~2-3 min (vs 25+ min avec nvidia/cuda)
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

# BuildKit cache mount: pip téléchargé une seule fois sur la machine de build
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

RUN mkdir -p /models

COPY sam_server.py /app/sam_server.py

EXPOSE 9470

# Healthcheck sur /ready (retourne 503 tant que le modèle charge)
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:9470/ready || exit 1

CMD ["python3", "/app/sam_server.py"]
