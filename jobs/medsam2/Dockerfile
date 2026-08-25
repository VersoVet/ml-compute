# MedSAM2 Temporal Propagation Server
# Base: PyTorch 2.5.1 + CUDA 12.4 (SAM2 requires PyTorch >= 2.5)
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install SAM2 from Facebook Research
RUN pip install --no-cache-dir \
    git+https://github.com/facebookresearch/sam2.git \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0 \
    pillow>=10.0.0 \
    numpy>=1.26.0

RUN mkdir -p /models

COPY medsam2_server.py /app/medsam2_server.py

EXPOSE 9473

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:9473/ready || exit 1

CMD ["python3", "/app/medsam2_server.py"]
