from __future__ import annotations
import random, copy

def mutate(c: dict) -> dict:
    d = copy.deepcopy(c)
    for k,v in list(d.items()):
        if random.random() < 0.3 and isinstance(v,(int,bool,str)):
            if isinstance(v,int):
                d[k] = max(2, v + random.choice([-2,0,2]))
            elif isinstance(v,bool):
                d[k] = not v
            elif isinstance(v,str):
                d[k] = v
    return d

def crossover(a: dict, b: dict) -> dict:
    c = {}
    for k in set(a)|set(b):
        c[k] = random.choice([a.get(k), b.get(k)])
    return c
