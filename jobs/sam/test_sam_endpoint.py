#!/usr/bin/env python3
"""Test script for SAM inference endpoint via ml-compute API."""

import base64
import json
import sys
from pathlib import Path

import requests

# Configuration
ML_COMPUTE_URL = "http://10.0.0.44:9469"
SAM_ENDPOINT = f"{ML_COMPUTE_URL}/api/serve/sam/interact"
SAM_HEALTH = f"{ML_COMPUTE_URL}/api/serve/sam/health"
TIMEOUT = 60.0


def test_health():
    """Test SAM health endpoint."""
    print("[1/3] Testing SAM health endpoint...")
    try:
        response = requests.get(SAM_HEALTH, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SAM is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Model: {data.get('model')}")
            print(f"  Device: {data.get('device')}")
            return True
        else:
            print(f"  ✗ Health check returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Cannot connect to ml-compute: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def create_dummy_image():
    """Create a minimal test image (1x1 pixel, red)."""
    # This is a base64-encoded 1x1 PNG (transparent)
    return (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd3PcAAAACElEQVQI12"
        "NgAAAAAgABSK+kcQAAAAASUVORK5CYII="
    )


def test_segmentation_dummy():
    """Test segmentation with a dummy image."""
    print("\n[2/3] Testing segmentation with dummy image...")

    request_data = {
        "image_base64": create_dummy_image(),
        "points": [[0, 0]],
        "negative_points": None,
        "box": None,
    }

    try:
        print(f"  Sending request to {SAM_ENDPOINT}...")
        response = requests.post(
            SAM_ENDPOINT,
            json=request_data,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        print(f"  Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Segmentation successful")
            print(f"  Status: {result.get('status')}")
            if result.get('masks'):
                print(f"  Masks: {len(result['masks'])} masks generated")
            if result.get('iou_predictions'):
                print(f"  IoU: {result['iou_predictions']}")
            return True
        else:
            print(f"  ✗ Segmentation failed with {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"  ✗ Request timeout (backend may be busy)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Cannot connect to SAM endpoint: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_segmentation_real_image(image_path: str):
    """Test segmentation with a real image file."""
    print(f"\n[3/3] Testing with real image: {image_path}")

    try:
        # Read image
        with open(image_path, "rb") as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode("utf-8")
        print(f"  Image size: {len(image_data)} bytes")

        # Create segmentation request
        request_data = {
            "image_base64": image_base64,
            "points": [[100, 100], [200, 150]],  # Example points
            "negative_points": [[150, 100]],      # Example negative point
            "box": None,
        }

        print(f"  Sending request with {len(request_data['points'])} points...")
        response = requests.post(
            SAM_ENDPOINT,
            json=request_data,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        print(f"  Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Segmentation successful")
            print(f"  Status: {result.get('status')}")
            if result.get('masks'):
                print(f"  Masks: {len(result['masks'])} masks generated")
                print(f"  First mask size: {len(result['masks'][0]) if result['masks'] else 'N/A'}")
            if result.get('iou_predictions'):
                print(f"  IoU predictions: {result['iou_predictions']}")
            return True
        else:
            print(f"  ✗ Segmentation failed with {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except FileNotFoundError:
        print(f"  ⚠ Image file not found: {image_path}")
        print(f"    Skipping real image test")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SAM ml-compute Endpoint Test Suite")
    print("=" * 60)
    print(f"Target: {ML_COMPUTE_URL}")
    print(f"Endpoint: {SAM_ENDPOINT}")
    print("")

    tests = [
        test_health(),
        test_segmentation_dummy(),
    ]

    # Check if a test image is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        tests.append(test_segmentation_real_image(image_path))
    else:
        print("\nNote: To test with a real image, run:")
        print("  python3 test_sam_endpoint.py /path/to/image.jpg")

    # Summary
    print("\n" + "=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
