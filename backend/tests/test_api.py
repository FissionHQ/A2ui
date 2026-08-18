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
        assert "routingResult" in text


@pytest.mark.asyncio
async def test_stream_asks_for_missing_weather_location():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/stream", json={"text": "Will it rain tomorrow?"})
        assert res.status_code == 200
        assert "Which city or location should I check?" in res.text
        assert "WeatherCard" not in res.text


@pytest.mark.asyncio
async def test_stream_weather_comparison_uses_both_locations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/stream",
            json={"text": "Compare Hyderabad weather to Banglore weather"},
        )
        assert res.status_code == 200
        assert "weather_comparison_surface" in res.text
        assert "Hyderabad" in res.text
        assert "Bengaluru" in res.text


@pytest.mark.asyncio
async def test_stream_market_news_impact_surface():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/stream", json={"text": "What news impacted Nifty or Sensex?"})
        assert res.status_code == 200
        assert '"focus": "news_impact"' in res.text
        assert "impact_news" in res.text
        assert "not proof" in res.text


@pytest.mark.asyncio
async def test_remote_action_allowlist():
    bad = await handle_action({"name": "drop_database", "actionId": "1"})
    assert bad["actionResponse"]["error"]["code"] == "NOT_ALLOWLISTED"
    ok = await handle_action({"name": "book_trip", "actionId": "2", "context": {"destination": "Goa"}})
    assert ok["actionResponse"]["value"]["bookingId"] == "TR-1024"
