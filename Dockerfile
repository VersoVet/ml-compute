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

# Create necessary directories (will be mounted or auto-created at runtime)
RUN mkdir -p /app/config /app/models

# Expose port
EXPOSE 9469

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9469/health || exit 1

# Run FastAPI app
CMD ["python", "-m", "src.main"]
