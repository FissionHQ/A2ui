from __future__ import annotations

from typing import Any


class FintechProvider:
    async def invoices(self, role: str) -> dict[str, Any]:
        raise NotImplementedError

    async def milestone(self) -> dict[str, Any]:
        raise NotImplementedError


class MockFintechProvider(FintechProvider):
    async def invoices(self, role: str) -> dict[str, Any]:
        invoices = [
            {
                "id": "INV-1042",
                "customer": "Northwind Traders",
                "amount": 185000,
                "due": "2026-08-10",
                "status": "overdue",
            },
            {
                "id": "INV-1055",
                "customer": "Brightloop Labs",
                "amount": 64000,
                "due": "2026-08-18",
                "status": "due-soon",
            },
            {
                "id": "INV-1061",
                "customer": "Kaveri Mills",
                "amount": 22000,
                "due": "2026-08-28",
                "status": "open",
            },
        ]
        return {
            "focus": "invoices_attention",
            "openCount": 3,
            "overdueAmount": 185000,
            "aging90": 185000 if role == "finance-manager" else 0,
            "invoices": invoices,
            "source": "mock",
        }

    async def milestone(self) -> dict[str, Any]:
        return {
            "focus": "release_milestone",
            "readyAmount": 125000,
            "milestone": {
                "id": "MS-88",
                "title": "Phase 2 delivery — mobile checkout",
                "client": "Brightloop Labs",
                "amount": 125000,
                "status": "approved",
            },
            "source": "mock",
        }
