from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    name: str
    model: str

    async def complete_json(self, *, system: str, user: str, schema: dict | None = None) -> dict | list:
        ...

    async def complete_text_stream(self, *, system: str, user: str):
        ...


class LLMError(RuntimeError):
    pass
