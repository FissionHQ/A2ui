from app.config import get_settings


CATALOG_ID = "AppCatalog"
PROTOCOL_VERSION = "v1.0"

COMPONENT_NAMES = [
    "Page",
    "Card",
    "MetricCard",
    "List",
    "ListItem",
    "Table",
    "TableRow",
    "Badge",
    "StatusChip",
    "Button",
    "Image",
    "Chart",
    "Tabs",
    "Progress",
    "Timeline",
    "Alert",
    "WeatherCard",
    "NewsCard",
    "TravelCard",
    "MarketCard",
    "ProductCard",
    "InvoiceTable",
    "MilestoneCard",
    "ForecastChart",
    "NewsList",
    "FlightCard",
    "HotelCard",
    "ProductList",
    "Rating",
    "Price",
    "CompareButton",
    "CompareTray",
    "PayButton",
    "OrderCard",
    "RefundButton",
]

LOCAL_FUNCTIONS = {
    "changeTab",
    "filterList",
    "sortList",
    "searchList",
    "toggleCompare",
    "clearCompare",
}

REMOTE_EVENTS = {
    "execute_payout",
    "book_trip",
    "request_refund",
    "open_news",
    "refresh_market",
    "pay_invoice",
    "release_milestone",
    "search_products",
}

DOMAIN_COMPONENTS: dict[str, list[str]] = {
    "WEATHER": ["Page", "Card", "List", "WeatherCard", "MetricCard", "ForecastChart", "Chart", "Alert"],
    "NEWS": ["Page", "NewsCard", "NewsList", "List", "Image", "Badge", "Tabs"],
    "TRAVEL": [
        "Page",
        "List",
        "TravelCard",
        "WeatherCard",
        "FlightCard",
        "HotelCard",
        "MetricCard",
        "Button",
    ],
    "MARKET_DATA": ["Page", "List", "MarketCard", "MetricCard", "Chart", "Table", "TableRow", "StatusChip", "Alert", "NewsList", "NewsCard", "Image", "Badge"],
    "SHOPPING": [
        "Page",
        "ProductCard",
        "ProductList",
        "List",
        "Rating",
        "Price",
        "CompareButton",
        "CompareTray",
        "Button",
        "Alert",
    ],
    "FINTECH": ["Page", "List", "MetricCard", "InvoiceTable", "Table", "StatusChip", "PayButton", "MilestoneCard"],
    "CUSTOMER_SUPPORT": ["Page", "OrderCard", "StatusChip", "Timeline", "Alert", "RefundButton"],
}


def enabled_domains() -> set[str]:
    return get_settings().domains
