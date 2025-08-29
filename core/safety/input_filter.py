
from __future__ import annotations
import re
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
def enforce_length(text: str, max_chars: int) -> str:
    return text[:max_chars]
def redact_pii(text: str, enabled: bool = True) -> str:
    if not enabled: return text
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = PHONE_RE.sub("[redacted-phone]", text)
    return text
