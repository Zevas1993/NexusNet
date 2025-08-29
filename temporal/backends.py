
from __future__ import annotations

def has_pgvector() -> bool:
  try:
    import psycopg2  # noqa: F401
    return True
  except Exception:
    return False

def has_graphiti() -> bool:
  try:
    import graphiti  # noqa: F401
    return True
  except Exception:
    return False
