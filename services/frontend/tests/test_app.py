from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> httpx.Response:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


@pytest.mark.anyio
async def test_index_renders_form(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "City Geocode Search" in resp.text
    assert '<form' in resp.text


@pytest.mark.anyio
@patch("app.main.httpx.AsyncClient")
async def test_search_success(mock_client_cls, client):
    mock_resp = _mock_response(200, {"name": "Berlin", "latitude": 52.52, "longitude": 13.405})
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_ctx.get = AsyncMock(return_value=mock_resp)
    mock_client_cls.return_value = mock_ctx

    resp = await client.post("/search", data={"city": "Berlin"})
    assert resp.status_code == 200
    assert "Berlin" in resp.text
    assert "52.52" in resp.text
    assert "13.405" in resp.text


@pytest.mark.anyio
@patch("app.main.httpx.AsyncClient")
async def test_search_not_found(mock_client_cls, client):
    mock_resp = _mock_response(404, {"detail": "City not found: Xyzzyville"})
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_ctx.get = AsyncMock(return_value=mock_resp)
    mock_client_cls.return_value = mock_ctx

    resp = await client.post("/search", data={"city": "Xyzzyville"})
    assert resp.status_code == 200
    assert "City not found" in resp.text


@pytest.mark.anyio
@patch("app.main.httpx.AsyncClient")
async def test_search_timeout(mock_client_cls, client):
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_ctx.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
    mock_client_cls.return_value = mock_ctx

    resp = await client.post("/search", data={"city": "Berlin"})
    assert resp.status_code == 200
    assert "timed out" in resp.text


@pytest.mark.anyio
@patch("app.main.httpx.AsyncClient")
async def test_search_connection_error(mock_client_cls, client):
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_ctx.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    mock_client_cls.return_value = mock_ctx

    resp = await client.post("/search", data={"city": "Berlin"})
    assert resp.status_code == 200
    assert "Could not connect" in resp.text
