"""Ray cluster nodes service layer."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def get_cluster_nodes() -> dict[str, Any]:
    """Get all nodes in Ray cluster with resource info.

    Returns:
        Dict with nodes list and cluster status.

    Raises:
        RuntimeError: If Ray is not initialized.
    """
    try:
        import ray

        if not ray.is_initialized():
            raise RuntimeError("Ray cluster not initialized")

        nodes = ray.nodes()
        resources = ray.cluster_resources()
        available_resources = ray.available_resources()

        nodes_info = []
        for node in nodes:
            node_info = {
                "node_id": node["NodeID"],
                "node_name": node.get("NodeName", "unknown"),
                "node_ip": node.get("NodeManagerAddress", "unknown"),
                "is_head": node["IsHead"],
                "status": "alive",
                "resources": node.get("Resources", {}),
                "available_resources": node.get("AvailableResources", {}),
            }
            nodes_info.append(node_info)

        return {
            "nodes": nodes_info,
            "cluster_status": "healthy" if len(nodes) > 0 else "unhealthy",
            "total_resources": resources,
        }
    except RuntimeError as e:
        logger.error(f"Failed to get cluster nodes: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting cluster nodes: {e}")
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
                "cpu_percent": (
                    100 * (total_cpu - available_cpu) / total_cpu
                    if total_cpu > 0
                    else 0
                ),
                "gpu_percent": (
                    100 * (total_gpu - available_gpu) / total_gpu
                    if total_gpu > 0
                    else 0
                ),
                "memory_percent": (
                    100 * (total_memory - available_memory) / total_memory
                    if total_memory > 0
                    else 0
                ),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get resource summary: {e}")
        return {
            "total": {"cpu": 0, "gpu": 0, "memory_bytes": 0},
            "available": {"cpu": 0, "gpu": 0, "memory_bytes": 0},
            "utilization": {"cpu_percent": 0, "gpu_percent": 0, "memory_percent": 0},
        }
