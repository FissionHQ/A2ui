from __future__ import annotations

from typing import Any


class JsonPointerError(ValueError):
    pass


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def parse(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise JsonPointerError(f"Invalid JSON Pointer: {pointer}")
    return [_unescape(part) for part in pointer.split("/")[1:]]


def get(doc: Any, pointer: str, default: Any = None) -> Any:
    if pointer in ("", "/"):
        return doc
    try:
        tokens = parse(pointer)
    except JsonPointerError:
        raise
    cur = doc
    for token in tokens:
        if isinstance(cur, list):
            if not token.isdigit():
                return default
            idx = int(token)
            if idx >= len(cur):
                return default
            cur = cur[idx]
        elif isinstance(cur, dict):
            if token not in cur:
                return default
            cur = cur[token]
        else:
            return default
    return cur


def set_value(doc: Any, pointer: str, value: Any) -> Any:
    if pointer in ("", "/"):
        if value is None:
            return {}
        return value
    tokens = parse(pointer)
    if not isinstance(doc, dict) and pointer != "/":
        doc = {} if doc is None else doc
    if not isinstance(doc, dict):
        raise JsonPointerError(f"Invalid JSON Pointer: {pointer}")
    cur: Any = doc
    for i, token in enumerate(tokens[:-1]):
        nxt = tokens[i + 1]
        is_index = nxt.isdigit()
        if isinstance(cur, list):
            idx = int(token)
            while len(cur) <= idx:
                cur.append({} if not is_index else [])
            cur = cur[idx]
        else:
            if token not in cur or cur[token] is None:
                cur[token] = [] if is_index else {}
            cur = cur[token]
    last = tokens[-1]
    if value is None:
        if isinstance(cur, list) and last.isdigit():
            idx = int(last)
            if 0 <= idx < len(cur):
                cur.pop(idx)
        elif isinstance(cur, dict):
            cur.pop(last, None)
        return doc
    if isinstance(cur, list) and last.isdigit():
        idx = int(last)
        while len(cur) <= idx:
            cur.append(None)
        cur[idx] = value
    elif isinstance(cur, dict):
        cur[last] = value
    else:
        raise JsonPointerError(f"Invalid JSON Pointer: {pointer}")
    return doc
