
from __future__ import annotations
import os, json
from typing import List, Dict

def summarize(messages: List[Dict[str,str]], max_chars: int = 400) -> str:
    if not messages:
        return ""
    # naive summary: take first user question + last assistant answer (fallback $0 mode)
    first = next((m for m in messages if m.get("role")=="user"), messages[0])
    last = next((m for m in reversed(messages) if m.get("role")=="assistant"), messages[-1])
    s = f"First: {first.get('content','')[:max_chars//2]}; Last: {last.get('content','')[:max_chars//2]}"
    return s[:max_chars]
