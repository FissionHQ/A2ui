from __future__ import annotations

import asyncio
import httpx

_MOCK_FALLBACK = [
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "year": "1960", "genre": "Fiction", "rating": 4.3},
    {"title": "1984", "author": "George Orwell", "year": "1949", "genre": "Dystopian", "rating": 4.5},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": "1925", "genre": "Classic", "rating": 3.9},
    {"title": "The Alchemist", "author": "Paulo Coelho", "year": "1988", "genre": "Adventure", "rating": 4.2},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "year": "2011", "genre": "Non-Fiction", "rating": 4.4},
]


async def _search(query: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": 10, "fields": "title,author_name,first_publish_year,subject,ratings_average"},
            timeout=8,
        )
        data = r.json()
    books = []
    for doc in (data.get("docs") or []):
        title = doc.get("title") or ""
        authors = doc.get("author_name") or []
        year = doc.get("first_publish_year") or ""
        subjects = doc.get("subject") or []
        genre = subjects[0] if subjects else "Fiction"
        try:
            rating = round(float(doc.get("ratings_average") or 0), 1)
        except (ValueError, TypeError):
            rating = 0.0
        if not title:
            continue
        books.append({
            "title": title,
            "author": authors[0] if authors else "Unknown",
            "year": str(year),
            "genre": genre[:30],
            "rating": rating,
        })
    return books


class OpenLibraryBooksProvider:
    async def search(self, query: str) -> dict:
        books = await _search(query)
        return {"query": query, "label": f"Books: {query}", "books": books or _MOCK_FALLBACK}


class MockBooksProvider:
    async def search(self, query: str) -> dict:
        await asyncio.sleep(0.1)
        return {"query": query, "label": f"Books: {query}", "books": _MOCK_FALLBACK}

    async def top_rated(self) -> dict:
        await asyncio.sleep(0.1)
        return {"label": "Top Rated Books", "books": _MOCK_FALLBACK}
