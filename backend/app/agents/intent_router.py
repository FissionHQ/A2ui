from __future__ import annotations

import re
from typing import Any

from app.a2ui.catalog import enabled_domains
from app.llm.factory import create_llm
from app.providers.shopping import query_grounded_in_prompt

KEYWORD_RULES: list[tuple[str, str, str]] = [
    (r"refund|delayed|order|support|ticket|shipment|delivery", "CUSTOMER_SUPPORT", "REQUEST_REFUND"),
    (r"invoice|payout|milestone|freelancer|gst|overdue|receivable", "FINTECH", "INVOICES_ATTENTION"),
    (
        r"headphone|laptop|phone|shoes|buy|shop|₹|rs\.?|product|under \d|earbuds|tv|watch",
        "SHOPPING",
        "PRODUCT_SEARCH",
    ),
    (r"market|nifty|sensex|stock|share|indian market|bse|nse", "MARKET_DATA", "MARKET_OVERVIEW"),
    (r"trip|travel|flight|hotel|weekend|vacation|book.*(goa|manali|jaipur|kerala|paris)", "TRAVEL", "PLAN_TRIP"),
    (r"news|headline|article|what's happening", "NEWS", "NEWS_TOPIC"),
    (r"weather|forecast|rain|temperature|humidity|climate|umbrella|hot|monsoon", "WEATHER", "WEATHER_FORECAST"),
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
        m = re.search(
            r"(?:in|for|at|near)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
            t,
        ) or re.search(
            r"(Hyderabad|Mumbai|Delhi|Bengaluru|Bangalore|Chennai|Goa|Pune|Kolkata|Jaipur|London|Singapore|Dubai)",
            t,
            re.I,
        )
        loc = m.group(1) if m else "Hyderabad"
        if re.search(r"\bweekend\b", t, re.I):
            date = "weekend"
        elif re.search(r"\btomorrow\b", t, re.I):
            date = "tomorrow"
        else:
            date = "today"
        return {"location": loc, "date": date, "focus": _focus_weather(t)}
    if domain == "NEWS":
        topic = "AI"
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
        bm = re.search(r"₹\s*([\d,]+)", t) or re.search(r"under\s+([\d,]+)", t, re.I)
        if bm:
            budget = int(bm.group(1).replace(",", ""))
        return {
            "destination": dest_m.group(1) if dest_m else "Goa",
            "origin": origin_m.group(1) if origin_m else "Hyderabad",
            "duration": "weekend" if re.search(r"weekend", t, re.I) else "trip",
            "budget": budget,
            "focus": focus,
        }
    if domain == "MARKET_DATA":
        focus = "overview"
        if re.search(r"nifty", t, re.I):
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


ROUTER_SYSTEM = """You route natural-language requests for one Indian business demo app.

Pick exactly one domain:
WEATHER, NEWS, TRAVEL, MARKET_DATA, SHOPPING, FINTECH, CUSTOMER_SUPPORT
or UNKNOWN if it is unrelated (poetry, math homework, coding, etc.).

Extract entities that actually appear in the prompt. Do not invent a city, product, or topic the user did not mention.
Fill only relevant keys:

WEATHER: location, date (today|tomorrow|weekend), focus (rain|temperature|humidity|forecast)
NEWS: topic, timeRange
TRAVEL: destination, origin, duration, budget (number INR or null), focus (flights|hotels|full_plan)
MARKET_DATA: market (usually INDIA), focus (overview|nifty|sensex|movers)
SHOPPING: query (product words), maxPrice (number or null), currency (INR)
FINTECH: focus (invoices_attention|release_milestone|execute_payout)
CUSTOMER_SUPPORT: issue, desiredAction (refund|status)

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
    domains = enabled_domains()
    if result["domain"] not in domains and result["domain"] != "UNKNOWN":
        result["disabled"] = True
    if result["domain"] == "UNKNOWN" or float(result.get("confidence") or 0) < 0.35:
        result["clarify"] = True
    return result
