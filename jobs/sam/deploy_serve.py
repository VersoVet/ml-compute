#!/usr/bin/env python3
"""Deploy SAM via Ray Serve on existing Ray cluster.

This script:
1. Connects to Ray head at RAY_HEAD_ADDRESS
2. Starts Ray Serve on the cluster
3. Deploys SAM with num_gpus=1 (will run on OnyxCortex GPU worker)
4. Exposes HTTP endpoint on port 9470
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import ray
from ray import serve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Deploy SAM on Ray cluster."""
    parser = argparse.ArgumentParser(description="Deploy SAM via Ray Serve")
    parser.add_argument(
        "--ray-address",
        default=os.environ.get("RAY_HEAD_ADDRESS", "http://10.0.0.44:8265"),
        help="Ray dashboard address (default: http://10.0.0.44:8265)",
    )
    parser.add_argument(
        "--serve-port",
        type=int,
        default=9470,
        help="Ray Serve HTTP port (default: 9470)",
    )
    parser.add_argument(
        "--deployment-name",
        default="sam-vit-b",
        help="Deployment name (default: sam-vit-b)",
    )
    args = parser.parse_args()

    try:
        # Initialize Ray (will connect to existing cluster)
        logger.info(f"Connecting to Ray cluster at {args.ray_address}")
        ray.init(address="auto", ignore_reinit_error=True)
        logger.info("✓ Connected to Ray cluster")

        # Initialize Ray Serve
        logger.info(f"Starting Ray Serve on port {args.serve_port}")
        serve.start(http_options={"host": "0.0.0.0", "port": args.serve_port})
        logger.info(f"✓ Ray Serve started on port {args.serve_port}")

        # Import and deploy SAM
        # Use absolute import to ensure we get the right module
        sys.path.insert(0, "/opt/onyx/skills/ml-compute")
        from src.modules.sam import SAMDeployment

        logger.info(f"Deploying {args.deployment_name} with num_gpus=1")
        serve.run(
            SAMDeployment.bind(),
            name=args.deployment_name,
            route_prefix="/api/interact",
        )

        logger.info(f"✓ SAM deployment active at http://0.0.0.0:{args.serve_port}/api/interact")
        logger.info("Deployment ready! Send POST requests with:")
        logger.info("""
  {
    "image": "base64_encoded_image_or_array",
    "positive_points": [[x1, y1], [x2, y2], ...],
    "negative_points": [[x3, y3], ...]
  }
        """)

        # Keep serving
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")

    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        try:
            serve.shutdown()
            ray.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
