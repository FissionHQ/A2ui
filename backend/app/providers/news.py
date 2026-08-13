from __future__ import annotations

from typing import Any

import httpx


class NewsProvider:
    async def headlines(self, topic: str = "AI") -> dict[str, Any]:
        raise NotImplementedError


class MockNewsProvider(NewsProvider):
    async def headlines(self, topic: str = "AI") -> dict[str, Any]:
        topic = topic or "AI"
        return {
            "activeTab": "ai",
            "topic": topic,
            "articles": [
                {
                    "title": "India’s AI startups close a busy funding week",
                    "source": "Mock Wire",
                    "summary": "Enterprise copilots and vernacular models led announcements.",
                    "topic": topic,
                    "url": "https://example.com/ai-1",
                    "imageUrl": "",
                },
                {
                    "title": "Open models push on-device inference forward",
                    "source": "Mock Labs",
                    "summary": "Smaller checkpoints are showing up in mobile production apps.",
                    "topic": topic,
                    "url": "https://example.com/ai-2",
                    "imageUrl": "",
                },
                {
                    "title": "Regulators ask for clearer AI labeling",
                    "source": "Mock Policy",
                    "summary": "Draft guidance focuses on synthetic media and customer support bots.",
                    "topic": topic,
                    "url": "https://example.com/ai-3",
                    "imageUrl": "",
                },
            ],
            "source": "mock",
        }


class HackerNewsProvider(NewsProvider):
    async def headlines(self, topic: str = "AI") -> dict[str, Any]:
        q = topic or "AI"
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": q, "tags": "story", "hitsPerPage": 5},
            )
            res.raise_for_status()
            hits = res.json().get("hits") or []
        articles = []
        for h in hits:
            articles.append(
                {
                    "title": h.get("title") or "Untitled",
                    "source": "Hacker News",
                    "summary": (h.get("url") or "Discussion on HN")[:180],
                    "topic": q,
                    "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    "imageUrl": "",
                }
            )
        if not articles:
            raise RuntimeError("No news hits")
        return {"activeTab": "ai", "topic": q, "articles": articles, "source": "hn-algolia"}
