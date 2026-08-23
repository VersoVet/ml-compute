FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and system dependencies upfront
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Increase memory limit for pip (important for large packages)
ENV PIP_NO_CACHE_DIR=1

# Install Python dependencies (pre-compiled)
# Using specific wheel versions to avoid compilation
# Lock numpy<2.0.0 for compatibility with segment-anything
RUN pip install --upgrade pip setuptools wheel && \
    pip install "numpy<2.0.0" && \
    pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121 && \
    pip install segment-anything fastapi uvicorn python-multipart pillow

# Copy SAM server code
COPY sam_server.py /app/sam_server.py

# Create model directory
RUN mkdir -p /models

# Expose port
EXPOSE 9470

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD curl -f http://localhost:9470/health || exit 1

# Run SAM server
CMD ["python3", "/app/sam_server.py"]
