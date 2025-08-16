import re, datetime as dt, math
TS = re.compile(r'(?:as of|on|in)\s+([A-Za-z0-9 ,/\-]+)', re.I)
def parse_scope(q: str, default_lookback_days=365):
    m = TS.search(q)
    if m:
        txt = m.group(1).strip()
        for fmt in ("%Y-%m-%d","%Y/%m/%d","%b %d %Y","%B %d %Y","%Y-%m","%Y"):
            try:
                d = dt.datetime.strptime(txt, fmt).date()
                return {"mode":"point","from":d,"to":d}
            except Exception: pass
    ql=q.lower()
    if any(w in ql for w in ["current","now","latest","today"]):
        to=dt.date.today(); fr=to - dt.timedelta(days=default_lookback_days)
        return {"mode":"latest","from":fr,"to":to}
    return {"mode":"open","from":None,"to":None}
def in_scope(meta, scope):
    if scope is None or scope["mode"]=="open": return True
    vf = meta.get("valid_from") or meta.get("observed_at")
    if not vf: return True
    try:
        d = dt.date.fromisoformat(str(vf)[:10])
        return (scope["from"] is None or d >= scope["from"]) and (scope["to"] is None or d <= scope["to"])
    except Exception: return True
def recency_boost(meta, scope, lam=0.15):
    if scope is None or scope["mode"]!="latest": return 1.0
    oa = meta.get("observed_at") or meta.get("valid_from")
    if not oa: return 1.0
    try:
        age = (dt.date.today() - dt.date.fromisoformat(str(oa)[:10])).days
        return math.exp(-lam * max(age,0))
    except Exception: return 1.0