"""PostgreSQL connection pool for GPU allocator.

Uses the same bone_recognition DB as bone-rotation, schema ml_compute.
Password fetched from Vault. Pool is a lazy singleton.
"""

import logging
import os
from typing import Any

import asyncpg
import httpx

from src.config import CONFIG

logger = logging.getLogger(__name__)

_db_cfg: dict[str, Any] = CONFIG.get("database", {})
PG_HOST = os.environ.get("PG_HOST") or _db_cfg.get("host", "10.0.0.59")
PG_PORT = int(os.environ.get("PG_PORT") or _db_cfg.get("port", 5432))
PG_DB = os.environ.get("PG_DB") or _db_cfg.get("name", "bone_recognition")
PG_USER = os.environ.get("PG_USER") or _db_cfg.get("user", "onyx")
VAULT_URL = CONFIG.get("endpoints", {}).get("vault", "http://10.0.0.44:8050/vault")
VAULT_KEY = _db_cfg.get("vault_key", "onyxplex_password")
VAULT_TOKEN = os.environ.get("ONYX_VAULT_TOKEN", "")

_pool: asyncpg.Pool | None = None

SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS ml_compute;

CREATE TABLE IF NOT EXISTS ml_compute.gpu_slots (
    gpu_id          TEXT PRIMARY KEY,
    node            TEXT NOT NULL,
    node_ip         TEXT NOT NULL,
    gpu_type        TEXT NOT NULL,
    vram_mb         INTEGER NOT NULL,
    assigned_job_id TEXT,
    assigned_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ml_compute.job_queue (
    queue_id        SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    entrypoint      TEXT NOT NULL,
    runtime_env     JSONB NOT NULL DEFAULT '{}',
    submit_kwargs   JSONB NOT NULL DEFAULT '{}',
    queued_at       TIMESTAMPTZ DEFAULT NOW(),
    status          TEXT NOT NULL DEFAULT 'queued'
                    CHECK (status IN ('queued', 'submitted', 'cancelled')),
    ray_job_id      TEXT
);

CREATE INDEX IF NOT EXISTS idx_queue_status
    ON ml_compute.job_queue (status, queued_at);

-- Migration: add ray_job_id column if table already exists without it
DO $$ BEGIN
    ALTER TABLE ml_compute.job_queue ADD COLUMN IF NOT EXISTS ray_job_id TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;
"""


async def _get_pg_password() -> str:
    """Fetch PG password from Vault or environment.

    Returns:
        Password string.
    """
    env_pw = os.environ.get("PG_PASSWORD")
    if env_pw:
        return env_pw
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{VAULT_URL}/{VAULT_KEY}",
            headers={"X-Vault-Token": VAULT_TOKEN},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()["value"]


async def get_pool() -> asyncpg.Pool:
    """Get or create the asyncpg connection pool.

    Returns:
        Shared asyncpg connection pool.
    """
    global _pool  # noqa: PLW0603
    if _pool is None:
        password = await _get_pg_password()
        _pool = await asyncpg.create_pool(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=password,
            min_size=1,
            max_size=3,
            ssl=False,
        )
        logger.info("GPU allocator PG pool: %s@%s:%d/%s", PG_USER, PG_HOST, PG_PORT, PG_DB)
    return _pool


async def ensure_schema() -> None:
    """Create schema, tables, and seed GPU slots from config."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)
        await _seed_gpu_slots(conn)
    logger.info("Schema ml_compute ensured")


async def _seed_gpu_slots(conn: asyncpg.Connection) -> None:
    """Upsert GPU slots from config/ml-compute.yaml workers section."""
    workers = CONFIG.get("workers", {})
    for node_name, worker in workers.items():
        node_ip = worker.get("ip", "")
        for gpu in worker.get("gpus", []):
            gpu_id = gpu.get("id")
            if not gpu_id:
                continue
            await conn.execute(
                """INSERT INTO ml_compute.gpu_slots (gpu_id, node, node_ip, gpu_type, vram_mb)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (gpu_id) DO UPDATE SET
                       node = EXCLUDED.node, node_ip = EXCLUDED.node_ip,
                       gpu_type = EXCLUDED.gpu_type, vram_mb = EXCLUDED.vram_mb""",
                gpu_id,
                node_name,
                node_ip,
                gpu.get("type", ""),
                gpu.get("vram_mb", 0),
            )
            logger.debug("GPU slot seeded: %s (%s)", gpu_id, gpu.get("type"))


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool  # noqa: PLW0603
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("GPU allocator PG pool closed")
