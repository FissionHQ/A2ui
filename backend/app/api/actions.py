from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.a2ui.catalog import REMOTE_EVENTS
from app.a2ui.examples import error_surface


async def handle_action(payload: dict[str, Any]) -> dict[str, Any]:
    name = payload.get("name")
    action_id = payload.get("actionId") or str(uuid4())
    context = payload.get("context") or {}
    surface_id = payload.get("surfaceId") or "action_surface"
    if name not in REMOTE_EVENTS:
        return {
            "actionResponse": {
                "actionId": action_id,
                "error": {"code": "NOT_ALLOWLISTED", "message": f"Remote action not allowlisted: {name}"},
            },
            "messages": error_surface("Action blocked", f"Remote action not allowlisted: {name}"),
        }
    results = {
        "book_trip": {
            "status": "confirmed",
            "bookingId": "TR-1024",
            "destination": context.get("destination"),
            "origin": context.get("origin"),
            "hotel": context.get("hotel"),
            "total": context.get("total"),
            "message": f"Mock trip to {context.get('destination') or 'your destination'} booked successfully.",
        },
        "request_refund": {"status": "ok", "refundId": "RF-331", "orderId": context.get("orderId")},
        "pay_invoice": {"status": "ok", "paymentId": "PAY-19", "invoiceId": context.get("id")},
        "release_milestone": {"status": "ok", "payoutId": "PO-88", "milestoneId": context.get("id")},
        "execute_payout": {"status": "ok", "payoutId": "PO-12"},
        "open_news": {"status": "ok", "url": context.get("url")},
        "refresh_market": {"status": "ok"},
        "search_products": {"status": "ok"},
    }
    value = results.get(name, {"status": "ok"})
    path = "/action"
    update = {
        "version": "v1.0",
        "updateDataModel": {
            "surfaceId": surface_id,
            "path": path,
            "value": value,
        },
    }
    return {
        "actionResponse": {"actionId": action_id, "value": value},
        "messages": [update],
    }
