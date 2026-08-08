#!/bin/bash

# Install onyx-sdk from wheel if available
if ls /app/onyx_sdk*.whl 1> /dev/null 2>&1; then
  echo "Installing onyx-sdk from wheel..."
  pip install --no-cache-dir /app/onyx_sdk*.whl
fi

# Start the FastAPI application
exec python -m src.main
