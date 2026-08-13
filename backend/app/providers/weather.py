from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

IST = timezone(timedelta(hours=5, minutes=30))


class WeatherProvider:
    async def forecast(self, location: str, date: str = "tomorrow") -> dict[str, Any]:
        raise NotImplementedError


class MockWeatherProvider(WeatherProvider):
    async def forecast(self, location: str, date: str = "tomorrow") -> dict[str, Any]:
        day = (datetime.now(IST) + timedelta(days=1)).date().isoformat()
        loc = location or "Hyderabad"
        rain = 20 if loc.lower() != "mumbai" else 72
        return {
            "location": loc,
            "date": day,
            "temperature": 31,
            "humidity": 62,
            "rainProbability": rain,
            "condition": "Partly cloudy" if rain < 50 else "Rain likely",
            "alert": "High rain probability tomorrow." if rain >= 50 else "",
            "hourly": [
                {"label": "09:00", "value": 28},
                {"label": "12:00", "value": 31},
                {"label": "15:00", "value": 33},
                {"label": "18:00", "value": 30},
                {"label": "21:00", "value": 27},
            ],
            "source": "mock",
        }


class OpenMeteoWeatherProvider(WeatherProvider):
    async def forecast(self, location: str, date: str = "tomorrow") -> dict[str, Any]:
        loc = location or "Hyderabad"
        async with httpx.AsyncClient(timeout=8.0) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": loc, "count": 1, "language": "en", "format": "json"},
            )
            geo.raise_for_status()
            results = geo.json().get("results") or []
            if not results:
                raise RuntimeError(f"Unknown location {loc}")
            lat, lon = results[0]["latitude"], results[0]["longitude"]
            name = results[0].get("name", loc)
            wx = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,precipitation_probability",
                    "hourly": "temperature_2m,precipitation_probability",
                    "daily": "temperature_2m_max,precipitation_probability_max",
                    "timezone": "Asia/Kolkata",
                    "forecast_days": 2,
                },
            )
            wx.raise_for_status()
            body = wx.json()
        tomorrow = (datetime.now(IST) + timedelta(days=1)).date().isoformat()
        daily = body.get("daily") or {}
        times = daily.get("time") or []
        idx = times.index(tomorrow) if tomorrow in times else min(1, max(0, len(times) - 1))
        temp = (daily.get("temperature_2m_max") or [31])[idx]
        rain = (daily.get("precipitation_probability_max") or [20])[idx]
        current = body.get("current") or {}
        hourly_out = []
        htimes = (body.get("hourly") or {}).get("time") or []
        htemp = (body.get("hourly") or {}).get("temperature_2m") or []
        for t, v in zip(htimes, htemp):
            if t.startswith(tomorrow) and t[11:13] in {"09", "12", "15", "18", "21"}:
                hourly_out.append({"label": t[11:16], "value": round(v)})
        rain_i = int(rain or 0)
        return {
            "location": name,
            "date": tomorrow,
            "temperature": round(temp or current.get("temperature_2m") or 31),
            "humidity": int(current.get("relative_humidity_2m") or 62),
            "rainProbability": rain_i,
            "condition": "Rain likely" if rain_i >= 50 else "Partly cloudy",
            "alert": "High rain probability tomorrow." if rain_i >= 50 else "",
            "hourly": hourly_out
            or [
                {"label": "09:00", "value": 28},
                {"label": "12:00", "value": 31},
                {"label": "15:00", "value": 33},
                {"label": "18:00", "value": 30},
            ],
            "source": "open-meteo",
        }


async def get_weather_provider(mode: str) -> WeatherProvider:
    if mode == "mock":
        return MockWeatherProvider()
    return OpenMeteoWeatherProvider()
