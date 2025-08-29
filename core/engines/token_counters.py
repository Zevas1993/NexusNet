
from __future__ import annotations

_tok_cache = {}

def tok(model_id: str = "gpt2"):
    try:
        from transformers import AutoTokenizer  # type: ignore
        if model_id not in _tok_cache:
            _tok_cache[model_id] = AutoTokenizer.from_pretrained(model_id)
        return _tok_cache[model_id]
    except Exception:
        return None

def count_text(text: str, model_id: str = "gpt2") -> int:
    t = tok(model_id)
    if t is None:
        return max(1, len((text or "").split()))
    try:
        return len(t.encode(text or ""))
    except Exception:
        return max(1, len((text or "").split()))
