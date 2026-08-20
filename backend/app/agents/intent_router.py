from __future__ import annotations

import re
from typing import Any

from app.a2ui.catalog import enabled_domains
from app.llm.factory import create_llm
from app.providers.shopping import query_grounded_in_prompt

KEYWORD_RULES: list[tuple[str, str, str]] = [
    (r"refund|delayed|order|support|ticket|shipment|delivery", "CUSTOMER_SUPPORT", "REQUEST_REFUND"),
    (r"invoice|payout|milestone|freelancer|gst|overdue|receivable", "FINTECH", "INVOICES_ATTENTION"),
    (r"trip|travel|flight|hotel|weekend|vacation|book.*(goa|manali|jaipur|kerala|paris)", "TRAVEL", "PLAN_TRIP"),
    (
        r"headphone|laptop|phone|shoes|buy|shop|₹|rs\.?|product|under \d|earbuds|tv|watch",
        "SHOPPING",
        "PRODUCT_SEARCH",
    ),
    (r"market|nifty|sensex|stock|share|indian market|bse|nse", "MARKET_DATA", "MARKET_OVERVIEW"),
    (r"news|headline|article|what's happening", "NEWS", "NEWS_TOPIC"),
    (r"weather|forecast|rain|temperature|humidity|climate|umbrella|hot|monsoon", "WEATHER", "WEATHER_FORECAST"),
    (r"movie|film|cinema|theatre|theater|jr\.?\s*ntr|junior ntr|ntr|top rated|now playing|bollywood|tollywood", "MOVIES", "MOVIES_BROWSE"),
    (r"book|novel|author|read|fiction|bestseller|literature", "BOOKS", "BOOKS_BROWSE"),
]

STOPWORDS = {
    "show",
    "me",
    "the",
    "a",
    "an",
    "today",
    "todays",
    "tomorrow",
    "please",
    "find",
    "get",
    "what's",
    "whats",
    "what",
    "is",
    "are",
    "in",
    "for",
    "to",
    "of",
    "my",
    "i",
    "want",
    "need",
    "can",
    "how",
    "doing",
    "under",
    "news",
    "weather",
    "plan",
    "weekend",
    "trip",
}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "WEATHER": ("location",),
    "TRAVEL": ("destination",),
    "SHOPPING": ("query",),
}

CLARIFICATION_QUESTIONS = {
    ("WEATHER", "location"): "Which city or location should I check?",
    ("TRAVEL", "destination"): "Where would you like to travel?",
    ("SHOPPING", "query"): "What product are you looking for?",
}

CITY_ALIASES = {
    "hyderabad": "Hyderabad", "mumbai": "Mumbai", "delhi": "Delhi",
    "new delhi": "New Delhi", "bengaluru": "Bengaluru", "bangalore": "Bengaluru",
    "banglore": "Bengaluru", "chennai": "Chennai", "goa": "Goa", "pune": "Pune",
    "kolkata": "Kolkata", "jaipur": "Jaipur", "london": "London",
    "singapore": "Singapore", "dubai": "Dubai",
}


def _weather_locations(text: str) -> list[str]:
    hits: list[tuple[int, str]] = []
    lower = text.lower()
    for alias, canonical in CITY_ALIASES.items():
        hits.extend((m.start(), canonical) for m in re.finditer(rf"\b{re.escape(alias)}\b", lower))
    ordered: list[str] = []
    for _, city in sorted(hits):
        if city not in ordered:
            ordered.append(city)
    return ordered


def _normalize_locations(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        raw = str(item).strip()
        city = CITY_ALIASES.get(raw.lower(), raw)
        if city and city not in result:
            result.append(city)
    return result[:4]


def _focus_weather(text: str) -> str:
    lower = text.lower()
    if re.search(r"rain|umbrella|precip", lower):
        return "rain"
    if re.search(r"humid", lower):
        return "humidity"
    if re.search(r"temp|hot|cold|degree", lower):
        return "temperature"
    return "forecast"


def _extract_entities(text: str, domain: str) -> dict[str, Any]:
    t = text
    if domain == "WEATHER":
        locations = _weather_locations(t)
        m = re.search(
            r"(?:in|for|at|near)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
            t,
        ) or re.search(
            r"(Hyderabad|Mumbai|Delhi|Bengaluru|Bangalore|Chennai|Goa|Pune|Kolkata|Jaipur|London|Singapore|Dubai)",
            t,
            re.I,
        )
        loc = locations[0] if locations else (m.group(1) if m else None)
        if re.search(r"\bweekend\b", t, re.I):
            date = "weekend"
        elif re.search(r"\btomorrow\b", t, re.I):
            date = "tomorrow"
        else:
            date = "today"
        comparison = len(locations) > 1 or bool(re.search(r"\b(?:compare|comparison|versus|vs\.?)\b", t, re.I))
        return {
            "location": loc,
            "locations": locations if len(locations) > 1 else [],
            "date": date,
            "focus": "comparison" if comparison else _focus_weather(t),
        }
    if domain == "NEWS":
        topic = "Top stories"
        m = re.search(r"(?:about|on|regarding)\s+([A-Za-z0-9][A-Za-z0-9 \-]{1,40})", t, re.I)
        if m:
            topic = m.group(1).strip()
        else:
            words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9]+", t) if w.lower() not in STOPWORDS]
            if words:
                topic = " ".join(words[:4])
        return {"topic": topic, "timeRange": "today"}
    if domain == "TRAVEL":
        dest_m = re.search(r"(?:to|in)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", t) or re.search(
            r"(Goa|Manali|Jaipur|Kerala|Paris|Dubai|Singapore|Bali|Leh)", t, re.I
        )
        origin_m = re.search(r"(?:from|out of)\s+([A-Z][a-zA-Z]+)", t)
        focus = "full_plan"
        lower = t.lower()
        if "flight" in lower and "hotel" not in lower:
            focus = "flights"
        elif "hotel" in lower and "flight" not in lower:
            focus = "hotels"
        budget = None
        bm = re.search(r"₹\s*([\d,]+)", t) or re.search(r"under\s+₹?\s*([\d,]+)", t, re.I)
        if bm:
            budget = int(bm.group(1).replace(",", ""))
        price_range = re.search(r"(?:between|within|from)\s+₹?\s*([\d,]+)\s*(?:[-–—]|to|and)\s*₹?\s*([\d,]+)", t, re.I)
        meals = [meal for meal in ("breakfast", "dinner") if re.search(rf"\b{meal}\b", t, re.I)]
        hotel_preferences = {
            "nearAirport": True
            if re.search(r"near (?:the )?airport|airport hotel|close to (?:the )?airport", t, re.I)
            else None,
            "meals": meals,
            "minPrice": int(price_range.group(1).replace(",", "")) if price_range else None,
            "maxPrice": int(price_range.group(2).replace(",", "")) if price_range else budget,
        }
        return {
            "destination": dest_m.group(1) if dest_m else None,
            "origin": origin_m.group(1) if origin_m else None,
            "duration": "weekend" if re.search(r"weekend", t, re.I) else "trip",
            "budget": budget,
            "hotelPreferences": hotel_preferences,
            "focus": focus,
        }
    if domain == "MARKET_DATA":
        focus = "overview"
        if re.search(r"news|headline|impact|why.*(?:move|up|down)|what.*(?:moved|affected)", t, re.I):
            focus = "news_impact"
        elif re.search(r"nifty", t, re.I):
            focus = "nifty"
        elif re.search(r"sensex", t, re.I):
            focus = "sensex"
        elif re.search(r"mover|gainer|loser", t, re.I):
            focus = "movers"
        return {"market": "INDIA", "focus": focus}
    if domain == "SHOPPING":
        price = 100000
        m = re.search(r"₹\s*([\d,]+)", t) or re.search(r"under\s+([\d,]+)", t, re.I)
        if m:
            price = int(m.group(1).replace(",", ""))
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9]+", t) if w.lower() not in STOPWORDS]
        skip = {"find", "buy", "show", "cheap", "best", "under"}
        qwords = [w for w in words if w.lower() not in skip]
        query = " ".join(qwords[:4]) if qwords else ""
        return {"query": query, "maxPrice": price, "currency": "INR"}
    if domain == "FINTECH":
        if re.search(r"milestone", t, re.I):
            return {"focus": "release_milestone"}
        if re.search(r"payout", t, re.I):
            return {"focus": "execute_payout"}
        return {"focus": "invoices_attention"}
    if domain == "MOVIES":
        skip = {"show", "me", "movies", "movie", "films", "film", "find", "get",
                "what", "are", "the", "a", "an", "in", "of", "for", "to",
                "please", "list", "some", "all", "i", "want", "need", "can"}
        words = [w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9']+", t) if w.lower() not in skip]
        query = " ".join(words[:6]) if words else "Inception"
        return {"query": query}
    if domain == "BOOKS":
        skip = {"show", "me", "books", "book", "novels", "novel", "find", "get",
                "what", "are", "the", "a", "an", "of", "for", "to", "please",
                "list", "some", "all", "top", "rated", "best", "latest"}
        words = [w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9']+", t) if w.lower() not in skip]
        query = " ".join(words[:6]) if words else "fiction bestsellers"
        return {"query": query}
    if domain == "CUSTOMER_SUPPORT":
        action = "refund" if re.search(r"refund", t, re.I) else "status"
        return {"issue": "delayed_order", "desiredAction": action}
    return {}


def classify_mock(text: str) -> dict[str, Any]:
    lower = text.lower()
    for pattern, domain, intent in KEYWORD_RULES:
        if re.search(pattern, lower):
            if domain == "FINTECH" and re.search(r"milestone", lower):
                intent = "RELEASE_MILESTONE"
            entities = _extract_entities(text, domain)
            return {
                "domain": domain,
                "intent": intent,
                "entities": entities,
                "focus": entities.get("focus"),
                "confidence": 0.86,
                "source": "mock-rules",
            }
    return {
        "domain": "UNKNOWN",
        "intent": "CLARIFY",
        "entities": {},
        "confidence": 0.2,
        "source": "mock-fallback",
    }


def _semantic_state(history: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    for item in reversed(history or []):
        state = item.get("state")
        if isinstance(state, dict) and state.get("domain"):
            return state
    return None


def _looks_like_follow_up(text: str) -> bool:
    return bool(
        re.search(
            r"^(?:and |also |what about |how about |make (?:it|them) |show (?:me )?more|cheaper|tomorrow|today|next )",
            text.strip(),
            re.I,
        )
    )


def _apply_history(result: dict[str, Any], text: str, history: list[dict[str, Any]] | None) -> dict[str, Any]:
    previous = _semantic_state(history)
    if not previous:
        return result
    previous_domain = str(previous.get("domain") or "")
    if result.get("domain") == "UNKNOWN" and _looks_like_follow_up(text):
        result = classify_mock(text)
        result["domain"] = previous_domain
        result["intent"] = str(previous.get("intent") or "FOLLOW_UP")
        result["entities"] = _extract_entities(text, previous_domain)
        result["confidence"] = 0.72
        result["source"] = "history-follow-up"
    if result.get("domain") == previous_domain:
        inherited = dict(previous.get("entities") or {})
        current = result.get("entities") or {}
        if previous_domain == "TRAVEL" and isinstance(inherited.get("hotelPreferences"), dict):
            preferences = dict(inherited["hotelPreferences"])
            preferences.update(
                {k: v for k, v in (current.get("hotelPreferences") or {}).items() if v not in (None, "", [], {})}
            )
            current = {**current, "hotelPreferences": preferences}
        inherited.update({k: v for k, v in current.items() if v not in (None, "", [], {})})
        result["entities"] = inherited
        result["focus"] = result.get("focus") or inherited.get("focus") or previous.get("focus")
    return result


def _add_clarification(result: dict[str, Any]) -> dict[str, Any]:
    domain = str(result.get("domain") or "UNKNOWN")
    entities = result.get("entities") or {}
    missing = [field for field in REQUIRED_FIELDS.get(domain, ()) if entities.get(field) in (None, "", [], {})]
    if domain == "WEATHER" and entities.get("locations"):
        missing = [field for field in missing if field != "location"]
    result["missingFields"] = missing
    if missing:
        result["clarify"] = True
        result["clarificationQuestion"] = CLARIFICATION_QUESTIONS.get(
            (domain, missing[0]), "Could you provide a little more detail?"
        )
    return result


ROUTER_SYSTEM = """You route natural-language requests for one Indian business demo app.

Pick exactly one domain:
WEATHER, NEWS, TRAVEL, MARKET_DATA, SHOPPING, FINTECH, CUSTOMER_SUPPORT, MOVIES, BOOKS
or UNKNOWN if it is unrelated (poetry, math homework, coding, etc.).

Extract entities that actually appear in the prompt. Do not invent a city, product, or topic the user did not mention.
Fill only relevant keys:

WEATHER: location, locations (ordered list when comparing places), date (today|tomorrow|weekend),
focus (rain|temperature|humidity|forecast|comparison)
NEWS: topic, timeRange
TRAVEL: destination, origin, duration, budget (number INR or null), hotelPreferences
({nearAirport:boolean, meals:[breakfast|dinner], minPrice:number|null, maxPrice:number|null}),
focus (flights|hotels|full_plan)
MARKET_DATA: market (usually INDIA), focus (overview|nifty|sensex|movers|news_impact)
SHOPPING: query (product words), maxPrice (number or null), currency (INR)
FINTECH: focus (invoices_attention|release_milestone|execute_payout)
CUSTOMER_SUPPORT: issue, desiredAction (refund|status)
MOVIES: query (exact search term to pass to OMDB, e.g. "Prabhas", "Pushpa", "Christopher Nolan", "top rated")
BOOKS: focus (top_rated)

Also set intent, a short snake label, and confidence 0-1.

If conversation history is provided, treat the latest user message as the current request. Resolve follow-ups like "cheaper ones" or "what about tomorrow" using prior turns.

Return JSON only:
{"domain":"...","intent":"...","entities":{},"focus":"...","confidence":0.0}
No UI, HTML, or JavaScript.
"""


def _merge_entities(text: str, domain: str, llm_entities: Any) -> dict[str, Any]:
    base = _extract_entities(text, domain)
    if not isinstance(llm_entities, dict):
        return base
    merged = dict(base)
    for k, v in llm_entities.items():
        if v not in (None, "", [], {}):
            merged[k] = v
    if domain == "WEATHER":
        merged["locations"] = base.get("locations") or _normalize_locations(merged.get("locations"))
        if merged["locations"]:
            merged["location"] = merged["locations"][0]
            if len(merged["locations"]) > 1:
                merged["focus"] = "comparison"
    if domain == "SHOPPING":
        llm_query = str(merged.get("query") or "")
        if llm_query and not query_grounded_in_prompt(llm_query, text):
            merged["query"] = base.get("query") or llm_query
    return merged


def _format_history(history: list[dict[str, Any]] | None) -> str:
    if not history:
        return ""
    lines: list[str] = []
    for item in history[-8:]:
        role = str(item.get("role") or "user").lower()
        content = str(item.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    if not lines:
        return ""
    return "Conversation so far:\n" + "\n".join(lines) + "\n\nLatest user message:\n"


async def classify(text: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    llm = create_llm()
    router_input = f"{_format_history(history)}{text}" if history else text
    if llm is None:
        result = classify_mock(text)
    else:
        try:
            raw = await llm.complete_json(system=ROUTER_SYSTEM, user=router_input)
            if isinstance(raw, list):
                raw = raw[0] if raw else {}
            domain = str(raw.get("domain") or "UNKNOWN").upper()
            result = {
                "domain": domain,
                "intent": str(raw.get("intent") or "UNKNOWN"),
                "entities": _merge_entities(text, domain, raw.get("entities")) if domain != "UNKNOWN" else {},
                "focus": raw.get("focus"),
                "confidence": float(raw.get("confidence") or 0.7),
                "source": "llm",
            }
        except Exception:
            result = classify_mock(text)
            result["source"] = "mock-after-llm-error"
    result = _apply_history(result, text, history)
    domains = enabled_domains()
    if result["domain"] not in domains and result["domain"] != "UNKNOWN":
        result["disabled"] = True
    if result["domain"] == "UNKNOWN" or float(result.get("confidence") or 0) < 0.35:
        result["clarify"] = True
    return _add_clarification(result)
