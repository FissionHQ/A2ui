from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.a2ui.catalog import CATALOG_ID


def envelope(surface_id: str, components: list[dict[str, Any]], path: str, value: Any) -> list[dict[str, Any]]:
    return [
        {
            "version": "v1.0",
            "createSurface": {"surfaceId": surface_id, "catalogId": CATALOG_ID},
        },
        {
            "version": "v1.0",
            "updateComponents": {"surfaceId": surface_id, "components": components},
        },
        {
            "version": "v1.0",
            "updateDataModel": {"surfaceId": surface_id, "path": path, "value": value},
        },
    ]


def weather_surface(data: dict[str, Any], focus: str = "forecast") -> list[dict[str, Any]]:
    metric_ids = ["temperature", "humidity", "rain"]
    if focus == "rain":
        metric_ids = ["rain", "temperature"]
    elif focus == "humidity":
        metric_ids = ["humidity", "temperature"]
    elif focus == "temperature":
        metric_ids = ["temperature", "rain"]
    show_chart = focus in ("forecast", "temperature")
    root_children = ["summary", "metrics"]
    if show_chart:
        root_children.append("forecast")
    if data.get("rainProbability", 0) >= 50 or focus == "rain":
        root_children.append("alert")
    components: list[dict[str, Any]] = [
        {"id": "root", "component": "Page", "children": root_children},
        {
            "id": "summary",
            "component": "WeatherCard",
            "location": {"path": "/weather/location"},
            "condition": {"path": "/weather/condition"},
            "temperature": {"path": "/weather/temperature"},
            "date": {"path": "/weather/date"},
        },
        {"id": "metrics", "component": "List", "children": metric_ids},
        {
            "id": "temperature",
            "component": "MetricCard",
            "title": "Temperature",
            "unit": "°C",
            "value": {"path": "/weather/temperature"},
        },
        {
            "id": "humidity",
            "component": "MetricCard",
            "title": "Humidity",
            "unit": "%",
            "value": {"path": "/weather/humidity"},
        },
        {
            "id": "rain",
            "component": "MetricCard",
            "title": "Rain chance",
            "unit": "%",
            "value": {"path": "/weather/rainProbability"},
        },
        {
            "id": "forecast",
            "component": "ForecastChart",
            "title": "Hourly outlook",
            "series": {"path": "/weather/hourly"},
        },
    ]
    if "alert" in root_children:
        components.append(
            {
                "id": "alert",
                "component": "Alert",
                "variant": "warning" if data.get("rainProbability", 0) >= 50 else "info",
                "title": "Carry an umbrella" if data.get("rainProbability", 0) >= 50 else "Rain outlook",
                "message": {"path": "/weather/alert"},
            }
        )
    return envelope("weather_surface", components, "/weather", data)


def weather_comparison_surface(data: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[str] = []
    components: list[dict[str, Any]] = []
    for index, forecast in enumerate(data.get("locations") or []):
        base = f"/weather/locations/{index}"
        group_id = f"location_{index}"
        card_id = f"weather_{index}"
        metric_list_id = f"metrics_{index}"
        metric_ids = [f"temperature_{index}", f"humidity_{index}", f"rain_{index}"]
        groups.append(group_id)
        components.extend(
            [
                {"id": group_id, "component": "Card", "children": [card_id, metric_list_id]},
                {
                    "id": card_id,
                    "component": "WeatherCard",
                    "location": {"path": f"{base}/location"},
                    "condition": {"path": f"{base}/condition"},
                    "temperature": {"path": f"{base}/temperature"},
                    "date": {"path": f"{base}/date"},
                },
                {"id": metric_list_id, "component": "List", "children": metric_ids},
                {
                    "id": metric_ids[0], "component": "MetricCard",
                    "title": f"{forecast.get('location', '')} · Temperature", "unit": "°C",
                    "value": {"path": f"{base}/temperature"},
                },
                {
                    "id": metric_ids[1], "component": "MetricCard",
                    "title": f"{forecast.get('location', '')} · Humidity", "unit": "%",
                    "value": {"path": f"{base}/humidity"},
                },
                {
                    "id": metric_ids[2], "component": "MetricCard",
                    "title": f"{forecast.get('location', '')} · Rain chance", "unit": "%",
                    "value": {"path": f"{base}/rainProbability"},
                },
            ]
        )
    return envelope(
        "weather_comparison_surface",
        [
            {"id": "root", "component": "Page", "children": ["comparison"]},
            {"id": "comparison", "component": "List", "children": groups},
            *components,
        ],
        "/weather",
        data,
    )


def news_surface(data: dict[str, Any]) -> list[dict[str, Any]]:
    components = [
        {"id": "root", "component": "Page", "children": ["tabs", "list"]},
        {
            "id": "tabs",
            "component": "Tabs",
            "value": {"path": "/news/activeTab"},
            "tabs": [
                {"id": "top", "label": "Top"},
                {"id": "ai", "label": "AI"},
                {"id": "india", "label": "India"},
            ],
            "action": {"functionCall": {"call": "changeTab", "args": {"path": "/news/activeTab"}}},
        },
        {
            "id": "list",
            "component": "NewsList",
            "children": {"componentId": "article_template", "path": "/news/articles"},
        },
        {
            "id": "article_template",
            "component": "NewsCard",
            "title": {"path": "/news/articles/@index/title"},
            "source": {"path": "/news/articles/@index/source"},
            "summary": {"path": "/news/articles/@index/summary"},
            "imageUrl": {"path": "/news/articles/@index/imageUrl"},
            "badge": {"path": "/news/articles/@index/topic"},
            "action": {
                "event": {
                    "name": "open_news",
                    "context": {"url": {"path": "/news/articles/@index/url"}},
                }
            },
        },
    ]
    return envelope("news_surface", components, "/news", data)


def travel_surface(data: dict[str, Any], focus: str = "full_plan") -> list[dict[str, Any]]:
    children = ["trip", "wx"]
    if focus != "hotels":
        children.append("flight")
    if focus != "flights":
        children.extend(["hotel_note", "hotel_options"])
    children.extend(["price", "book"])
    components = [
        {"id": "root", "component": "Page", "children": children},
        {
            "id": "trip",
            "component": "TravelCard",
            "destination": {"path": "/travel/destination"},
            "dates": {"path": "/travel/dates"},
            "summary": {"path": "/travel/summary"},
        },
        {
            "id": "wx",
            "component": "WeatherCard",
            "location": {"path": "/travel/weather/location"},
            "condition": {"path": "/travel/weather/condition"},
            "temperature": {"path": "/travel/weather/temperature"},
        },
        {
            "id": "flight",
            "component": "FlightCard",
            "title": {"path": "/travel/flight/title"},
            "detail": {"path": "/travel/flight/detail"},
            "price": {"path": "/travel/flight/price"},
        },
        {
            "id": "hotel_note",
            "component": "Alert",
            "variant": "info",
            "title": "Hotels matched to your stay",
            "message": {"path": "/travel/hotelPreferenceNote"},
        },
        {
            "id": "hotel_options",
            "component": "List",
            "children": {"componentId": "hotel_template", "path": "/travel/hotels"},
        },
        {
            "id": "hotel_template",
            "component": "HotelCard",
            "title": {"path": "/travel/hotels/@index/title"},
            "detail": {"path": "/travel/hotels/@index/detail"},
            "price": {"path": "/travel/hotels/@index/price"},
        },
        {
            "id": "price",
            "component": "MetricCard",
            "title": "Est. weekend total",
            "unit": "INR",
            "value": {"path": "/travel/total"},
        },
        {
            "id": "book",
            "component": "Button",
            "label": "Book this trip",
            "variant": "primary",
            "action": {
                "event": {
                    "name": "book_trip",
                    "context": {
                        "destination": {"path": "/travel/destination"},
                        "origin": {"path": "/travel/origin"},
                        "hotel": {"path": "/travel/hotel/title"},
                        "total": {"path": "/travel/total"},
                    },
                }
            },
        },
    ]
    return envelope("travel_surface", components, "/travel", data)


def market_surface(data: dict[str, Any], focus: str = "overview") -> list[dict[str, Any]]:
    children = ["header"]
    metric_ids: list[str] = []
    if focus != "sensex":
        metric_ids.append("nifty")
    if focus != "nifty":
        metric_ids.append("sensex")
    if metric_ids:
        children.append("metrics")
    if focus == "news_impact":
        children.extend(["impact_note", "impact_news"])
    if focus in ("overview", "nifty", "news_impact"):
        children.append("chart")
    if focus in ("overview", "movers"):
        children.append("movers")
    components = [
        {"id": "root", "component": "Page", "children": children},
        {
            "id": "header",
            "component": "MarketCard",
            "title": {"path": "/market/title"},
            "asOf": {"path": "/market/asOf"},
        },
        {"id": "metrics", "component": "List", "children": metric_ids or ["nifty"]},
        {
            "id": "nifty",
            "component": "MetricCard",
            "title": "NIFTY 50",
            "value": {"path": "/market/nifty/value"},
            "delta": {"path": "/market/nifty/changePct"},
        },
        {
            "id": "sensex",
            "component": "MetricCard",
            "title": "SENSEX",
            "value": {"path": "/market/sensex/value"},
            "delta": {"path": "/market/sensex/changePct"},
        },
        {
            "id": "chart",
            "component": "Chart",
            "title": "NIFTY 30d",
            "series": {"path": "/market/series"},
        },
        {
            "id": "movers",
            "component": "Table",
            "columns": ["Symbol", "Last", "Change", "Status"],
            "rowsPath": "/market/movers",
        },
        {
            "id": "impact_note",
            "component": "Alert",
            "variant": "warning",
            "title": "What may be influencing the market",
            "message": {"path": "/market/newsImpact/disclaimer"},
        },
        {
            "id": "impact_news",
            "component": "NewsList",
            "children": {"componentId": "impact_article", "path": "/market/newsImpact/articles"},
        },
        {
            "id": "impact_article",
            "component": "NewsCard",
            "title": {"path": "/market/newsImpact/articles/@index/title"},
            "source": {"path": "/market/newsImpact/articles/@index/source"},
            "summary": {"path": "/market/newsImpact/articles/@index/summary"},
            "imageUrl": {"path": "/market/newsImpact/articles/@index/imageUrl"},
            "badge": {"path": "/market/newsImpact/articles/@index/topic"},
            "action": {
                "event": {
                    "name": "open_news",
                    "context": {"url": {"path": "/market/newsImpact/articles/@index/url"}},
                }
            },
        },
    ]
    return envelope("market_surface", components, "/market", data)


def shopping_surface(data: dict[str, Any]) -> list[dict[str, Any]]:
    payload = {**data, "compared": list(data.get("compared") or [])}
    count = len(payload.get("products") or [])
    components = [
        {"id": "root", "component": "Page", "children": ["heading", "list", "tray"]},
        {
            "id": "heading",
            "component": "Alert",
            "variant": "info",
            "title": {"path": "/shopping/query"},
            "message": f"{count} matches · tap Compare to add up to 3 products",
        },
        {
            "id": "list",
            "component": "ProductList",
            "children": {"componentId": "product_template", "path": "/shopping/products"},
        },
        {
            "id": "product_template",
            "component": "ProductCard",
            "title": {"path": "/shopping/products/@index/title"},
            "price": {"path": "/shopping/products/@index/price"},
            "rating": {"path": "/shopping/products/@index/rating"},
            "imageUrl": {"path": "/shopping/products/@index/imageUrl"},
            "children": ["compare"],
        },
        {
            "id": "compare",
            "component": "CompareButton",
            "label": "Compare",
            "action": {"functionCall": {"call": "toggleCompare", "args": {}}},
        },
        {
            "id": "tray",
            "component": "CompareTray",
            "items": {"path": "/shopping/compared"},
            "action": {"functionCall": {"call": "clearCompare", "args": {}}},
        },
    ]
    return envelope("shopping_surface", components, "/shopping", payload)


def fintech_surface(data: dict[str, Any], role: str = "business-owner") -> list[dict[str, Any]]:
    if role == "freelancer" or data.get("focus") == "release_milestone":
        components = [
            {"id": "root", "component": "Page", "children": ["metric", "mile"]},
            {
                "id": "metric",
                "component": "MetricCard",
                "title": "Ready to release",
                "unit": "INR",
                "value": {"path": "/fintech/readyAmount"},
            },
            {
                "id": "mile",
                "component": "MilestoneCard",
                "title": {"path": "/fintech/milestone/title"},
                "client": {"path": "/fintech/milestone/client"},
                "amount": {"path": "/fintech/milestone/amount"},
                "status": {"path": "/fintech/milestone/status"},
                "action": {
                    "event": {
                        "name": "release_milestone",
                        "context": {"id": {"path": "/fintech/milestone/id"}},
                    }
                },
            },
        ]
    else:
        children = ["metrics", "table"]
        metric_ids = ["open", "overdue"]
        components = [
            {"id": "root", "component": "Page", "children": children},
            {"id": "metrics", "component": "List", "children": metric_ids},
            {
                "id": "open",
                "component": "MetricCard",
                "title": "Open invoices",
                "value": {"path": "/fintech/openCount"},
            },
            {
                "id": "overdue",
                "component": "MetricCard",
                "title": "Overdue",
                "unit": "INR",
                "value": {"path": "/fintech/overdueAmount"},
            },
            {
                "id": "table",
                "component": "InvoiceTable",
                "rowsPath": "/fintech/invoices",
                "payEvent": "pay_invoice",
            },
        ]
        if role == "finance-manager":
            components[1]["children"] = ["open", "overdue", "aging"]
            components.insert(
                4,
                {
                    "id": "aging",
                    "component": "MetricCard",
                    "title": "90+ days risk",
                    "unit": "INR",
                    "value": {"path": "/fintech/aging90"},
                },
            )
    return envelope("fintech_surface", components, "/fintech", data)


def support_surface(data: dict[str, Any], focus: str = "refund") -> list[dict[str, Any]]:
    children = ["order", "status", "timeline", "alert"]
    if focus != "status":
        children.append("refund")
    components = [
        {"id": "root", "component": "Page", "children": children},
        {
            "id": "order",
            "component": "OrderCard",
            "orderId": {"path": "/support/orderId"},
            "item": {"path": "/support/item"},
            "eta": {"path": "/support/eta"},
        },
        {
            "id": "status",
            "component": "StatusChip",
            "label": {"path": "/support/status"},
            "tone": {"path": "/support/tone"},
        },
        {
            "id": "timeline",
            "component": "Timeline",
            "items": {"path": "/support/timeline"},
        },
        {
            "id": "alert",
            "component": "Alert",
            "variant": "warning",
            "title": "Delay detected",
            "message": {"path": "/support/message"},
        },
        {
            "id": "refund",
            "component": "RefundButton",
            "label": "Request refund",
            "variant": "danger",
            "action": {
                "event": {
                    "name": "request_refund",
                    "context": {"orderId": {"path": "/support/orderId"}},
                }
            },
        },
    ]
    return envelope("support_surface", components, "/support", data)


def books_surface(data: dict[str, Any]) -> list[dict[str, Any]]:
    count = len(data.get("books") or [])
    components = [
        {"id": "root", "component": "Page", "children": ["heading", "list"]},
        {
            "id": "heading",
            "component": "Alert",
            "variant": "info",
            "title": {"path": "/books/label"},
            "message": f"{count} titles",
        },
        {
            "id": "list",
            "component": "ItemList",
            "children": {"componentId": "book_template", "path": "/books/books"},
        },
        {
            "id": "book_template",
            "component": "ItemCard",
            "icon": "star",
            "title": {"path": "/books/books/@index/title"},
            "subtitle": {"path": "/books/books/@index/author"},
            "badge": {"path": "/books/books/@index/genre"},
            "year": {"path": "/books/books/@index/year"},
            "rating": {"path": "/books/books/@index/rating"},
        },
    ]
    return envelope("books_surface", components, "/books", data)


def movies_surface(data: dict[str, Any], focus: str = "") -> list[dict[str, Any]]:
    components = [
        {"id": "root", "component": "Page", "children": ["heading", "list"]},
        {
            "id": "heading",
            "component": "Alert",
            "variant": "info",
            "title": {"path": "/movies/label"},
            "message": f"{len(data.get('movies', []))} titles",
        },
        {
            "id": "list",
            "component": "ItemList",
            "children": {"componentId": "movie_template", "path": "/movies/movies"},
        },
        {
            "id": "movie_template",
            "component": "ItemCard",
            "icon": {"path": "/movies/movies/@index/icon"},
            "title": {"path": "/movies/movies/@index/title"},
            "year": {"path": "/movies/movies/@index/year"},
            "rating": {"path": "/movies/movies/@index/rating"},
            "badge": {"path": "/movies/movies/@index/genre"},
            "director": {"path": "/movies/movies/@index/director"},
        },
    ]
    return envelope("movies_surface", components, "/movies", data)


def disabled_surface(domain: str) -> list[dict[str, Any]]:
    return envelope(
        "error_surface",
        [
            {"id": "root", "component": "Page", "children": ["err"]},
            {
                "id": "err",
                "component": "Alert",
                "variant": "info",
                "title": "Domain not enabled",
                "message": f"{domain} is not in ENABLED_DOMAINS.",
            },
        ],
        "/",
        {},
    )


def error_surface(title: str, message: str) -> list[dict[str, Any]]:
    return envelope(
        "error_surface",
        [
            {"id": "root", "component": "Page", "children": ["err"]},
            {"id": "err", "component": "Alert", "variant": "danger", "title": title, "message": message},
        ],
        "/",
        {},
    )


def clarification_surface(prompt: str, question: str | None = None) -> list[dict[str, Any]]:
    specific = question or (
        f"I didn't map “{prompt}” to a single domain. Try weather, news, travel, "
        "Indian markets, shopping, invoices/milestones, or an order/refund."
    )
    return envelope(
        "clarify_surface",
        [
            {"id": "root", "component": "Page", "children": ["alert"]},
            {
                "id": "alert",
                "component": "Alert",
                "variant": "info",
                "title": "One detail needed",
                "message": specific,
            },
        ],
        "/",
        {"prompt": prompt},
    )


def build_surface(
    domain: str,
    data: dict[str, Any],
    role: str = "business-owner",
    focus: str | None = None,
) -> list[dict[str, Any]]:
    focus = focus or data.get("focus") or ""
    builders = {
        "WEATHER": lambda: weather_comparison_surface(data)
        if data.get("comparison")
        else weather_surface(data, focus or "forecast"),
        "NEWS": lambda: news_surface(data),
        "TRAVEL": lambda: travel_surface(data, focus or "full_plan"),
        "MARKET_DATA": lambda: market_surface(data, focus or "overview"),
        "SHOPPING": lambda: shopping_surface(data),
        "FINTECH": lambda: fintech_surface(data, role),
        "CUSTOMER_SUPPORT": lambda: support_surface(data, focus or data.get("desiredAction") or "refund"),
        "MOVIES": lambda: movies_surface(data, focus or "top_rated"),
        "BOOKS": lambda: books_surface(data),
    }
    fn = builders.get(domain)
    if not fn:
        return error_surface("Unknown domain", domain)
    return deepcopy(fn())
