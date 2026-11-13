"""Ray Serve deployments service layer.

Manages inference deployments via Ray Dashboard REST API (port 8265).
Uses the Ray Serve v2 API (applications-based).
"""

import logging
import os
from typing import Any

import httpx

from src.config import CONFIG

logger = logging.getLogger(__name__)

RAY_DASHBOARD_URL = os.environ.get("RAY_DASHBOARD_URL", CONFIG["endpoints"]["ray_dashboard"])
RAY_SERVE_URL = os.environ.get("RAY_SERVE_URL", CONFIG["endpoints"]["ray_serve"])
HTTP_TIMEOUT = 15.0


async def list_deployments() -> dict[str, Any]:
    """List active Ray Serve applications via Dashboard API.

    Returns:
        Dict with deployments list and serve status.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{RAY_DASHBOARD_URL}/api/serve/applications/",
                timeout=HTTP_TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()

        applications = data.get("applications", {})
        deployments = []

        for app_name, app_info in applications.items():
            app_status = app_info.get("status", "UNKNOWN")
            app_deployments = app_info.get("deployments", {})

            for deploy_name, deploy_info in app_deployments.items():
                replicas = len(deploy_info.get("replica_states", {}).get("RUNNING", []))
                deployments.append(
                    {
                        "name": deploy_name,
                        "application": app_name,
                        "status": deploy_info.get("status", app_status),
                        "replicas": replicas,
                        "endpoint": f"{RAY_SERVE_URL}/{app_name}",
                    }
                )

        return {
            "deployments": deployments,
            "ray_serve_status": "running",
        }
    except httpx.ConnectError:
        logger.warning("Ray Serve not reachable (may not be started)")
        return {"deployments": [], "ray_serve_status": "not_started"}
    except Exception as e:
        logger.error(f"Failed to list deployments: {e}")
        return {"deployments": [], "ray_serve_status": "unavailable"}


async def get_serve_status() -> dict[str, Any]:
    """Get Ray Serve global status.

    Returns:
        Serve status dict with proxy and application info.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{RAY_DASHBOARD_URL}/api/serve/applications/",
                timeout=HTTP_TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()

        app_count = len(data.get("applications", {}))
        proxy_status = data.get("proxy_location", "unknown")

        return {
            "status": "running",
            "applications": app_count,
            "proxy_location": proxy_status,
        }
    except httpx.ConnectError:
        return {"status": "not_started", "applications": 0}
    except Exception as e:
        logger.error(f"Failed to get serve status: {e}")
        return {"status": "error", "reason": str(e)}


async def deploy_model(
    name: str,
    model_type: str,
    model_path: str | None = None,
    num_replicas: int = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Deploy a model as Ray Serve application via Dashboard PUT API.

    Args:
        name: Application/deployment name.
        model_type: Model type (bone-rotation, yolo, efficientnet, vllm, custom).
        model_path: Path to model weights file.
        num_replicas: Number of serving replicas.
        **kwargs: Extra config (num_gpus, gpu_memory_utilization, etc).

    Returns:
        Deployment info dict with name, status, endpoint.
    """
    import_path = _resolve_import_path(model_type)
    if not import_path:
        raise RuntimeError(f"Unsupported model type: {model_type}")

    deployment_config: dict[str, Any] = {"num_replicas": num_replicas}

    num_gpus = kwargs.get("num_gpus", 1 if model_type in ("yolo", "vllm") else 0)
    if num_gpus > 0:
        deployment_config["ray_actor_options"] = {"num_gpus": num_gpus}

    init_args: dict[str, Any] = {}
    if model_path:
        init_args["model_path"] = model_path
    if model_type == "vllm":
        init_args["gpu_memory_utilization"] = kwargs.get("gpu_memory_utilization", 0.7)

    app_config: dict[str, Any] = {
        "applications": [
            {
                "name": name,
                "route_prefix": f"/{name}",
                "import_path": import_path,
                "deployments": [
                    {
                        "name": name,
                        "deployment_config": deployment_config,
                        "init_args": init_args,
                    }
                ],
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{RAY_DASHBOARD_URL}/api/serve/applications/",
                json=app_config,
                timeout=HTTP_TIMEOUT,
            )
            r.raise_for_status()

        logger.info(f"Deployed {name} ({model_type}), replicas={num_replicas}")

        return {
            "name": name,
            "status": "DEPLOYING",
            "type": model_type,
            "replicas": num_replicas,
            "endpoint": f"{RAY_SERVE_URL}/{name}",
        }
    except httpx.HTTPStatusError as e:
        detail = e.response.text[:500] if e.response else str(e)
        logger.error(f"Ray Serve rejected deploy for {name}: {detail}")
        raise RuntimeError(f"Deploy rejected by Ray Serve: {detail}")
    except Exception as e:
        logger.error(f"Failed to deploy {name}: {e}")
        raise RuntimeError(f"Deployment failed: {e}")


async def undeploy_model(name: str) -> dict[str, str]:
    """Remove a Ray Serve application via Dashboard API.

    Args:
        name: Application name to remove.

    Returns:
        Status dict with name and status.

    Raises:
        RuntimeError: If application not found or delete fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{RAY_DASHBOARD_URL}/api/serve/applications/{name}",
                timeout=HTTP_TIMEOUT,
            )
            if r.status_code == 404:
                raise RuntimeError(f"Application '{name}' not found")
            r.raise_for_status()

        logger.info(f"Undeployed application {name}")
        return {"name": name, "status": "UNDEPLOYED"}
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Failed to undeploy {name}: {e}")
        raise RuntimeError(f"Undeploy failed: {e}")


def _resolve_import_path(model_type: str) -> str | None:
    """Resolve model type to a Ray Serve import path.

    Args:
        model_type: Short model type identifier.

    Returns:
        Python import path string, or None if unsupported.
    """
    import_paths: dict[str, str] = {
        "bone-rotation": "src.serving.bone_rotation_app:app",
        "bone-seg": "src.serving.bone_seg_app:app",
        "yolo": "src.serving.yolo_app:app",
        "efficientnet": "src.serving.efficientnet_app:app",
        "vllm": "src.serving.vllm_app:app",
        "custom": "src.serving.custom_app:app",
    }
    return import_paths.get(model_type)


async def predict(app_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Forward prediction request to a running Ray Serve deployment.

    Args:
        app_name: Deployed Ray Serve application name.
        payload: JSON-serializable request body for the model.

    Returns:
        Prediction result dict from the model deployment.
    """
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{RAY_SERVE_URL}/{app_name}",
            json=payload,
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()


async def get_deployment_status(name: str) -> dict[str, Any]:
    """Get detailed status of a specific Ray Serve application.

    Args:
        name: Application name.

    Returns:
        Status dict with application state, deployments, and replica info.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{RAY_DASHBOARD_URL}/api/serve/applications/",
                timeout=HTTP_TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()

        applications = data.get("applications", {})
        if name not in applications:
            raise RuntimeError(f"Application '{name}' not found")

        app_info = applications[name]
        deployments_info = []
        for deploy_name, deploy_data in app_info.get("deployments", {}).items():
            replica_states = deploy_data.get("replica_states", {})
            deployments_info.append(
                {
                    "name": deploy_name,
                    "status": deploy_data.get("status", "UNKNOWN"),
                    "replicas_running": len(replica_states.get("RUNNING", [])),
                    "replicas_starting": len(replica_states.get("STARTING", [])),
                    "message": deploy_data.get("message", ""),
                }
            )

        return {
            "name": name,
            "status": app_info.get("status", "UNKNOWN"),
            "route_prefix": app_info.get("route_prefix", f"/{name}"),
            "endpoint": f"{RAY_SERVE_URL}/{name}",
            "deployments": deployments_info,
            "message": app_info.get("message", ""),
        }
    except RuntimeError:
        raise
    except httpx.ConnectError:
        raise RuntimeError("Ray Serve not reachable")
    except Exception as e:
        logger.error(f"Failed to get deployment status for {name}: {e}")
        raise RuntimeError(f"Status check failed: {e}")
