"""Ray cluster nodes service layer."""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

RAY_DASHBOARD_URL = os.environ.get("RAY_DASHBOARD_URL", "http://localhost:8265")


async def get_cluster_nodes() -> dict[str, Any]:
    """Get all nodes in Ray cluster with resource info via HTTP Dashboard API.

    Returns:
        Dict with nodes list and cluster status.

    Raises:
        RuntimeError: If unable to reach Ray Dashboard.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{RAY_DASHBOARD_URL}/api/v0/nodes", timeout=10.0)
            r.raise_for_status()
            data = r.json()

        raw_nodes = data.get("data", {}).get("result", {}).get("result", [])

        nodes_info = []
        total_resources = {}

        for node in raw_nodes:
            node_info = {
                "node_id": node.get("node_id", ""),
                "node_name": node.get("node_name", "unknown"),
                "node_ip": node.get("node_ip", "unknown"),
                "is_head": node.get("is_head_node", False),
                "status": node.get("state", "unknown").lower(),
                "resources": node.get("resources_total", {}),
                "available_resources": node.get("resources_total", {}),
            }
            nodes_info.append(node_info)

            # Aggregate total resources
            for key, value in node.get("resources_total", {}).items():
                total_resources[key] = total_resources.get(key, 0) + value

        return {
            "nodes": nodes_info,
            "cluster_status": "healthy" if raw_nodes else "unhealthy",
            "total_resources": total_resources,
        }
    except Exception as e:
        logger.error(f"Failed to get cluster nodes: {e}")
        raise RuntimeError(f"Failed to query cluster: {e}")


async def get_resource_summary() -> dict[str, Any]:
    """Get summary of cluster resources (CPU, GPU, memory).

    Returns:
        Aggregated resource info.
    """
    try:
        result = await get_cluster_nodes()

        total_cpu = 0.0
        total_gpu = 0.0
        total_memory = 0.0
        available_cpu = 0.0
        available_gpu = 0.0
        available_memory = 0.0

        for node in result["nodes"]:
            resources = node.get("resources", {})
            available = node.get("available_resources", {})

            total_cpu += resources.get("CPU", 0)
            total_gpu += resources.get("GPU", 0)
            total_memory += resources.get("memory", 0)

            available_cpu += available.get("CPU", 0)
            available_gpu += available.get("GPU", 0)
            available_memory += available.get("memory", 0)

        return {
            "total": {
                "cpu": total_cpu,
                "gpu": total_gpu,
                "memory_bytes": total_memory,
            },
            "available": {
                "cpu": available_cpu,
                "gpu": available_gpu,
                "memory_bytes": available_memory,
            },
            "utilization": {
                "cpu_percent": (100 * (total_cpu - available_cpu) / total_cpu if total_cpu > 0 else 0),
                "gpu_percent": (100 * (total_gpu - available_gpu) / total_gpu if total_gpu > 0 else 0),
                "memory_percent": (100 * (total_memory - available_memory) / total_memory if total_memory > 0 else 0),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get resource summary: {e}")
        return {
            "total": {"cpu": 0, "gpu": 0, "memory_bytes": 0},
            "available": {"cpu": 0, "gpu": 0, "memory_bytes": 0},
            "utilization": {"cpu_percent": 0, "gpu_percent": 0, "memory_percent": 0},
        }
