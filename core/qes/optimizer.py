
import itertools, random
from typing import Dict, Any, Iterable

def candidates(search_space:Dict[str,Any])->Iterable[dict]:
    quants = [q.get("name") if isinstance(q,dict) else q for q in search_space.get("quant",[])]
    scheds = search_space.get("sched",["greedy"])
    for q in quants:
        for s in scheds:
            yield {"quant": q, "sched": s}

def choose_next(history:list, space:dict)->dict:
    # trivial epsilon-greedy over explored configs
    eps=0.25
    if not history or random.random()<eps:
        return random.choice(list(candidates(space)))
    # exploit: pick the best seen and mutate sched
    best=max(history, key=lambda h: h.get("score",0))
    return {"quant": best.get("quant"), "sched": random.choice(space.get("sched",["greedy"]))}
