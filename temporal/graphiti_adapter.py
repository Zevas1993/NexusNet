
from __future__ import annotations

class GraphitiTKG:
    """
    Runtime adapter for Graphiti if available.
    Uses a simple in-memory emulation when graphiti import fails (keeps $0 path consistent).
    """
    def __init__(self):
        try:
            import graphiti  # type: ignore
            self._g = graphiti.Graph()
            self._emu = None
        except Exception:
            self._g = None
            self._emu = []  # (s,p,o, data)
    def upsert_fact(self, s, p, o, source, vf, vt, provenance=''):
        if self._g:
            self._g.add_edge(s, p, o, {"src":source,"vf":vf,"vt":vt,"prov":provenance})
        else:
            self._emu.append((s,p,o,{"src":source,"vf":vf,"vt":vt,"prov":provenance}))
    def as_of(self, ts: int):
        if self._g:
            out=[]
            for (s,p,o,data) in self._g.edges():
                if data.get("vf",0) <= ts <= data.get("vt", 2**31-1):
                    out.append({"s":s,"p":p,"o":o,"src":data.get("src",""),"vf":data.get("vf",0),"vt":data.get("vt",0),"prov":data.get("prov","")})
            return out
        out=[]
        for (s,p,o,data) in self._emu:
            if data.get("vf",0) <= ts <= data.get("vt", 2**31-1):
                out.append({"s":s,"p":p,"o":o,"src":data.get("src",""),"vf":data.get("vf",0),"vt":data.get("vt",0),"prov":data.get("prov","")})
        return out
    def between(self, t1:int, t2:int):
        if self._g:
            out=[]
            for (s,p,o,data) in self._g.edges():
                vf,vt = data.get("vf",0), data.get("vt",2**31-1)
                if not (vt < t1 or vf > t2):
                    out.append({"s":s,"p":p,"o":o,"src":data.get("src",""),"vf":vf,"vt":vt,"prov":data.get("prov","")})
            return out
        out=[]
        for (s,p,o,data) in self._emu:
            vf,vt = data.get("vf",0), data.get("vt",2**31-1)
            if not (vt < t1 or vf > t2):
                out.append({"s":s,"p":p,"o":o,"src":data.get("src",""),"vf":vf,"vt":vt,"prov":data.get("prov","")})
        return out


def timeline(self, entity: str, buckets: int = 10):
    # naive bucketed counts over vf,vt
    def iter_edges():
        if self._g:
            for (s,p,o,data) in self._g.edges():
                yield s,p,o,data
        else:
            for (s,p,o,data) in self._emu:
                yield s,p,o,data
    # collect spans for entity as subject
    spans=[]
    e=entity.strip().lower()
    for (s,p,o,data) in iter_edges():
        if (s or '').lower()==e:
            spans.append((int(data.get('vf',0)), int(data.get('vt',2**31-1))))
    if not spans: return []
    lo=min(v for v,_ in spans); hi=max(v for _,v in spans)
    if hi<=lo: hi=lo+1
    step=max(1,(hi-lo)//max(1,buckets))
    out=[]
    for b in range(buckets):
        a=lo + b*step; z=min(hi, a+step-1)
        cnt=sum(1 for vf,vt in spans if not (vt< a or vf> z))
        out.append({"start":a,"end":z,"count":cnt})
    return out


def build_indexes(self):
    try:
        if self._g and hasattr(self._g, "build_indexes"):
            self._g.build_indexes()
    except Exception:
        pass
