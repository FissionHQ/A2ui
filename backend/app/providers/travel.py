from __future__ import annotations

from typing import Any


class FlightProvider:
    async def search(self, destination: str) -> dict[str, Any]:
        raise NotImplementedError


class HotelProvider:
    async def search(self, destination: str) -> dict[str, Any]:
        raise NotImplementedError


class MockFlightProvider(FlightProvider):
    async def search(self, destination: str) -> dict[str, Any]:
        dest = destination or "Goa"
        return {
            "title": f"HYD → {dest[:3].upper()}  ·  IndiGo 6E-214",
            "detail": "Fri 07:10 – 08:45  ·  nonstop",
            "price": 6420,
        }


class MockHotelProvider(HotelProvider):
    def _catalog(self, destination: str) -> list[dict[str, Any]]:
        dest = destination or "Goa"
        return [
            {"title": f"Airport Residency, {dest}", "detail": "4.3★ · 2.1 km from airport · breakfast + dinner", "price": 6200, "airportDistanceKm": 2.1, "meals": ["breakfast", "dinner"]},
            {"title": f"Skyline Airport Hotel, {dest}", "detail": "4.1★ · 0.8 km from airport · breakfast included", "price": 5200, "airportDistanceKm": 0.8, "meals": ["breakfast"]},
            {"title": f"Palm Grove, {dest}", "detail": "4.4★ · city centre · breakfast included", "price": 7800, "airportDistanceKm": 24.0, "meals": ["breakfast"]},
            {"title": f"Coastal Table Resort, {dest}", "detail": "4.6★ · beach district · breakfast + dinner", "price": 8900, "airportDistanceKm": 18.0, "meals": ["breakfast", "dinner"]},
        ]

    async def search(self, destination: str) -> dict[str, Any]:
        return self._catalog(destination)[0]

    async def search_many(self, destination: str, preferences: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        prefs = preferences or {}
        hotels = self._catalog(destination)
        if prefs.get("nearAirport"):
            hotels = [hotel for hotel in hotels if float(hotel["airportDistanceKm"]) <= 5]
        meals = {str(meal).lower() for meal in prefs.get("meals") or []}
        if meals:
            hotels = [hotel for hotel in hotels if meals.issubset(set(hotel["meals"]))]
        minimum = prefs.get("minPrice")
        maximum = prefs.get("maxPrice")
        if minimum is not None:
            hotels = [hotel for hotel in hotels if int(hotel["price"]) >= int(minimum)]
        if maximum is not None:
            hotels = [hotel for hotel in hotels if int(hotel["price"]) <= int(maximum)]
        return hotels
