from __future__ import annotations

import asyncio
import httpx

from app.config import get_settings

_GENRE_ICON: list[tuple[str, str]] = [
    ("action|adventure|war|thriller", "swords"),
    ("comedy", "laugh"),
    ("horror", "skull"),
    ("romance", "heart"),
    ("sci-fi|fantasy", "rocket"),
    ("animation", "sparkles"),
    ("documentary", "book-open"),
    ("crime|mystery", "search"),
    ("music|musical", "music"),
    ("drama", "theater"),
]


def _icon_for_genre(genre: str) -> str:
    g = genre.lower()
    for pattern, icon in _GENRE_ICON:
        if any(p in g for p in pattern.split("|")):
            return icon
    return "film"


_MOCK_FALLBACK = [
    {"title": "The Shawshank Redemption", "year": "1994", "rating": 9.3, "genre": "Drama", "icon": "theater", "director": "Frank Darabont", "poster": ""},
    {"title": "The Godfather", "year": "1972", "rating": 9.2, "genre": "Crime", "icon": "search", "director": "Francis Ford Coppola", "poster": ""},
    {"title": "The Dark Knight", "year": "2008", "rating": 9.0, "genre": "Action", "icon": "swords", "director": "Christopher Nolan", "poster": ""},
    {"title": "Pulp Fiction", "year": "1994", "rating": 8.9, "genre": "Crime", "icon": "search", "director": "Quentin Tarantino", "poster": ""},
    {"title": "Inception", "year": "2010", "rating": 8.8, "genre": "Sci-Fi", "icon": "rocket", "director": "Christopher Nolan", "poster": ""},
]


async def _fetch_detail(client: httpx.AsyncClient, api_key: str, imdb_id: str) -> dict | None:
    try:
        r = await client.get(
            "https://www.omdbapi.com/",
            params={"apikey": api_key, "i": imdb_id, "r": "json"},
            timeout=5,
        )
        raw = r.json()
        if raw.get("Response") != "True":
            return None
        try:
            rating = float(raw.get("imdbRating") or 0)
        except ValueError:
            rating = 0.0
        genre = (raw.get("Genre") or "").split(",")[0].strip()
        return {
            "title": raw.get("Title", ""),
            "year": raw.get("Year", ""),
            "rating": rating,
            "genre": genre,
            "icon": _icon_for_genre(genre),
            "director": raw.get("Director", ""),
            "poster": raw.get("Poster") or "",
        }
    except Exception:
        return None


async def _search(query: str) -> list[dict]:
    api_key = get_settings().omdb_api_key
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://www.omdbapi.com/",
            params={"apikey": api_key, "s": query, "type": "movie", "r": "json"},
            timeout=8,
        )
        data = r.json()
        if data.get("Response") != "True":
            return []
        imdb_ids = [item["imdbID"] for item in (data.get("Search") or [])[:10]]
        results = await asyncio.gather(*[_fetch_detail(client, api_key, id_) for id_ in imdb_ids])
    return [m for m in results if m]


class OmdbMoviesProvider:
    async def search(self, query: str) -> dict:
        movies = await _search(query)
        return {"query": query, "label": f"Movies: {query}", "movies": movies or _MOCK_FALLBACK}


class MockMoviesProvider:
    async def search(self, query: str) -> dict:
        await asyncio.sleep(0.1)
        return {"query": query, "label": f"Movies: {query}", "movies": _MOCK_FALLBACK}
