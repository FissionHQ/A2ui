from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx


class MarketProvider:
    async def overview(self, market: str = "INDIA") -> dict[str, Any]:
        raise NotImplementedError


class MockMarketProvider(MarketProvider):
    async def overview(self, market: str = "INDIA") -> dict[str, Any]:
        return {
            "title": "Indian markets",
            "asOf": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M IST"),
            "nifty": {"value": 24780.4, "changePct": 0.62},
            "sensex": {"value": 81240.1, "changePct": 0.48},
            "series": [
                {"label": "W1", "value": 24120},
                {"label": "W2", "value": 24380},
                {"label": "W3", "value": 24510},
                {"label": "W4", "value": 24780},
            ],
            "movers": [
                {"Symbol": "HDFCBANK", "Last": "1,642", "Change": "+1.2%", "Status": "up"},
                {"Symbol": "RELIANCE", "Last": "2,918", "Change": "-0.4%", "Status": "down"},
                {"Symbol": "TCS", "Last": "4,105", "Change": "+0.6%", "Status": "up"},
                {"Symbol": "INFY", "Last": "1,788", "Change": "+0.3%", "Status": "up"},
            ],
            "source": "mock",
        }


class YahooMarketProvider(MarketProvider):
    async def overview(self, market: str = "INDIA") -> dict[str, Any]:
        symbol = "%5ENSEI"
        async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "a2ui-demo/1.0"}) as client:
            res = await client.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                params={"interval": "1d", "range": "1mo"},
            )
            res.raise_for_status()
            result = (res.json().get("chart") or {}).get("result") or []
            if not result:
                raise RuntimeError("No market data")
            meta = result[0].get("meta") or {}
            quotes = ((result[0].get("indicators") or {}).get("quote") or [{}])[0]
            closes = [c for c in (quotes.get("close") or []) if c is not None]
            price = meta.get("regularMarketPrice") or (closes[-1] if closes else 24780)
            prev = meta.get("chartPreviousClose") or (closes[0] if closes else price)
            change = ((price - prev) / prev) * 100 if prev else 0
            series = [{"label": f"D{i+1}", "value": round(v, 1)} for i, v in enumerate(closes[-8:])]
        mock = await MockMarketProvider().overview(market)
        mock["nifty"] = {"value": round(float(price), 1), "changePct": round(change, 2)}
        mock["series"] = series or mock["series"]
        mock["source"] = "yahoo-chart"
        mock["asOf"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return mock
