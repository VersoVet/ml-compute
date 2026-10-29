"""GPU management service for OnyxCortex.

Manages GPU allocation between inference (SAM/MedSAM2) and training jobs.
Stops/starts Docker containers on OnyxCortex via SSH to free GPU memory.
"""

import logging
from datetime import UTC, datetime

import httpx

from src.config import CONFIG
from src.modules.gpu.models import (
    ContainerState,
    GPUAcquireResponse,
    GPUMode,
    GPUReleaseResponse,
    GPUStatusResponse,
)

logger = logging.getLogger("ml-compute.gpu")

# Containers that use GPU on OnyxCortex and can be stopped for training
INFERENCE_CONTAINERS = ["sam-gpu", "medsam2-gpu"]

CORTEX_IP = CONFIG.get("workers", {}).get("onyxcortex", {}).get("ip", "10.0.0.26")


async def _get_vault_secret(key: str) -> str:
    """Fetch a secret from OnyxVault.

    Args:
        key: Secret key name.

    Returns:
        Secret value string.
    """
    vault_url = CONFIG.get("endpoints", {}).get("vault", "http://10.0.0.44:8050/vault")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{vault_url}/{key}", timeout=10.0)
        r.raise_for_status()
        return r.json()["value"]


async def _ssh_exec(host: str, command: str) -> tuple[int, str]:
    """Execute a command on a remote host via SSH using onyx-core proxy.

    Uses the Core API SSH exec endpoint for simplicity (no paramiko needed).
    Falls back to direct docker API if available.

    Args:
        host: Target host IP.
        command: Shell command to execute.

    Returns:
        Tuple of (return_code, stdout).
    """
    core_url = CONFIG.get("endpoints", {}).get("core", "http://10.0.0.44:8050")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{core_url}/ssh/exec",
                json={"host": host, "command": command},
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("exit_code", 0), data.get("stdout", "")
        except Exception:
            logger.debug("Core SSH proxy unavailable, trying direct Docker API")

    # Fallback: direct Docker API on Cortex (port 2375 if exposed)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"http://{host}:2375/version", timeout=5.0)
            r.raise_for_status()
            # Docker API available — but we need shell commands, not API
            # This path is limited; log and raise
        except Exception:
            pass

    raise RuntimeError(f"Cannot execute command on {host}: no SSH proxy or Docker API")


async def _docker_exec(container_action: str, container_name: str) -> bool:
    """Start or stop a Docker container on OnyxCortex.

    Uses Docker Engine API directly on OnyxCortex (port 2375).

    Args:
        container_action: 'start' or 'stop'.
        container_name: Docker container name.

    Returns:
        True if successful.
    """
    docker_url = f"http://{CORTEX_IP}:2375"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{docker_url}/containers/{container_name}/{container_action}",
                timeout=30.0,
            )
            # 204 = success, 304 = already in desired state
            if r.status_code in (204, 304):
                logger.info(f"Container {container_name}: {container_action} OK")
                return True
            logger.warning(f"Container {container_name} {container_action}: HTTP {r.status_code}")
            return r.status_code < 400
        except Exception as e:
            logger.error(f"Failed to {container_action} {container_name}: {e}")
            return False


async def _get_container_state(container_name: str) -> ContainerState:
    """Get the state of a Docker container on OnyxCortex.

    Args:
        container_name: Docker container name.

    Returns:
        ContainerState with running status.
    """
    docker_url = f"http://{CORTEX_IP}:2375"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{docker_url}/containers/{container_name}/json",
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                running = data.get("State", {}).get("Running", False)
                return ContainerState(name=container_name, running=running, gpu_mib=0)
            return ContainerState(name=container_name, running=False, gpu_mib=0)
        except Exception:
            return ContainerState(name=container_name, running=False, gpu_mib=0)


async def _get_nvidia_smi() -> dict:
    """Query nvidia-smi on OnyxCortex via NVML Docker API or fallback.

    Returns:
        Dict with gpu_name, memory_used, memory_total, memory_free (all in MiB).
    """
    # Try nvidia-smi via ray-worker container (always has GPU access)
    docker_url = f"http://{CORTEX_IP}:2375"
    async with httpx.AsyncClient() as client:
        try:
            # Create exec instance in ray-worker
            r = await client.post(
                f"{docker_url}/containers/ray-worker/exec",
                json={
                    "Cmd": [
                        "nvidia-smi",
                        "--query-gpu=name,memory.used,memory.total,memory.free",
                        "--format=csv,noheader,nounits",
                    ],
                    "AttachStdout": True,
                    "AttachStderr": True,
                },
                timeout=10.0,
            )
            r.raise_for_status()
            exec_id = r.json()["Id"]

            # Start exec
            r2 = await client.post(
                f"{docker_url}/exec/{exec_id}/start",
                json={"Detach": False, "Tty": False},
                timeout=10.0,
            )
            # Docker exec stream has 8-byte header per frame
            raw = r2.content
            # Strip Docker stream headers (type byte + 3 padding + 4 size bytes)
            output = ""
            i = 0
            while i < len(raw):
                if i + 8 <= len(raw):
                    size = int.from_bytes(raw[i + 4 : i + 8], "big")
                    if i + 8 + size <= len(raw):
                        output += raw[i + 8 : i + 8 + size].decode("utf-8", errors="replace")
                    i += 8 + size
                else:
                    break

            parts = [p.strip() for p in output.strip().split(",")]
            if len(parts) >= 4:
                return {
                    "gpu_name": parts[0],
                    "memory_used": int(parts[1]),
                    "memory_total": int(parts[2]),
                    "memory_free": int(parts[3]),
                }
        except Exception as e:
            logger.warning(f"nvidia-smi via Docker exec failed: {e}")

    return {"gpu_name": "Unknown", "memory_used": 0, "memory_total": 0, "memory_free": 0}


# Track acquisition state in-memory
_acquired_at: datetime | None = None


async def get_gpu_status() -> GPUStatusResponse:
    """Get current GPU status on OnyxCortex.

    Returns:
        GPUStatusResponse with GPU memory and container states.
    """
    gpu_info = await _get_nvidia_smi()
    containers = [await _get_container_state(name) for name in INFERENCE_CONTAINERS]

    any_inference_running = any(c.running for c in containers)
    if _acquired_at and not any_inference_running:
        mode = GPUMode.TRAINING
    elif any_inference_running and _acquired_at:
        mode = GPUMode.MIXED
    else:
        mode = GPUMode.INFERENCE

    return GPUStatusResponse(
        gpu_name=gpu_info["gpu_name"],
        gpu_memory_used_mib=gpu_info["memory_used"],
        gpu_memory_total_mib=gpu_info["memory_total"],
        gpu_memory_free_mib=gpu_info["memory_free"],
        mode=mode,
        containers=containers,
        acquired_at=_acquired_at,
    )


async def acquire_gpu() -> GPUAcquireResponse:
    """Acquire GPU for training by stopping inference containers.

    Stops SAM and MedSAM2 containers on OnyxCortex to free GPU memory.

    Returns:
        GPUAcquireResponse with results.
    """
    global _acquired_at

    stopped: list[str] = []
    for name in INFERENCE_CONTAINERS:
        state = await _get_container_state(name)
        if state.running:
            ok = await _docker_exec("stop", name)
            if ok:
                stopped.append(name)
            else:
                logger.error(f"Failed to stop {name}")

    _acquired_at = datetime.now(UTC)

    # Get updated GPU info
    gpu_info = await _get_nvidia_smi()

    return GPUAcquireResponse(
        success=True,
        mode=GPUMode.TRAINING,
        stopped_containers=stopped,
        gpu_memory_free_mib=gpu_info["memory_free"],
        message=f"GPU acquired for training. Stopped {len(stopped)} container(s). "
        f"Free VRAM: {gpu_info['memory_free']} MiB",
    )


async def release_gpu() -> GPUReleaseResponse:
    """Release GPU back to inference by restarting containers.

    Restarts SAM and MedSAM2 containers on OnyxCortex.

    Returns:
        GPUReleaseResponse with results.
    """
    global _acquired_at

    started: list[str] = []
    for name in INFERENCE_CONTAINERS:
        state = await _get_container_state(name)
        if not state.running:
            ok = await _docker_exec("start", name)
            if ok:
                started.append(name)

    _acquired_at = None

    return GPUReleaseResponse(
        success=True,
        mode=GPUMode.INFERENCE,
        started_containers=started,
        message=f"GPU released to inference. Started {len(started)} container(s).",
    )
