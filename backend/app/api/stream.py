from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator

from sse_starlette.sse import ServerSentEvent

from app.a2ui.validate import A2UIValidationError, validate_message
from app.agents.orchestrator import orchestrate


def _event_name(msg: dict[str, Any]) -> str:
    if msg.get("version") == "demo":
        return "demo"
    return "a2ui"


async def stream_intent(text: str, user_context: dict[str, Any] | None) -> AsyncIterator[ServerSentEvent]:
    try:
        async for msg in orchestrate(text, user_context):
            if msg.get("version") != "demo":
                try:
                    validate_message(msg)
                except A2UIValidationError as exc:
                    err = {
                        "version": "demo",
                        "agentActivity": {
                            "step": "validation_error",
                            "detail": str(exc),
                            "status": "error",
                        },
                    }
                    yield ServerSentEvent(event="demo", data=json.dumps(err))
                    continue
            yield ServerSentEvent(event=_event_name(msg), data=json.dumps(msg))
            await asyncio.sleep(0.05)
        yield ServerSentEvent(event="done", data="{}")
    except Exception as exc:  # noqa: BLE001
        payload = {
            "version": "demo",
            "agentActivity": {"step": "fatal", "detail": str(exc), "status": "error"},
        }
        yield ServerSentEvent(event="demo", data=json.dumps(payload))
        yield ServerSentEvent(event="done", data="{}")
