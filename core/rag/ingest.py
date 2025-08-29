
from __future__ import annotations
import re, os, uuid
from typing import List, Dict

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text: return []
    chunks=[]; i=0
    while i < len(text):
        j=min(len(text), i+max_chars)
        # try to end on sentence
        k=text.rfind(". ", i, j)
        if k==-1 or k<=i+200: k=j
        chunks.append(text[i:k].strip())
        i=max(k-overlap, i+1)
    return [c for c in chunks if c]

def batch_upsert(doc_id_prefix: str, text: str, meta: Dict):
    "Upsert chunks to pgvector when available; otherwise no-op."
    try:
        from core.rag.pgvector_adapter import available, ensure_schema, upsert
        if not available():
            return 0
        ensure_schema()
        n=0
        for idx, ch in enumerate(chunk_text(text)):
            cid=f"{doc_id_prefix}-{idx:04d}"
            upsert(cid, ch, meta or {}); n+=1
        return n
    except Exception:
        return 0
