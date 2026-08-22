"""Tests for Ray Serve deployments service and routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.modules.serve import service

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
        import httpx

        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=resp,
        )
        resp.text = str(json_data)
    return resp


RAY_APPLICATIONS_RESPONSE = {
    "applications": {
        "yolo-bones": {
            "status": "RUNNING",
            "deployments": {
                "yolo-bones": {
                    "status": "HEALTHY",
                    "replica_states": {"RUNNING": ["replica-1", "replica-2"]},
                }
            },
        },
        "efficientnet-cls": {
            "status": "RUNNING",
            "deployments": {
                "efficientnet-cls": {
                    "status": "HEALTHY",
                    "replica_states": {"RUNNING": ["replica-1"]},
                }
            },
        },
    }
}

EMPTY_APPLICATIONS = {"applications": {}}


# ---------------------------------------------------------------------------
# service.list_deployments
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_deployments_returns_parsed_apps() -> None:
    """list_deployments parses Ray applications into flat list."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(RAY_APPLICATIONS_RESPONSE))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.list_deployments()

    assert result["ray_serve_status"] == "running"
    assert len(result["deployments"]) == 2

    names = {d["name"] for d in result["deployments"]}
    assert "yolo-bones" in names
    assert "efficientnet-cls" in names

    yolo = next(d for d in result["deployments"] if d["name"] == "yolo-bones")
    assert yolo["replicas"] == 2
    assert yolo["status"] == "HEALTHY"
    assert "/yolo-bones" in yolo["endpoint"]


@pytest.mark.asyncio
async def test_list_deployments_empty() -> None:
    """list_deployments returns empty list when no apps deployed."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(EMPTY_APPLICATIONS))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.list_deployments()

    assert result["deployments"] == []
    assert result["ray_serve_status"] == "running"


@pytest.mark.asyncio
async def test_list_deployments_connect_error() -> None:
    """list_deployments returns not_started on connection failure."""
    import httpx

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.list_deployments()

    assert result["ray_serve_status"] == "not_started"
    assert result["deployments"] == []


# ---------------------------------------------------------------------------
# service.get_serve_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_serve_status_running() -> None:
    """get_serve_status returns app count and status."""
    data = {
        "applications": {"app1": {}, "app2": {}},
        "proxy_location": "EveryNode",
    }
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(data))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_serve_status()

    assert result["status"] == "running"
    assert result["applications"] == 2
    assert result["proxy_location"] == "EveryNode"


@pytest.mark.asyncio
async def test_get_serve_status_not_started() -> None:
    """get_serve_status returns not_started when Ray Serve unreachable."""
    import httpx

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.get_serve_status()

    assert result["status"] == "not_started"


# ---------------------------------------------------------------------------
# service.deploy_model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deploy_model_success() -> None:
    """deploy_model sends PUT to Ray and returns deployment info."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.put = AsyncMock(return_value=_mock_response({}))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.deploy_model(
            name="test-yolo",
            model_type="yolo",
            model_path="/models/yolo.pt",
            num_replicas=2,
            num_gpus=1,
        )

    assert result["name"] == "test-yolo"
    assert result["status"] == "DEPLOYING"
    assert result["replicas"] == 2
    assert "/test-yolo" in result["endpoint"]

    # Verify PUT was called with correct config
    call_args = mock_client.put.call_args
    config = call_args.kwargs["json"]
    app = config["applications"][0]
    assert app["name"] == "test-yolo"
    assert app["route_prefix"] == "/test-yolo"
    assert app["import_path"] == "src.serving.yolo_app:app"


@pytest.mark.asyncio
async def test_deploy_model_vllm_passes_gpu_config() -> None:
    """deploy_model for vllm type includes gpu_memory_utilization."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.put = AsyncMock(return_value=_mock_response({}))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.deploy_model(
            name="llama-8b",
            model_type="vllm",
            model_path="meta-llama/Llama-3.3-8B",
            gpu_memory_utilization=0.85,
        )

    assert result["type"] == "vllm"

    call_args = mock_client.put.call_args
    config = call_args.kwargs["json"]
    deploy = config["applications"][0]["deployments"][0]
    assert deploy["init_args"]["gpu_memory_utilization"] == 0.85
    assert deploy["init_args"]["model_path"] == "meta-llama/Llama-3.3-8B"


@pytest.mark.asyncio
async def test_deploy_model_unsupported_type() -> None:
    """deploy_model raises RuntimeError for unknown model type."""
    with pytest.raises(RuntimeError, match="Unsupported model type"):
        await service.deploy_model(name="bad", model_type="tensorflow")


@pytest.mark.asyncio
async def test_deploy_model_ray_rejects() -> None:
    """deploy_model raises RuntimeError when Ray returns HTTP error."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.put = AsyncMock(return_value=_mock_response({"error": "bad config"}, 400))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(RuntimeError, match="Deploy rejected"):
            await service.deploy_model(name="bad-deploy", model_type="yolo")


# ---------------------------------------------------------------------------
# service.undeploy_model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_undeploy_model_success() -> None:
    """undeploy_model sends DELETE and returns status."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.delete = AsyncMock(return_value=_mock_response({}, 200))

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        result = await service.undeploy_model("yolo-bones")

    assert result["name"] == "yolo-bones"
    assert result["status"] == "UNDEPLOYED"

    call_args = mock_client.delete.call_args
    assert "yolo-bones" in call_args.args[0]


@pytest.mark.asyncio
async def test_undeploy_model_not_found() -> None:
    """undeploy_model raises RuntimeError when app not found."""
    resp = MagicMock()
    resp.status_code = 404
    resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.delete = AsyncMock(return_value=resp)

    with patch("src.modules.serve.service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(RuntimeError, match="not found"):
            await service.undeploy_model("ghost-app")


# ---------------------------------------------------------------------------
# _resolve_import_path
# ---------------------------------------------------------------------------


def test_resolve_import_path_known_types() -> None:
    """_resolve_import_path returns paths for known model types."""
    assert service._resolve_import_path("yolo") == "src.serving.yolo_app:app"
    assert service._resolve_import_path("vllm") == "src.serving.vllm_app:app"
    assert service._resolve_import_path("efficientnet") == "src.serving.efficientnet_app:app"
    assert service._resolve_import_path("custom") == "src.serving.custom_app:app"


def test_resolve_import_path_unknown() -> None:
    """_resolve_import_path returns None for unknown types."""
    assert service._resolve_import_path("tensorflow") is None
    assert service._resolve_import_path("") is None
