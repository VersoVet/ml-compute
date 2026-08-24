"""Nuclio handler for SAM proxy — CVAT interactor protocol.

CVAT interactors work in 2 phases:
1. Server (this handler): receive image → return SAM embeddings as blob
2. Client (browser): CVAT decodes embeddings with ONNX decoder for interactive segmentation

This handler simply forwards the image to SAM GPU server's /api/embed endpoint.
"""

import json
import os

import requests

SAM_GPU_URL = os.environ.get("SAM_GPU_URL", "http://10.0.0.26:9470")
SAM_MODEL_NAME = os.environ.get("SAM_MODEL_NAME", "vit_b")

_last_model = None


def init_context(context):
    """Initialize handler context."""
    context.logger.info(f"SAM embed proxy -> {SAM_GPU_URL} (model: {SAM_MODEL_NAME})")


def handler(context, event):
    """Forward image to SAM server, return embeddings blob to CVAT.

    CVAT sends: {"image": "<base64 image>"}
    SAM returns: {"blob": "<base64 embeddings>"}
    CVAT frontend decodes blob with ONNX decoder for interactive masking.
    """
    global _last_model

    if isinstance(event.body, bytes):
        data = json.loads(event.body.decode())
    elif isinstance(event.body, str):
        data = json.loads(event.body)
    elif isinstance(event.body, dict):
        data = event.body
    else:
        data = json.loads(str(event.body))

    # Switch model if needed (first call or different model)
    if _last_model != SAM_MODEL_NAME:
        try:
            resp = requests.post(
                f"{SAM_GPU_URL}/switch-model",
                json={"model": SAM_MODEL_NAME},
                timeout=30,
            )
            if resp.status_code == 200:
                _last_model = SAM_MODEL_NAME
                context.logger.info(f"Model switched to {SAM_MODEL_NAME}")
        except Exception as e:
            context.logger.warning(f"Model switch failed: {e}")

    # Forward to SAM /api/embed — returns {"blob": "<base64 embeddings>"}
    try:
        resp = requests.post(
            f"{SAM_GPU_URL}/api/embed",
            json=data,
            timeout=60,
        )
        context.logger.info(f"SAM embed: HTTP {resp.status_code}")
        return context.Response(
            body=resp.text,
            headers={},
            content_type="application/json",
            status_code=resp.status_code,
        )
    except requests.exceptions.Timeout:
        context.logger.error("SAM embed timeout")
        return context.Response(
            body=json.dumps({"error": "SAM timeout"}),
            headers={},
            content_type="application/json",
            status_code=504,
        )
    except Exception as e:
        context.logger.error(f"SAM embed failed: {e}")
        return context.Response(
            body=json.dumps({"error": str(e)}),
            headers={},
            content_type="application/json",
            status_code=503,
        )
