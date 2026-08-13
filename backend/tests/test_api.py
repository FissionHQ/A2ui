from httpx import ASGITransport, AsyncClient
from app.main import app
from app.api.actions import handle_action
import pytest


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert "WEATHER" in body["enabledDomains"]
        assert "demoMode" in body


@pytest.mark.asyncio
async def test_stream_weather_sse():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/stream",
            json={"text": "What's the weather in Hyderabad tomorrow?"},
        )
        assert res.status_code == 200
        text = res.text
        assert "createSurface" in text
        assert "WeatherCard" in text or "updateComponents" in text


@pytest.mark.asyncio
async def test_remote_action_allowlist():
    bad = await handle_action({"name": "drop_database", "actionId": "1"})
    assert bad["actionResponse"]["error"]["code"] == "NOT_ALLOWLISTED"
    ok = await handle_action({"name": "book_trip", "actionId": "2", "context": {"destination": "Goa"}})
    assert ok["actionResponse"]["value"]["bookingId"] == "TR-1024"
