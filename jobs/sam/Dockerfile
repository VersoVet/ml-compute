FROM pytorch/pytorch:2.1-cuda12.1-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install SAM and dependencies
RUN pip install --no-cache-dir segment-anything fastapi uvicorn python-multipart

# Copy SAM model download script
COPY sam_server.py /app/sam_server.py

# Create model directory
RUN mkdir -p /models

# Expose port
EXPOSE 9470

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:9470/health || exit 1

# Run SAM server
CMD ["python", "/app/sam_server.py"]
