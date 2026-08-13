from __future__ import annotations

import json
import re
from typing import Any, AsyncIterator

import httpx

from app.llm.base import LLMError


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str, generation_model: str, base_url: str = ""):
        self.api_key = api_key
        self.model = model
        self.generation_model = generation_model or "gemini-3.6-flash"
        self.base_url = (base_url or "https://generativelanguage.googleapis.com").rstrip("/")

    async def complete_json(self, *, system: str, user: str, schema: dict | None = None) -> dict | list:
        text = await self._generate(system, user)
        return _parse_json(text)

    async def complete_text_stream(self, *, system: str, user: str) -> AsyncIterator[str]:
        # Single-shot then yield; streaming generateContent is optional.
        text = await self._generate(system, user)
        yield text

    async def _generate(self, system: str, user: str) -> str:
        models = [
            self.generation_model,
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ]
        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=25.0) as client:
            for model in dict.fromkeys(models):
                url = f"{self.base_url}/v1beta/models/{model}:generateContent"
                try:
                    res = await client.post(
                        url,
                        params={"key": self.api_key},
                        json={
                            "systemInstruction": {"parts": [{"text": system}]},
                            "contents": [{"role": "user", "parts": [{"text": user}]}],
                            "generationConfig": {
                                "temperature": 0.2,
                                "responseMimeType": "application/json",
                            },
                        },
                    )
                    if res.status_code >= 400:
                        last_error = LLMError(f"Gemini {model} HTTP {res.status_code}: {res.text[:400]}")
                        continue
                    data = res.json()
                    parts = data["candidates"][0]["content"]["parts"]
                    return "".join(p.get("text", "") for p in parts)
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    continue
        raise LLMError(f"Gemini unavailable: {last_error}")


def _parse_json(text: str) -> dict | list:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.replace("<a2ui-json>", "").replace("</a2ui-json>", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        start_obj = cleaned.find("{")
        if start == -1 or (start_obj != -1 and start_obj < start):
            start = start_obj
        end = cleaned.rfind("]")
        end_obj = cleaned.rfind("}")
        if end == -1 or (end_obj > end):
            end = end_obj
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise LLMError("Gemini returned non-JSON output")
