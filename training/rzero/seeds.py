
def harvest_from_memory(memory, planes, limit=20):
    out=[]
    for p in planes:
        try:
            for it in memory.scan(p, limit=max(1,limit//max(1,len(planes)))):
                out.append(it.get('hint') or it.get('text') or p)
        except Exception: pass
    # dedupe preserve order
    seen=set(); res=[]
    for s in out:
        if s in seen: continue
        seen.add(s); res.append(s)
    return res[:limit]
