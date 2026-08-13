from __future__ import annotations

import re
from typing import Any


class ShoppingProvider:
    async def search(self, query: str, max_price: int = 10000) -> dict[str, Any]:
        raise NotImplementedError


CATALOG = [
    {"title": "Sony WH-CH720N", "price": 8990, "rating": 4.5, "tags": ["headphone", "headphones", "sony", "audio"]},
    {"title": "boAt Nirvana 751 ANC", "price": 3499, "rating": 4.2, "tags": ["headphone", "headphones", "boat", "audio"]},
    {"title": "JBL Tune 770NC", "price": 6499, "rating": 4.3, "tags": ["headphone", "headphones", "jbl", "audio"]},
    {"title": "Noise VS104 Pro", "price": 2199, "rating": 4.0, "tags": ["earbud", "earbuds", "noise", "audio"]},
    {"title": "Apple MacBook Air M2", "price": 99990, "rating": 4.7, "tags": ["laptop", "macbook", "apple"]},
    {"title": "Lenovo IdeaPad Slim 3", "price": 42990, "rating": 4.3, "tags": ["laptop", "lenovo"]},
    {"title": "ASUS Vivobook 15", "price": 38990, "rating": 4.2, "tags": ["laptop", "asus"]},
    {"title": "Samsung Galaxy S24", "price": 74999, "rating": 4.6, "tags": ["phone", "samsung", "mobile", "smartphone"]},
    {"title": "OnePlus Nord CE4", "price": 24999, "rating": 4.4, "tags": ["phone", "oneplus", "mobile", "smartphone"]},
    {"title": "Google Pixel 8a", "price": 39999, "rating": 4.5, "tags": ["phone", "pixel", "google", "mobile"]},
    {"title": "Motorola Edge 50", "price": 22999, "rating": 4.3, "tags": ["phone", "motorola", "mobile"]},
    {"title": "Nike Revolution 7", "price": 3695, "rating": 4.4, "tags": ["shoes", "nike", "running"]},
    {"title": "Adidas Runfalcon 5", "price": 4299, "rating": 4.3, "tags": ["shoes", "adidas", "running"]},
    {"title": "Apple Watch SE", "price": 29900, "rating": 4.5, "tags": ["watch", "apple"]},
]

ALIASES = {
    "phones": "phone",
    "phone": "phone",
    "mobile": "phone",
    "mobiles": "phone",
    "smartphone": "phone",
    "smartphones": "phone",
    "iphone": "phone",
    "headphones": "headphone",
    "headphone": "headphone",
    "earbuds": "earbud",
    "earbud": "earbud",
    "earphones": "earbud",
    "earphone": "earbud",
    "laptops": "laptop",
    "laptop": "laptop",
    "notebook": "laptop",
    "macbook": "laptop",
    "shoes": "shoe",
    "shoe": "shoe",
    "sneakers": "shoe",
    "sneaker": "shoe",
    "trainers": "shoe",
    "watches": "watch",
    "watch": "watch",
}

GENERIC_TOKENS = {
    "find",
    "buy",
    "show",
    "get",
    "cheap",
    "best",
    "under",
    "product",
    "products",
    "item",
    "items",
    "please",
    "want",
    "need",
    "looking",
    "search",
}


def normalize_token(token: str) -> str:
    t = token.lower()
    if t in ALIASES:
        return ALIASES[t]
    if t.endswith("s") and len(t) > 3:
        stem = t[:-1]
        return ALIASES.get(stem, stem)
    return t


def tokens_of(text: str) -> set[str]:
    return {normalize_token(t) for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) > 1}


def query_grounded_in_prompt(query: str, prompt: str) -> bool:
    """True when every product token in query also appears in the user prompt."""
    wanted = tokens_of(query) - GENERIC_TOKENS
    if not wanted:
        return False
    return wanted <= tokens_of(prompt)


def search_catalog(query: str, max_price: int = 100000) -> dict[str, Any]:
    q = (query or "").strip()
    wanted = tokens_of(q) - GENERIC_TOKENS
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in CATALOG:
        item_tokens = tokens_of(item["title"]) | tokens_of(" ".join(item["tags"]))
        overlap = wanted & item_tokens
        if overlap:
            scored.append((len(overlap), item))
    scored.sort(key=lambda x: (-x[0], x[1]["price"]))
    matched = [dict(item) for score, item in scored if score > 0 and item["price"] <= max_price]
    if not matched and wanted:
        matched = [
            {
                "title": f"{q.title()} — option {i + 1}",
                "price": max(499, min(max_price, 7999) - i * 800),
                "rating": round(4.4 - i * 0.1, 1),
                "imageUrl": "",
                "tags": sorted(wanted),
            }
            for i in range(3)
            if max(499, min(max_price, 7999) - i * 800) <= max_price
        ]
    elif not matched:
        matched = [dict(item) for item in CATALOG if item["price"] <= max_price][:6]
    for p in matched:
        p.setdefault("imageUrl", "")
    return {
        "query": q or "catalog",
        "maxPrice": max_price,
        "currency": "INR",
        "products": matched[:6],
        "compared": [],
        "source": "mock",
    }


class MockShoppingProvider(ShoppingProvider):
    async def search(self, query: str, max_price: int = 100000) -> dict[str, Any]:
        return search_catalog(query, max_price)
