#!/usr/bin/env python3
"""
Nomad Cluster Monitoring Script

Monitor GPU allocation, job status, and detect conflicts between SAM and training jobs.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

import httpx


class NomadMonitor:
    """Monitor Nomad cluster for GPU conflicts and job status."""

    def __init__(self, nomad_url: str = "http://10.0.0.44:4646"):
        """Initialize monitor."""
        self.nomad_url = nomad_url
        self.timeout = 30.0

    async def get_jobs(self) -> list[dict[str, Any]]:
        """Get all jobs in cluster."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.nomad_url}/v1/jobs",
                timeout=self.timeout,
            )
            return response.json() or []

    async def get_job_details(self, job_id: str) -> dict[str, Any]:
        """Get job allocations and status."""
        async with httpx.AsyncClient() as client:
            job_response = await client.get(
                f"{self.nomad_url}/v1/job/{job_id}",
                timeout=self.timeout,
            )
            alloc_response = await client.get(
                f"{self.nomad_url}/v1/job/{job_id}/allocations",
                timeout=self.timeout,
            )
            return {
                "job": job_response.json(),
                "allocations": alloc_response.json() or [],
            }

    async def get_nodes(self) -> list[dict[str, Any]]:
        """Get all nodes in cluster."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.nomad_url}/v1/nodes",
                timeout=self.timeout,
            )
            return response.json() or []

    async def detect_gpu_conflicts(self) -> list[dict[str, Any]]:
        """Detect GPUs with multiple jobs allocated."""
        jobs = await self.get_jobs()
        conflicts = []

        # Group jobs by GPU usage
        gpu_jobs = {}
        for job in jobs:
            if job.get("Status") in ("running", "pending"):
                details = await self.get_job_details(job["ID"])
                for alloc in details.get("allocations", []):
                    node = alloc.get("NodeName")
                    if node not in gpu_jobs:
                        gpu_jobs[node] = []
                    gpu_jobs[node].append(
                        {
                            "job": job["ID"],
                            "status": alloc.get("ClientStatus"),
                            "cpu": alloc.get("Resources", {}).get("CPU"),
                        }
                    )

        # Check for conflicts (multiple jobs on same node)
        for node, jobs_on_node in gpu_jobs.items():
            if (
                len(jobs_on_node) > 1
                and "cortex" in node.lower()
                and any("sam" in j["job"].lower() for j in jobs_on_node)
                and any("bone" in j["job"].lower() for j in jobs_on_node)
            ):
                conflicts.append(
                    {
                        "node": node,
                        "jobs": jobs_on_node,
                        "severity": "CRITICAL",
                    }
                )

        return conflicts

    async def print_cluster_status(self) -> None:
        """Print cluster status summary."""
        print("\n" + "=" * 60)
        print(f"Nomad Cluster Status — {datetime.now().isoformat()}")
        print("=" * 60)

        # Node status
        nodes = await self.get_nodes()
        print(f"\n📍 Nodes ({len(nodes)} total)")
        for node in nodes:
            status = node.get("Status")
            icon = "✓" if status == "ready" else "⚠"
            print(f"  {icon} {node.get('Name'):<20} {status:<15} ID: {node.get('ID')[:8]}")

        # Job status
        jobs = await self.get_jobs()
        running = sum(1 for j in jobs if j.get("Status") == "running")
        pending = sum(1 for j in jobs if j.get("Status") == "pending")
        print(f"\n⚙️  Jobs ({len(jobs)} total)")
        print(f"  ▶ Running: {running}")
        print(f"  ⏳ Pending: {pending}")
        print(f"  ■ Complete: {sum(1 for j in jobs if j.get('Status') == 'complete')}")

        # Active jobs
        print(f"\n📋 Active Jobs")
        for job in jobs:
            if job.get("Status") in ("running", "pending"):
                icon = "▶" if job.get("Status") == "running" else "⏳"
                print(f"  {icon} {job.get('ID'):<30} {job.get('Status'):<10} Type: {job.get('Type')}")

        # Check for conflicts
        conflicts = await self.detect_gpu_conflicts()
        if conflicts:
            print(f"\n⚠️  GPU CONFLICTS DETECTED ({len(conflicts)})")
            for conflict in conflicts:
                print(f"  Node: {conflict['node']}")
                for job in conflict["jobs"]:
                    print(f"    - {job['job']} ({job['status']})")
        else:
            print("\n✓ No GPU conflicts detected")

        print("\n" + "=" * 60 + "\n")

    async def monitor_loop(self, interval: int = 30) -> None:
        """Continuous monitoring loop."""
        while True:
            try:
                await self.print_cluster_status()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(interval)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Nomad cluster")
    parser.add_argument(
        "--url",
        default="http://10.0.0.44:4646",
        help="Nomad API URL",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitoring interval in seconds",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Print status once and exit",
    )

    args = parser.parse_args()

    monitor = NomadMonitor(args.url)

    if args.once:
        await monitor.print_cluster_status()
    else:
        await monitor.monitor_loop(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
