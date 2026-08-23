"""Nuclio handler for SAM proxy to ml-compute backend."""

import json
import logging
from typing import Any

import requests

# Configuration
SAM_BACKEND_URL = "http://10.0.0.44:9469/api/serve/sam/interact"
TIMEOUT = 60.0

logger = logging.getLogger(__name__)


def handler(context: Any, event: Any) -> dict:
    """Forward segmentation requests to ml-compute SAM backend.

    Receives HTTP POST with segmentation request, forwards to ml-compute,
    returns SAM segmentation results to caller.

    Args:
        context: Nuclio context (logging, env vars)
        event: Nuclio event object containing HTTP request

    Returns:
        dict with status and segmentation results
    """
    try:
        # Parse request body
        if isinstance(event.body, str):
            request_data = json.loads(event.body)
        else:
            request_data = event.body

        logger.info(f"Proxy request: image_size={len(request_data.get('image_base64', ''))}, "
                    f"points={len(request_data.get('points', []))}")

        # Forward to SAM backend
        response = requests.post(
            SAM_BACKEND_URL,
            json=request_data,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        # Check response status
        if response.status_code != 200:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return {
                "statusCode": response.status_code,
                "body": json.dumps({
                    "status": "error",
                    "detail": f"Backend returned {response.status_code}",
                }),
            }

        # Success
        result = response.json()
        logger.info(f"Segmentation succeeded: {len(result.get('masks', []))} masks")

        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {"Content-Type": "application/json"},
        }

    except requests.exceptions.Timeout:
        logger.error(f"Backend timeout after {TIMEOUT}s")
        return {
            "statusCode": 504,
            "body": json.dumps({
                "status": "error",
                "detail": "Backend timeout",
            }),
        }

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to backend: {e}")
        return {
            "statusCode": 503,
            "body": json.dumps({
                "status": "error",
                "detail": f"Cannot connect to backend at {SAM_BACKEND_URL}",
            }),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "status": "error",
                "detail": "Invalid JSON in request",
            }),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "detail": f"Internal error: {str(e)}",
            }),
        }
