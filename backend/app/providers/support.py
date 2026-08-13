from __future__ import annotations

from typing import Any


class SupportProvider:
    async def order(self, issue: str = "delayed_order") -> dict[str, Any]:
        raise NotImplementedError


class MockSupportProvider(SupportProvider):
    async def order(self, issue: str = "delayed_order") -> dict[str, Any]:
        return {
            "orderId": "ORD-77421",
            "item": "Noise VS104 Pro",
            "eta": "Originally 11 Aug · now 16 Aug",
            "status": "Delayed",
            "tone": "warning",
            "message": "Carrier scan stalled in Pune hub. Refund is eligible after 24h more delay.",
            "timeline": [
                {"title": "Placed", "detail": "7 Aug 14:12"},
                {"title": "Packed", "detail": "8 Aug 09:40"},
                {"title": "In transit", "detail": "9 Aug 18:02"},
                {"title": "Hub delay", "detail": "12 Aug 11:20"},
            ],
            "source": "mock",
        }
