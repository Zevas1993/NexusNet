
from __future__ import annotations
from typing import List, Dict, Any
from .entity_resolution import canonicalize
from .backends import has_graphiti

_DB: List[Dict[str,Any]] = []
_NS: Dict[str, List[int]] = {}
_INDEX_SUBJ: Dict[str, List[int]] = {}
_graph = None

def _ensure_graph():
    global _graph
    if _graph is None and has_graphiti():
        try:
            from .graphiti_adapter import GraphitiTKG
            _graph = GraphitiTKG()
        except Exception:
            _graph = None
    return _graph

def upsert_fact(subj:str, pred:str, obj:str, source:str, valid_from:int, valid_to:int, provenance: str = ""):
    g = _ensure_graph()
    cs = canonicalize(subj); co = canonicalize(obj)
    if g:
        return g.upsert_fact(cs, pred, co, source, valid_from, valid_to, provenance)
    rec = {"s":cs,"p":pred,"o":co,"src":source,"vf":valid_from,"vt":valid_to,"prov":provenance}
    _DB.append(rec)
    idx = len(_DB)-1
    _INDEX_SUBJ.setdefault(cs, []).append(idx)

def as_of(ts:int) -> List[Dict[str,Any]]:
    g = _ensure_graph()
    if g: return g.as_of(ts)
    return [r for r in _DB if r["vf"] <= ts <= r["vt"]]

def between(t1:int, t2:int) -> List[Dict[str,Any]]:
    g = _ensure_graph()
    if g: return g.between(t1,t2)
    return [r for r in _DB if not (r["vt"] < t1 or r["vf"] > t2)]

def timeline(entity: str, buckets: int = 10) -> List[Dict[str,Any]]:
    # Fallback only; graphiti path can be added later
    cs = canonicalize(entity)
    idxs = _INDEX_SUBJ.get(cs, [])
    if not idxs: return []
    times = [( _DB[i]["vf"], _DB[i]["vt"] ) for i in idxs]
    lo = min(vf for vf,_ in times); hi = max(vt for _,vt in times)
    if hi <= lo: hi = lo + 1
    step = max(1, (hi-lo)//max(1,buckets))
    out=[]
    for b in range(buckets):
        a = lo + b*step; z = min(hi, a+step-1)
        count = sum(1 for vf,vt in times if not (vt < a or vf > z))
        out.append({"start": a, "end": z, "count": count})
    return out


def upsert_fact_ns(ns: str, subj:str, pred:str, obj:str, source:str, valid_from:int, valid_to:int, provenance: str = ""):
    "Namespace-aware upsert; ns labels facts for per-capsule isolation."
    upsert_fact(subj, pred, obj, source, valid_from, valid_to, provenance)
    idx = len(_DB)-1
    _NS.setdefault(ns or "global", []).append(idx)

def as_of_ns(ns_list, ts:int) -> List[Dict[str,Any]]:
    g=_ensure_graph()
    if g: return g.as_of_ns(ns_list, ts)
    if not ns_list: return as_of(ts)
    idxs=set()
    for ns in ns_list:
        for i in _NS.get(ns, []): idxs.add(i)
    return [r for i,r in enumerate(_DB) if i in idxs and r['vf'] <= ts <= r['vt']]
