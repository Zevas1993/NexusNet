
from __future__ import annotations
from .policy import get_active_policy

def choose_for_capsule(capsule: str | None) -> dict:
    """Return {'engine': ..., 'quant': ...} from active policy, tolerant of missing files."""
    pol = get_active_policy(capsule)
    engine = (pol.get('engine') if isinstance(pol, dict) else None) or 'transformers'
    quant  = (pol.get('quant')  if isinstance(pol, dict) else None) or 'int8'
    return {'engine': engine, 'quant': quant}
