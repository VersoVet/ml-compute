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

# Copy onyx-sdk wheel if available (will be present when Forge deploys)
COPY onyx_sdk*.whl ./

# Copy source code
COPY src/ src/

# Create necessary directories (will be mounted or auto-created at runtime)
RUN mkdir -p /app/config /app/models

# Create entrypoint script to install onyx-sdk if available
RUN echo '#!/bin/bash\n\
if ls /app/onyx_sdk*.whl 1> /dev/null 2>&1; then\n\
  echo "Installing onyx-sdk from wheel..."\n\
  pip install --no-cache-dir /app/onyx_sdk*.whl\n\
fi\n\
exec python -m src.main' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 9469

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9469/health || exit 1

# Run FastAPI app via entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
