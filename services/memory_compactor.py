from __future__ import annotations

from typing import Any

from .memory import summarize


def compact_messages(messages: list[dict[str, str]], max_chars: int = 400) -> dict[str, Any]:
    summary = summarize(messages, max_chars=max_chars)
    return {
        "summary": summary,
        "message_count": len(messages),
        "max_chars": max_chars,
    }

