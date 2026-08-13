from app.config import get_settings
from app.providers.fintech import MockFintechProvider
from app.providers.market import MockMarketProvider, YahooMarketProvider
from app.providers.news import HackerNewsProvider, MockNewsProvider
from app.providers.shopping import MockShoppingProvider
from app.providers.support import MockSupportProvider
from app.providers.travel import MockFlightProvider, MockHotelProvider
from app.providers.weather import MockWeatherProvider, OpenMeteoWeatherProvider


async def weather():
    settings = get_settings()
    if settings.data_mode == "mock":
        return MockWeatherProvider()
    return OpenMeteoWeatherProvider()


async def news():
    settings = get_settings()
    if settings.data_mode == "mock":
        return MockNewsProvider()
    return HackerNewsProvider()


async def market():
    settings = get_settings()
    if settings.data_mode == "mock":
        return MockMarketProvider()
    return YahooMarketProvider()


def flights():
    return MockFlightProvider()


def hotels():
    return MockHotelProvider()


def shopping():
    return MockShoppingProvider()


def fintech():
    return MockFintechProvider()


def support():
    return MockSupportProvider()
