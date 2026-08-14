"""Tests for Ray cluster nodes service."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.modules.nodes import service

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    """Build a fake httpx.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=resp,
        )
        resp.text = str(json_data)
    return resp


def _make_mock_client(response: MagicMock | None = None,
                      side_effect: Exception | None = None) -> AsyncMock:
    """Build a mock httpx.AsyncClient with async context manager support.

    Args:
        response: Mock response to return from get().
        side_effect: Exception to raise from get().

    Returns:
        Configured AsyncMock for httpx.AsyncClient.
    """
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    if side_effect is not None:
        mock_client.get = AsyncMock(side_effect=side_effect)
    else:
        mock_client.get = AsyncMock(return_value=response)
    return mock_client


RAY_NODES_RESPONSE = {
    "data": {
        "result": {
            "result": [
                {
                    "node_id": "node-aaa",
                    "node_name": "head-node",
                    "node_ip": "10.0.0.1",
                    "is_head_node": True,
                    "state": "ALIVE",
                    "resources_total": {"CPU": 8.0, "GPU": 1.0, "memory": 17179869184},
                },
                {
                    "node_id": "node-bbb",
                    "node_name": "worker-1",
                    "node_ip": "10.0.0.2",
                    "is_head_node": False,
                    "state": "ALIVE",
                    "resources_total": {"CPU": 4.0, "GPU": 2.0, "memory": 8589934592},
                },
            ]
        }
    }
}

EMPTY_NODES_RESPONSE: dict = {
    "data": {"result": {"result": []}}
}


# ---------------------------------------------------------------------------
# service.get_cluster_nodes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_cluster_nodes_returns_parsed_nodes() -> None:
    """get_cluster_nodes parses Ray dashboard nodes into structured list."""
    mock_client = _make_mock_client(_mock_response(RAY_NODES_RESPONSE))

    with patch("src.modules.nodes.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_cluster_nodes()

    assert result["cluster_status"] == "healthy"
    assert len(result["nodes"]) == 2

    head = next(n for n in result["nodes"] if n["is_head"])
    assert head["node_id"] == "node-aaa"
    assert head["node_name"] == "head-node"
    assert head["node_ip"] == "10.0.0.1"
    assert head["status"] == "alive"
    assert head["resources"]["CPU"] == 8.0
    assert head["resources"]["GPU"] == 1.0

    worker = next(n for n in result["nodes"] if not n["is_head"])
    assert worker["node_id"] == "node-bbb"
    assert worker["resources"]["GPU"] == 2.0

    # Total resources aggregated across nodes
    assert result["total_resources"]["CPU"] == 12.0
    assert result["total_resources"]["GPU"] == 3.0
    assert result["total_resources"]["memory"] == 17179869184 + 8589934592


@pytest.mark.asyncio
async def test_get_cluster_nodes_empty_cluster() -> None:
    """get_cluster_nodes returns unhealthy status when no nodes found."""
    mock_client = _make_mock_client(_mock_response(EMPTY_NODES_RESPONSE))

    with patch("src.modules.nodes.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_cluster_nodes()

    assert result["cluster_status"] == "unhealthy"
    assert result["nodes"] == []
    assert result["total_resources"] == {}


@pytest.mark.asyncio
async def test_get_cluster_nodes_connection_error() -> None:
    """get_cluster_nodes raises RuntimeError on connection failure."""
    mock_client = _make_mock_client(side_effect=httpx.ConnectError("refused"))

    with patch("src.modules.nodes.service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(RuntimeError, match="Failed to query cluster"):
            await service.get_cluster_nodes()


# ---------------------------------------------------------------------------
# service.get_resource_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_resource_summary_calculates_totals() -> None:
    """get_resource_summary aggregates CPU, GPU and memory from all nodes."""
    mock_client = _make_mock_client(_mock_response(RAY_NODES_RESPONSE))

    with patch("src.modules.nodes.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_resource_summary()

    assert result["total"]["cpu"] == 12.0
    assert result["total"]["gpu"] == 3.0
    assert result["total"]["memory_bytes"] == 17179869184 + 8589934592

    # Available equals total (resources_total used for both in service)
    assert result["available"]["cpu"] == 12.0
    assert result["available"]["gpu"] == 3.0

    # Utilization should be 0% since available == total
    assert result["utilization"]["cpu_percent"] == 0
    assert result["utilization"]["gpu_percent"] == 0
    assert result["utilization"]["memory_percent"] == 0


@pytest.mark.asyncio
async def test_get_resource_summary_returns_zeros_on_error() -> None:
    """get_resource_summary returns zero values when cluster unreachable."""
    mock_client = _make_mock_client(side_effect=httpx.ConnectError("refused"))

    with patch("src.modules.nodes.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_resource_summary()

    assert result["total"]["cpu"] == 0
    assert result["total"]["gpu"] == 0
    assert result["total"]["memory_bytes"] == 0
    assert result["available"]["cpu"] == 0
    assert result["utilization"]["cpu_percent"] == 0
