from __future__ import annotations

from typing import Any

from app.a2ui.catalog import COMPONENT_NAMES, LOCAL_FUNCTIONS, REMOTE_EVENTS
from app.a2ui.validate import A2UIValidationError, validate_message


def parse_agent_output(payload: Any) -> list[dict[str, Any]]:
    messages = _as_message_list(payload)
    return [validate_message(m) for m in messages]


def try_parse_or_repair(payload: Any) -> list[dict[str, Any]]:
    try:
        return parse_agent_output(payload)
    except A2UIValidationError:
        messages = _as_message_list(payload)
        repaired = [_repair_message(m) for m in messages]
        repaired = [m for m in repaired if m]
        if not repaired:
            raise
        return [validate_message(m) for m in repaired]


def _as_message_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and "messages" in payload:
        payload = payload["messages"]
    if isinstance(payload, dict) and any(
        k in payload for k in ("createSurface", "updateComponents", "updateDataModel")
    ):
        payload = [payload]
    if not isinstance(payload, list):
        raise A2UIValidationError("Agent output must be a list of A2UI messages")
    return payload


def _repair_message(msg: Any) -> dict[str, Any] | None:
    if not isinstance(msg, dict):
        return None
    if msg.get("version") not in ("v1.0", "demo"):
        msg = {**msg, "version": "v1.0"}
    if "updateComponents" in msg:
        body = dict(msg["updateComponents"] or {})
        comps = []
        for c in body.get("components") or []:
            if not isinstance(c, dict):
                continue
            name = c.get("component")
            if name not in COMPONENT_NAMES:
                continue
            action = c.get("action")
            if isinstance(action, dict):
                fc = action.get("functionCall") or {}
                ev = action.get("event") or {}
                if fc.get("call") and fc.get("call") not in LOCAL_FUNCTIONS:
                    c = {k: v for k, v in c.items() if k != "action"}
                elif ev.get("name") and ev.get("name") not in REMOTE_EVENTS:
                    c = {k: v for k, v in c.items() if k != "action"}
            kids = c.get("children")
            if isinstance(kids, list):
                c = {**c, "children": [k for k in kids if isinstance(k, str)]}
            comps.append(c)
        body["components"] = comps
        msg = {**msg, "updateComponents": body}
    return msg


def unsupported_component_alert(surface_id: str, name: str) -> list[dict[str, Any]]:
    return [
        {
            "version": "v1.0",
            "createSurface": {"surfaceId": surface_id, "catalogId": "AppCatalog"},
        },
        {
            "version": "v1.0",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": [
                    {"id": "root", "component": "Page", "children": ["err"]},
                    {
                        "id": "err",
                        "component": "Alert",
                        "variant": "danger",
                        "title": "Unsupported A2UI component:",
                        "message": name,
                    },
                ],
            },
        },
        {
            "version": "v1.0",
            "updateDataModel": {"surfaceId": surface_id, "path": "/", "value": {}},
        },
    ]
