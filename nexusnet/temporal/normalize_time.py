
from __future__ import annotations
from typing import Optional
def normalize(text: str) -> Optional[str]:
    # Tiny ISO-date normalizer for YYYY, YYYY-MM, YYYY-MM-DD
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            import datetime as _dt
            d = _dt.datetime.strptime(text, fmt)
            return d.date().isoformat()
        except Exception:
            pass
    return None
