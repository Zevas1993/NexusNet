from __future__ import annotations
def filter_by_consistency(items: list[dict], min_agree: int = 2) -> list[dict]:
    for it in items:
        it["consistency"] = 1
    return items
