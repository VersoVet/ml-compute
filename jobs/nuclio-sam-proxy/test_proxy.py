#!/usr/bin/env python3
"""Test script for SAM proxy function."""

import base64
import json
import sys
from pathlib import Path

import requests

# Configuration
PROXY_URL = "http://10.0.0.59:9070/segment"
ML_COMPUTE_HEALTH = "http://10.0.0.44:9469/api/serve/sam/health"


def test_backend_available():
    """Test that ml-compute backend is available."""
    print(f"[1/3] Testing backend availability: {ML_COMPUTE_HEALTH}")
    try:
        response = requests.get(ML_COMPUTE_HEALTH, timeout=10)
        if response.status_code == 200:
            print(f"  ✓ Backend is available")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"  ✗ Backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Cannot connect to backend: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_proxy_endpoint():
    """Test the proxy endpoint with a dummy image."""
    print(f"\n[2/3] Testing proxy endpoint: {PROXY_URL}")

    # Create a minimal test image (1x1 pixel, red)
    # This is a base64-encoded 1x1 PNG
    dummy_image_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd3PcAAAACElEQVQI12"
        "NgAAAAAgABSK+kcQAAAAASUVORK5CYII="
    )

    request_data = {
        "image_base64": dummy_image_base64,
        "points": [[0, 0]],
        "negative_points": None,
        "box": None,
    }

    try:
        print(f"  Sending request with test image...")
        response = requests.post(
            PROXY_URL,
            json=request_data,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )

        print(f"  Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Proxy returned success")
            print(f"  Result: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"  ✗ Proxy returned {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            return False

    except requests.exceptions.Timeout:
        print(f"  ✗ Request timeout (backend may be busy)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Cannot connect to proxy: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_with_real_image(image_path: str):
    """Test proxy with a real image file."""
    print(f"\n[3/3] Testing with real image: {image_path}")

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode("utf-8")

        request_data = {
            "image_base64": image_base64,
            "points": [[100, 100], [200, 150]],
            "negative_points": [[150, 100]],
            "box": None,
        }

        print(f"  Sending request with real image ({len(image_data)} bytes)...")
        response = requests.post(
            PROXY_URL,
            json=request_data,
            timeout=60,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Proxy returned success")
            print(f"  Masks: {len(result.get('masks', []))} masks generated")
            return True
        else:
            print(f"  ✗ Proxy returned {response.status_code}")
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
    print("SAM Proxy Test Suite")
    print("=" * 60)

    tests = [
        test_backend_available(),
        test_proxy_endpoint(),
    ]

    # Check if a test image is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        tests.append(test_with_real_image(image_path))

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
