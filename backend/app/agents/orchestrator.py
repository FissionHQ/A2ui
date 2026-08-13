from __future__ import annotations

import json
from typing import Any, AsyncIterator

from app.a2ui.examples import build_surface, clarification_surface, disabled_surface
from app.a2ui.parse import try_parse_or_repair
from app.a2ui.schema_manager import prompt_for_domain
from app.a2ui.validate import A2UIValidationError, validate_messages
from app.agents.intent_router import classify
from app.config import get_settings
from app.llm.factory import create_llm
from app.providers.fintech import MockFintechProvider
from app.providers.market import MockMarketProvider, YahooMarketProvider
from app.providers.news import HackerNewsProvider, MockNewsProvider
from app.providers.shopping import MockShoppingProvider
from app.providers.support import MockSupportProvider
from app.providers.travel import MockFlightProvider, MockHotelProvider
from app.providers.weather import MockWeatherProvider, OpenMeteoWeatherProvider


def activity(step: str, detail: str, status: str = "ok") -> dict[str, Any]:
    return {
        "version": "demo",
        "agentActivity": {"step": step, "detail": detail, "status": status},
    }


def pipeline(stage: str) -> dict[str, Any]:
    return {"version": "demo", "pipeline": {"stage": stage}}


async def _safe_call(live_fn, mock_fn, label: str):
    settings = get_settings()
    try:
        if settings.data_mode == "mock":
            return await mock_fn(), "mock"
        return await live_fn(), "live"
    except Exception:
        data = await mock_fn()
        return data, f"mock-fallback:{label}"


async def run_domain(domain: str, entities: dict[str, Any], role: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    notes: list[dict[str, Any]] = []
    focus = entities.get("focus")
    if domain == "WEATHER":
        loc = entities.get("location") or "Hyderabad"
        date = entities.get("date") or "tomorrow"
        data, src = await _safe_call(
            lambda: OpenMeteoWeatherProvider().forecast(loc, date),
            lambda: MockWeatherProvider().forecast(loc, date),
            "weather",
        )
        data["focus"] = focus or "forecast"
        notes.append(activity("tool", f"Weather for {loc} via {src}"))
        return data, notes
    if domain == "NEWS":
        topic = entities.get("topic") or "AI"
        data, src = await _safe_call(
            lambda: HackerNewsProvider().headlines(topic),
            lambda: MockNewsProvider().headlines(topic),
            "news",
        )
        notes.append(activity("tool", f"News about “{topic}” via {src}"))
        return data, notes
    if domain == "TRAVEL":
        dest = entities.get("destination") or "Goa"
        origin = entities.get("origin") or "Hyderabad"
        wx, src = await _safe_call(
            lambda: OpenMeteoWeatherProvider().forecast(dest, entities.get("duration") or "weekend"),
            lambda: MockWeatherProvider().forecast(dest, "weekend"),
            "weather",
        )
        notes.append(activity("tool", f"Weather in {dest} ({src})"))
        flight = await MockFlightProvider().search(dest)
        if origin:
            flight["title"] = f"{origin[:3].upper()} → {dest[:3].upper()}  ·  IndiGo 6E-214"
        notes.append(activity("tool", "Flight data retrieved"))
        hotel = await MockHotelProvider().search(dest)
        notes.append(activity("tool", "Hotel data retrieved"))
        data = {
            "destination": dest,
            "origin": origin,
            "dates": entities.get("duration") or "This weekend",
            "summary": f"{origin} to {dest}. Focus: {focus or 'full plan'}.",
            "weather": wx,
            "flight": flight,
            "hotel": hotel,
            "total": int(flight["price"]) + int(hotel["price"]),
            "budget": entities.get("budget"),
            "focus": focus or "full_plan",
        }
        return data, notes
    if domain == "MARKET_DATA":
        data, src = await _safe_call(
            lambda: YahooMarketProvider().overview(entities.get("market") or "INDIA"),
            lambda: MockMarketProvider().overview("INDIA"),
            "market",
        )
        data["focus"] = focus or "overview"
        notes.append(activity("tool", f"Market data via {src}"))
        return data, notes
    if domain == "SHOPPING":
        data = await MockShoppingProvider().search(
            entities.get("query") or "", int(entities.get("maxPrice") or 100000)
        )
        notes.append(activity("tool", f"Products for “{data['query']}”"))
        return data, notes
    if domain == "FINTECH":
        p = MockFintechProvider()
        if entities.get("focus") == "release_milestone" or role == "freelancer":
            data = await p.milestone()
            notes.append(activity("tool", "Milestone retrieved"))
        else:
            data = await p.invoices(role)
            notes.append(activity("tool", "Invoices retrieved"))
        return data, notes
    if domain == "CUSTOMER_SUPPORT":
        data = await MockSupportProvider().order(entities.get("issue") or "delayed_order")
        data["desiredAction"] = entities.get("desiredAction") or "refund"
        data["focus"] = entities.get("desiredAction") or "refund"
        notes.append(activity("tool", "Order timeline retrieved"))
        return data, notes
    return {}, notes


async def generate_a2ui(
    domain: str,
    data: dict[str, Any],
    role: str,
    user_prompt: str = "",
    focus: str | None = None,
) -> list[dict[str, Any]]:
    focus = focus or data.get("focus")
    templates = build_surface(domain, data, role, focus=focus)
    llm = create_llm()
    settings = get_settings()
    if llm is None or not settings.llm_configured:
        return validate_messages(templates)
    try:
        system = prompt_for_domain(domain)
        user = json.dumps(
            {
                "userPrompt": user_prompt,
                "focus": focus,
                "role": role,
                "toolResult": data,
                "formatExample": templates,
                "instruction": (
                    "Compose A2UI that answers userPrompt. "
                    "formatExample is the legal message shape, not a required layout. "
                    "Vary cards/metrics/actions to match focus. "
                    "Return a JSON array of A2UI messages."
                ),
            }
        )
        raw = await llm.complete_json(system=system, user=user)
        messages = try_parse_or_repair(raw)
        return _rebind_tool_data(messages, domain, data)
    except (A2UIValidationError, Exception):
        return validate_messages(templates)


DATA_PATHS = {
    "WEATHER": "/weather",
    "NEWS": "/news",
    "TRAVEL": "/travel",
    "MARKET_DATA": "/market",
    "SHOPPING": "/shopping",
    "FINTECH": "/fintech",
    "CUSTOMER_SUPPORT": "/support",
}


def _rebind_tool_data(messages: list[dict[str, Any]], domain: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    path = DATA_PATHS.get(domain)
    if not path:
        return messages
    rebound: list[dict[str, Any]] = []
    for msg in messages:
        if "updateDataModel" in msg:
            body = dict(msg["updateDataModel"])
            body["path"] = path
            body["value"] = data if domain != "SHOPPING" else {**data, "compared": list(data.get("compared") or [])}
            rebound.append({**msg, "updateDataModel": body})
        else:
            rebound.append(msg)
    return rebound


async def orchestrate(text: str, user_context: dict[str, Any] | None) -> AsyncIterator[dict[str, Any]]:
    ctx = user_context or {}
    role = ((ctx.get("user") or {}).get("role")) or "business-owner"
    yield pipeline("USER")
    yield pipeline("INTENT_ROUTER")
    history = ctx.get("history") if isinstance(ctx.get("history"), list) else None
    routed = await classify(text, history)
    domain = routed["domain"]
    yield activity("intent_detected", f"Intent detected: {domain}", "ok")
    if routed.get("disabled"):
        yield pipeline("A2UI_GENERATOR")
        for msg in disabled_surface(domain):
            yield msg
        return
    if routed.get("clarify"):
        yield pipeline("A2UI_GENERATOR")
        yield activity("clarify", "Prompt did not map cleanly to a domain", "ok")
        for msg in clarification_surface(text):
            yield msg
        return
    yield pipeline("DOMAIN_AGENTS")
    yield activity("agent_started", f"{domain.title()} Agent started")
    entities = routed.get("entities") or {}
    data, notes = await run_domain(domain, entities, role)
    for n in notes:
        yield n
    yield pipeline("A2UI_GENERATOR")
    yield activity("a2ui", f"Composing A2UI for “{text[:80]}”")
    messages = await generate_a2ui(domain, data, role, user_prompt=text, focus=routed.get("focus") or entities.get("focus"))
    yield pipeline("SSE")
    for msg in messages:
        yield msg
    yield activity("rendered", "Components streamed to renderer")
    yield pipeline("A2UI_RUNTIME")
    yield pipeline("COMPONENT_CATALOG")
    yield pipeline("REACT")
