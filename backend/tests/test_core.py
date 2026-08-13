from app.a2ui.catalog import COMPONENT_NAMES
from app.a2ui.json_pointer import JsonPointerError, get, set_value
from app.a2ui.validate import A2UIValidationError, validate_message
from app.agents.intent_router import classify_mock
from app.a2ui.examples import build_surface
from app.a2ui.catalog import REMOTE_EVENTS
import pytest


def test_intent_weather():
    r = classify_mock("What's the weather in Hyderabad tomorrow?")
    assert r["domain"] == "WEATHER"
    assert r["entities"]["location"] == "Hyderabad"


def test_intent_news():
    assert classify_mock("Show me today's AI news.")["domain"] == "NEWS"


def test_intent_travel():
    r = classify_mock("Plan a weekend trip to Goa.")
    assert r["domain"] == "TRAVEL"
    assert r["entities"]["destination"] == "Goa"


def test_intent_market():
    assert classify_mock("How is the Indian stock market doing?")["domain"] == "MARKET_DATA"


def test_intent_shopping():
    r = classify_mock("Find headphones under ₹10,000.")
    assert r["domain"] == "SHOPPING"
    assert r["entities"]["maxPrice"] == 10000


def test_intent_fintech():
    assert classify_mock("Show me invoices that need attention.")["domain"] == "FINTECH"


def test_intent_shopping_generic():
    r = classify_mock("Find running shoes under 4000")
    assert r["domain"] == "SHOPPING"
    assert "shoe" in r["entities"]["query"].lower()
    assert r["entities"]["maxPrice"] == 4000


def test_intent_shopping_phones():
    r = classify_mock("find phones")
    assert r["domain"] == "SHOPPING"
    assert "phone" in r["entities"]["query"].lower()
    assert "headphone" not in r["entities"]["query"].lower()


def test_shopping_phones_do_not_match_headphones():
    from app.providers.shopping import search_catalog

    phones = search_catalog("phones")
    titles = " ".join(p["title"] for p in phones["products"]).lower()
    assert "galaxy" in titles or "oneplus" in titles or "pixel" in titles
    assert "sony" not in titles
    assert "headphone" not in titles
    assert phones["query"] == "phones"

    audio = search_catalog("headphones")
    audio_titles = " ".join(p["title"] for p in audio["products"]).lower()
    assert "sony" in audio_titles or "jbl" in audio_titles or "boat" in audio_titles
    assert "galaxy" not in audio_titles


def test_shopping_llm_cannot_invent_headphones():
    from app.agents.intent_router import _merge_entities

    merged = _merge_entities("find phones", "SHOPPING", {"query": "headphones", "maxPrice": 100000})
    assert "phone" in str(merged["query"]).lower()
    assert "headphone" not in str(merged["query"]).lower()


def test_intent_weather_rain_focus():
    r = classify_mock("Will it rain in Jaipur tomorrow?")
    assert r["domain"] == "WEATHER"
    assert r["entities"]["location"] == "Jaipur"
    assert r["entities"]["focus"] == "rain"


def test_intent_unknown_clarifies():
    r = classify_mock("Write a haiku about entropy")
    assert r["domain"] == "UNKNOWN"



def test_json_pointer():
    doc = {"weather": {"currentTemperature": 31}}
    assert get(doc, "/weather/currentTemperature") == 31
    set_value(doc, "/weather/rainProbability", 20)
    assert doc["weather"]["rainProbability"] == 20
    set_value(doc, "/weather/rainProbability", None)
    assert "rainProbability" not in doc["weather"]
    with pytest.raises(JsonPointerError):
        get(doc, "weather/temp")


def test_unsupported_component():
    with pytest.raises(A2UIValidationError) as exc:
        validate_message(
            {
                "version": "v1.0",
                "updateComponents": {
                    "surfaceId": "x",
                    "components": [{"id": "root", "component": "SuperFancyWidget"}],
                },
            }
        )
    assert "Unsupported A2UI component" in str(exc.value)


def test_catalog_known():
    assert "WeatherCard" in COMPONENT_NAMES
    assert "book_trip" in REMOTE_EVENTS


def test_surface_lifecycle_each_domain():
    for domain in [
        "WEATHER",
        "NEWS",
        "TRAVEL",
        "MARKET_DATA",
        "SHOPPING",
        "FINTECH",
        "CUSTOMER_SUPPORT",
    ]:
        msgs = build_surface(domain, {"location": "Hyderabad", "temperature": 31, "rainProbability": 10, "hourly": [], "articles": [], "products": [], "invoices": [], "movers": [], "series": [], "nifty": {}, "sensex": {}, "flight": {"price": 1, "title": "x", "detail": "x"}, "hotel": {"price": 1, "title": "x", "detail": "x"}, "weather": {"location": "Goa", "condition": "Sun", "temperature": 30}, "total": 2, "timeline": []})
        keys = [next(k for k in m if k not in ("version",)) for m in msgs]
        assert keys[0] == "createSurface"
        assert keys[1] == "updateComponents"
        assert keys[2] == "updateDataModel"
        for m in msgs:
            validate_message(m)
