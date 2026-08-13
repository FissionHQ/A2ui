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
    async def search(self, destination: str) -> dict[str, Any]:
        dest = destination or "Goa"
        return {
            "title": f"Palm Grove, {dest}",
            "detail": "4.4★  ·  Calangute  ·  breakfast included",
            "price": 7800,
        }
