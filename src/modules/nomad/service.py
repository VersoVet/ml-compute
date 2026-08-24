"""Nomad cluster manager for job orchestration and GPU resource coordination."""

import logging
from typing import Any

import httpx

from src.config import CONFIG
from src.modules.nomad.models import (
    AllocationStatus,
    GPUStatus,
    NomadClusterStatus,
    NomadJobRequest,
    NomadJobStatus,
    TaskStatus,
)
from src.modules.nomad.utils import build_job_spec, count_gpus

logger = logging.getLogger(__name__)

NOMAD_URL = CONFIG["endpoints"]["nomad"]
NOMAD_TIMEOUT = CONFIG.get("nomad", {}).get("timeout", 30.0)


class NomadManager:
    """Manager for Nomad job orchestration and GPU coordination."""

    def __init__(self, nomad_url: str = NOMAD_URL):
        """Initialize Nomad manager.

        Args:
            nomad_url: Nomad HTTP API URL.
        """
        self.nomad_url = nomad_url

    async def connect(self) -> None:
        """Verify Nomad cluster is accessible.

        Raises:
            ConnectionError: If Nomad is unreachable.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.nomad_url}/v1/status/leader", timeout=NOMAD_TIMEOUT)
                response.raise_for_status()
            logger.info(f"Connected to Nomad at {self.nomad_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Nomad: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Nomad client connection."""
        logger.info("Disconnected from Nomad")

    async def submit_job(self, request: NomadJobRequest) -> dict[str, Any]:
        """Submit a job to Nomad cluster.

        Args:
            request: Job specification.

        Returns:
            Job submission response with evaluation ID.

        Raises:
            httpx.HTTPError: If submission fails.
        """
        try:
            job_spec = build_job_spec(request)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.nomad_url}/v1/jobs",
                    json={"Job": job_spec},
                    timeout=NOMAD_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

            logger.info(f"Job submitted: {request.name}")
            return {
                "status": "submitted",
                "job_id": request.name,
                "evaluation_id": result.get("EvalID"),
            }
        except Exception as e:
            logger.error(f"Failed to submit job {request.name}: {e}")
            raise

    async def get_job_status(self, job_id: str) -> NomadJobStatus:
        """Get job status from Nomad.

        Args:
            job_id: Job name.

        Returns:
            NomadJobStatus with allocations.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nomad_url}/v1/job/{job_id}",
                    timeout=NOMAD_TIMEOUT,
                )
                response.raise_for_status()
                job_data = response.json()

                alloc_response = await client.get(
                    f"{self.nomad_url}/v1/job/{job_id}/allocations",
                    timeout=NOMAD_TIMEOUT,
                )
                alloc_response.raise_for_status()
                alloc_data = alloc_response.json() or []

            allocations = [
                AllocationStatus(
                    allocation_id=a.get("ID", ""),
                    job_id=a.get("JobID", ""),
                    task_name=a.get("TaskGroup", ""),
                    status=TaskStatus(a.get("ClientStatus", "pending")),
                    node_id=a.get("NodeID", ""),
                    node_name=a.get("NodeName", ""),
                    cpu_used_mhz=a.get("Resources", {}).get("CPU", 0),
                    memory_used_mb=a.get("Resources", {}).get("MemoryMB", 0),
                )
                for a in alloc_data
            ]

            return NomadJobStatus(
                job_id=job_data.get("ID", job_id),
                status=job_data.get("Status", "unknown"),
                priority=job_data.get("Priority", 50),
                allocations=allocations,
                create_index=job_data.get("CreateIndex", 0),
                modify_index=job_data.get("ModifyIndex", 0),
            )
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return NomadJobStatus(
                job_id=job_id,
                status="error",
                priority=0,
                allocations=[],
                create_index=0,
                modify_index=0,
            )

    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job.

        Args:
            job_id: Job name.

        Returns:
            True if stopped successfully.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.nomad_url}/v1/job/{job_id}",
                    timeout=NOMAD_TIMEOUT,
                )
                response.raise_for_status()
            logger.info(f"Job stopped: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop job {job_id}: {e}")
            return False

    async def get_cluster_status(self) -> NomadClusterStatus:
        """Get cluster-wide status including GPU availability.

        Returns:
            NomadClusterStatus with cluster metrics.
        """
        try:
            async with httpx.AsyncClient() as client:
                nodes_response = await client.get(
                    f"{self.nomad_url}/v1/nodes",
                    timeout=NOMAD_TIMEOUT,
                )
                nodes_response.raise_for_status()
                nodes_data = nodes_response.json() or []

                nodes_ready = sum(1 for n in nodes_data if n.get("Status") == "ready")

                jobs_response = await client.get(
                    f"{self.nomad_url}/v1/jobs",
                    timeout=NOMAD_TIMEOUT,
                )
                jobs_response.raise_for_status()
                jobs_data = jobs_response.json() or []

                jobs_running = sum(1 for j in jobs_data if j.get("Status") == "running")
                jobs_pending = sum(1 for j in jobs_data if j.get("Status") == "pending")

            return NomadClusterStatus(
                nodes_ready=nodes_ready,
                nodes_total=len(nodes_data),
                gpus_total=count_gpus(nodes_data),
                gpus_available=count_gpus(nodes_data),
                jobs_running=jobs_running,
                jobs_pending=jobs_pending,
            )
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return NomadClusterStatus(
                nodes_ready=0,
                nodes_total=0,
                gpus_total=0,
                gpus_available=0,
                jobs_running=0,
                jobs_pending=0,
            )

    async def get_gpu_status(self) -> list[GPUStatus]:
        """Get GPU status on all nodes.

        Returns:
            List of GPU status per node.
        """
        statuses: list[GPUStatus] = []
        try:
            async with httpx.AsyncClient() as client:
                nodes_response = await client.get(
                    f"{self.nomad_url}/v1/nodes",
                    timeout=NOMAD_TIMEOUT,
                )
                nodes_response.raise_for_status()
                nodes_data = nodes_response.json() or []

                for node in nodes_data:
                    node_id = node.get("ID")
                    node_name = node.get("Name")

                    node_detail = await client.get(
                        f"{self.nomad_url}/v1/node/{node_id}",
                        timeout=NOMAD_TIMEOUT,
                    )
                    node_detail.raise_for_status()
                    node_data = node_detail.json()

                    devices = node_data.get("NodeResources", {}).get("Devices") or []
                    gpu_devices = [d for d in devices if d.get("Type") == "gpu"]
                    num_gpus = len(gpu_devices)

                    statuses.append(
                        GPUStatus(
                            node_id=node_id,
                            node_name=node_name,
                            num_gpus=num_gpus,
                            available_gpus=num_gpus,
                            in_use=[],
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get GPU status: {e}")

        return statuses
