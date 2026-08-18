from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.a2ui.catalog import COMPONENT_NAMES, LOCAL_FUNCTIONS, REMOTE_EVENTS, enabled_domains
from app.api.actions import handle_action
from app.api.stream import stream_intent
from app.config import get_settings
from app.llm.factory import create_llm

app = FastAPI(title="A2UI Adaptive Experience Engine")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StreamBody(BaseModel):
    text: str
    userContext: dict[str, Any] | None = None
    activeSurfaceId: str | None = None
    history: list[dict[str, Any]] | None = None


class ActionBody(BaseModel):
    name: str
    surfaceId: str | None = None
    actionId: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    dataModel: dict[str, Any] | None = None
    userContext: dict[str, Any] | None = None


@app.get("/api/health")
def health():
    llm = create_llm()
    return {
        "ok": True,
        "llmConfigured": settings.llm_configured,
        "llmProvider": settings.llm_provider,
        "llmModel": settings.llm_model,
        "generationModel": settings.gemini_generation_model,
        "llmHost": type(llm).__name__ if llm else "MockAgentMode",
        "dataMode": settings.data_mode,
        "enabledDomains": sorted(enabled_domains()),
        "demoMode": not settings.llm_configured,
    }


@app.get("/api/catalog")
def catalog():
    return {
        "catalogId": "AppCatalog",
        "components": COMPONENT_NAMES,
        "localFunctions": sorted(LOCAL_FUNCTIONS),
        "remoteEvents": sorted(REMOTE_EVENTS),
    }


@app.post("/api/stream")
async def stream(body: StreamBody):
    ctx = dict(body.userContext or {})
    if body.history:
        ctx["history"] = body.history
    return EventSourceResponse(stream_intent(body.text, ctx))


@app.get("/api/stream")
async def stream_get(q: str, userContext: str | None = None):
    ctx = None
    if userContext:
        import json

        ctx = json.loads(userContext)
    return EventSourceResponse(stream_intent(q, ctx))


@app.post("/api/handle-action")
async def action(body: ActionBody):
    return await handle_action(body.model_dump())
