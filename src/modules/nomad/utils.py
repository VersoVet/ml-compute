"""Utility functions for Nomad job specification building."""

from typing import Any

from src.modules.nomad.models import NomadJobRequest


def build_job_spec(request: NomadJobRequest) -> dict[str, Any]:
    """Build Nomad job specification from request.

    Args:
        request: Job request.

    Returns:
        Nomad job spec dictionary.
    """
    task_group_constraints = request.constraints[0] if request.constraints else None

    if request.driver == "docker":
        driver_config: dict[str, Any] = {
            "image": request.image or "ubuntu:22.04",
            "command": "sh",
            "args": ["-c", request.command],
        }
        if request.volumes:
            driver_config["mounts"] = [
                {"type": "bind", "target": target, "source": source} for source, target in request.volumes.items()
            ]
    else:
        driver_config = {
            "command": "sh",
            "args": ["-c", request.command],
        }

    task_resources = {
        "CPU": task_group_constraints.cpu_mhz if task_group_constraints else 1000,
        "MemoryMB": task_group_constraints.memory_mb if task_group_constraints else 512,
    }

    task: dict[str, Any] = {
        "Name": request.name,
        "Driver": request.driver,
        "Config": driver_config,
        "Resources": task_resources,
        "Env": request.env_vars if request.env_vars else {},
    }

    if request.timeout_seconds > 0:
        task["Timeout"] = f"{request.timeout_seconds}s"

    return {
        "ID": request.name,
        "Name": request.name,
        "Type": request.job_type,
        "Priority": request.priority.value,
        "Datacenters": request.datacenters,
        "TaskGroups": [
            {
                "Name": f"{request.name}-group",
                "Count": 1,
                "Tasks": [task],
            }
        ],
    }


def count_gpus(nodes: list[dict[str, Any]]) -> int:
    """Count GPUs from node list based on known GPU workers.

    Args:
        nodes: List of Nomad node data.

    Returns:
        GPU count.
    """
    count = 0
    for node in nodes:
        node_name = node.get("Name", "").lower()
        if "cortex" in node_name or "point" in node_name:
            count += 1
    return count
