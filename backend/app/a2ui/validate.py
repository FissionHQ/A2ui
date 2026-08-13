from __future__ import annotations

from typing import Any

from app.a2ui.catalog import (
    CATALOG_ID,
    COMPONENT_NAMES,
    LOCAL_FUNCTIONS,
    PROTOCOL_VERSION,
    REMOTE_EVENTS,
)


class A2UIValidationError(ValueError):
    def __init__(self, message: str, payload: Any | None = None):
        super().__init__(message)
        self.payload = payload


MESSAGE_KEYS = (
    "createSurface",
    "updateComponents",
    "updateDataModel",
    "deleteSurface",
    "actionResponse",
)


def validate_message(msg: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(msg, dict):
        raise A2UIValidationError("Malformed message: expected object")
    if msg.get("version") not in (PROTOCOL_VERSION, "demo"):
        raise A2UIValidationError(f"Malformed message: unsupported version {msg.get('version')}")
    if msg.get("version") == "demo":
        return msg
    present = [k for k in MESSAGE_KEYS if k in msg]
    if len(present) != 1:
        raise A2UIValidationError("Malformed message: expected exactly one A2UI key")
    key = present[0]
    body = msg[key]
    if not isinstance(body, dict):
        raise A2UIValidationError(f"Malformed message: {key} must be an object")
    if key == "createSurface":
        if not body.get("surfaceId"):
            raise A2UIValidationError("createSurface missing surfaceId")
        catalog = body.get("catalogId", CATALOG_ID)
        if catalog != CATALOG_ID:
            raise A2UIValidationError(f"Unsupported catalog: {catalog}")
        if "components" in body:
            _validate_components(body["components"])
    elif key == "updateComponents":
        if not body.get("surfaceId"):
            raise A2UIValidationError("updateComponents missing surfaceId")
        _validate_components(body.get("components") or [])
    elif key == "updateDataModel":
        if not body.get("surfaceId"):
            raise A2UIValidationError("updateDataModel missing surfaceId")
        if "value" not in body:
            raise A2UIValidationError("updateDataModel missing value")
        path = body.get("path", "/")
        if path != "/" and not str(path).startswith("/"):
            raise A2UIValidationError(f"Invalid JSON Pointer: {path}")
    elif key == "deleteSurface":
        if not body.get("surfaceId"):
            raise A2UIValidationError("deleteSurface missing surfaceId")
    elif key == "actionResponse":
        if not body.get("actionId"):
            raise A2UIValidationError("actionResponse missing actionId")
    return msg


def _validate_components(components: Any) -> None:
    if not isinstance(components, list):
        raise A2UIValidationError("components must be a flat list")
    ids: set[str] = set()
    for comp in components:
        if not isinstance(comp, dict):
            raise A2UIValidationError("component must be an object")
        cid = comp.get("id")
        name = comp.get("component")
        if not cid or not isinstance(cid, str):
            raise A2UIValidationError("component missing id")
        if not name:
            raise A2UIValidationError("component missing component discriminator")
        if name not in COMPONENT_NAMES:
            raise A2UIValidationError(f"Unsupported A2UI component:\n{name}")
        if "children" in comp and not (
            isinstance(comp["children"], list)
            or (isinstance(comp["children"], dict) and "path" in comp["children"])
        ):
            raise A2UIValidationError("children must be an id list or template")
        if isinstance(comp.get("children"), list) and any(
            isinstance(c, dict) and "component" in c for c in comp["children"]
        ):
            raise A2UIValidationError("children must reference component IDs, not nested objects")
        action = comp.get("action")
        if action:
            _validate_action(action)
        ids.add(cid)
    if components and "root" not in ids and not any(c.get("id") == "root" for c in components):
        # Progressive updates may omit root; allow if this is a patch.
        pass


def _validate_action(action: dict[str, Any]) -> None:
    if "functionCall" in action:
        call = action["functionCall"].get("call")
        if call not in LOCAL_FUNCTIONS:
            raise A2UIValidationError(f"Unsupported local functionCall: {call}")
    if "event" in action:
        name = action["event"].get("name")
        if name not in REMOTE_EVENTS:
            raise A2UIValidationError(f"Remote action not allowlisted: {name}")


def validate_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_message(m) for m in messages]
