FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY config/ config/ 2>/dev/null || true
COPY models/ models/ 2>/dev/null || true

# Create necessary directories
RUN mkdir -p /opt/onyx/skills/ml-compute/{config,models}

# Expose port
EXPOSE 9469

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9469/health || exit 1

# Run FastAPI app
CMD ["python", "-m", "src.main"]
