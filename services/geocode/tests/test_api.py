from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas import GeocodeResponse


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


MOCK_RESPONSE = GeocodeResponse(name="Berlin", latitude=52.52, longitude=13.405)


@pytest.mark.anyio
@patch("app.main.geocode_city", new_callable=AsyncMock, return_value=MOCK_RESPONSE)
async def test_geocode_success(mock_gc, client):
    resp = await client.get("/geocode", params={"city": "Berlin"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Berlin"
    assert data["latitude"] == 52.52
    assert data["longitude"] == 13.405
    mock_gc.assert_awaited_once_with("Berlin")


@pytest.mark.anyio
@patch("app.main.geocode_city", new_callable=AsyncMock, return_value=None)
async def test_geocode_not_found(mock_gc, client):
    resp = await client.get("/geocode", params={"city": "Xyzzyville"})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.anyio
async def test_geocode_empty_city(client):
    resp = await client.get("/geocode", params={"city": ""})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_geocode_missing_param(client):
    resp = await client.get("/geocode")
    assert resp.status_code == 422


@pytest.mark.anyio
@patch(
    "app.main.geocode_city",
    new_callable=AsyncMock,
    side_effect=httpx.TimeoutException("timeout"),
)
async def test_geocode_upstream_timeout(mock_gc, client):
    resp = await client.get("/geocode", params={"city": "Berlin"})
    assert resp.status_code == 502
    assert "timeout" in resp.json()["detail"].lower()


@pytest.mark.anyio
async def test_correlation_id_echo(client):
    cid = "test-correlation-123"
    resp = await client.get(
        "/geocode",
        params={"city": "Berlin"},
        headers={"X-Correlation-ID": cid},
    )
    assert resp.headers.get("X-Correlation-ID") == cid


@pytest.mark.anyio
async def test_healthz(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
