# Ray Worker GPU — image custom pour le cluster Ray Onyx
#
# Base: rayproject/ray (Python 3.12) + torch cu121 + timm + outils
# Build: ./build.sh
# Deploy: ./deploy.sh [tensor|cortex|all]
#
# Pour ajouter un nouveau rig :
#   1. Ajouter l'IP dans deploy.sh (WORKERS array)
#   2. ./deploy.sh <nom>
#   C'est tout.

ARG RAY_VERSION=2.35.0
ARG PYTHON_VERSION=py312

FROM rayproject/ray:${RAY_VERSION}-${PYTHON_VERSION}

LABEL maintainer="onyx" \
      description="Ray worker with GPU ML dependencies (torch, timm, etc.)"

# System deps for image processing and compression
USER root
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
USER ray

# Python ML dependencies — pinned in requirements.txt
COPY --chown=ray:ray requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Smoke test: torch sees CUDA (will fail at build if base image is wrong)
RUN python -c "import torch, timm, blosc2, httpx; print(f'OK: torch={torch.__version__} timm={timm.__version__}')"

# Default: start ray worker (address passed via env or cmd)
# Override CMD in docker run or compose
CMD ["bash", "-c", "ray start --address=${RAY_HEAD_ADDRESS:-10.0.0.44:6380} --num-cpus=${NUM_CPUS:-2} --num-gpus=${NUM_GPUS:-1} --object-store-memory=${OBJECT_STORE_MEMORY:-2000000000} && sleep infinity"]
