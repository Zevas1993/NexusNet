
from __future__ import annotations
import os, time
from typing import List, Dict
from temporal import tkg

def _semantic_candidates(q: str) -> List[Dict]:
    # very small semantic stub: return TKG docs whose object snippet overlaps any query token
    toks = set([t for t in q.lower().split() if len(t)>2])
    out=[]
    ns=namespaces if isinstance(namespaces, list) else None
    if ns:
        raws = tkg.as_of_ns(ns, as_of_ts or int(time.time()))
    else:
        raws = tkg.as_of(as_of_ts or int(time.time()))
    for r in raws:
        if any(tok in r["o"].lower() for tok in toks):
            out.append({"text": r["o"], "source": r["src"], "validity": f"{r['vf']}..{r['vt']}", "score": 0.5})
    return out[:10]

def get_context(query: str, top_k: int = 5, as_of_ts: int | None = None, namespaces=None) -> List[Dict]:
    # TKG-first: filter candidates via temporal graph, then (optionally) re-rank (omitted in $0 mode)
    cands = _semantic_candidates(query)
    # Simple freshness boost: more recent vf gets a bit more
    now = int(time.time())
    for c in cands:
        try:
            vf = int(str(c["validity"]).split("..")[0])
            recency = max(0.0, min(1.0, (vf - (now-30*86400)) / (30*86400)))  # within ~30 days boosts
        except Exception:
            recency = 0.1
        c["score"] = c.get("score",0.5) + 0.2*recency
    cands.sort(key=lambda x: x.get("score",0), reverse=True)
    return cands[:top_k]


# Optional pgvector hybrid (auto): merge results if available
def get_context_hybrid(query: str, top_k: int = 5, as_of_ts: int | None = None, namespaces=None) -> List[Dict]:
    items = get_context(query, top_k, as_of_ts, namespaces)
    try:
        from .pgvector_adapter import available, search
        if available():
            vec = search(query, top_k)
            # naive merge (unique by source+text)
            seen=set((i.get("source",""),i.get("text","")) for i in items)
            for v in vec:
                key=(v.get("source",""),v.get("text",""))
                if key not in seen:
                    items.append(v); seen.add(key)
    except Exception:
        pass
    items.sort(key=lambda x: x.get("score",0), reverse=True)
    return items[:top_k]
