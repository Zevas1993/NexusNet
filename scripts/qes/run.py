
#!/usr/bin/env python3
import os, json, time
from core.qes.policy import load_config
from core.qes.optimizer import choose_next
from core.qes.sandbox import evaluate
from statistics import fmean

def score(meas, objectives):
    w={o.name:o.weight for o in objectives}
    # normalize simple: higher is better for tps & quality; lower is better for latency & memory
    inv = 1.0 / max(meas.get("latency_p95_ms",1),1)
    inv_mem = 1.0 / max(meas.get("memory_footprint_mb",1),1)
    return (w.get("throughput_tps",0)*meas.get("throughput_tps",0) +
            w.get("quality_proxy",0)*meas.get("quality_proxy",0) +
            w.get("latency_p95_ms",0)*inv +
            w.get("memory_footprint_mb",0)*inv_mem)

def main():
    cfg=load_config()
    hist=[]; trials=int(cfg.budget.get("max_trials_per_interval",4))
    for i in range(trials):
        cand=choose_next(hist, cfg.search_space)
        meas=evaluate(cand)
        s=score(meas, cfg.objectives)
        hist.append({**cand, **meas, "score": round(s,4)})
        print(f"trial {i+1}/{trials}: {cand} -> {meas} -> score={s:.4f}")
    best=max(hist, key=lambda h:h["score"])
    os.makedirs(cfg.persist_dir, exist_ok=True)
    out=os.path.join(cfg.persist_dir, f"best_{int(time.time())}.json")
    with open(out,"w",encoding="utf-8") as f: json.dump({"best":best, "history":hist}, f, indent=2)
    print("BEST", json.dumps(best))
    print("WROTE", out)

if __name__=="__main__": main()
