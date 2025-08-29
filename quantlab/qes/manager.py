
from __future__ import annotations
import os, json, yaml
from .fitness import eval_candidate, score
from .evolution import mutate, crossover
from .sandbox import run_trial

SPACE = yaml.safe_load(open("quantlab/qes/search_space.yaml","r",encoding="utf-8"))
POLICY_PATH = "runtime/quantlab/policy.json"
POLICY_DIR  = "runtime/quantlab/policies"

def sample_candidate() -> dict:
    import random
    return {k: random.choice(v) for k,v in SPACE.items()}

def run_evolution(capsule: str | None = None, budget_trials: int = 16) -> dict:
    sample_prompts = ["hello world","explain quicksort","proof sketch of pythagoras"]
    os.makedirs(os.path.dirname(POLICY_PATH), exist_ok=True)
    os.makedirs(POLICY_DIR, exist_ok=True)
    pop = [sample_candidate() for _ in range(6)]
    best = None
    for t in range(budget_trials):
        cand = pop[t % len(pop)]
        fit = eval_candidate(cand, sample_prompts)
        sc = score(fit)
        run_trial(cand, fit)
        if fit["quality"] >= 0.80 and (best is None or sc > best["score"]):
            best = {"candidate": cand, "fitness": fit, "score": sc}
        a = sample_candidate(); b = sample_candidate()
        pop.append(mutate(cand))
        pop.append(crossover(a,b))
    if best:
        pol = {"engine": best["candidate"].get("engine_hint","transformers"),
               "quant": f"int{best['candidate'].get('bits','8')}",
               "qes": {"candidate": best["candidate"], "fitness": best["fitness"]}}
        with open(POLICY_PATH,"w",encoding="utf-8") as f: f.write(json.dumps(pol))
        if capsule:
            with open(os.path.join(POLICY_DIR, f"{capsule}.json"),"w",encoding="utf-8") as f:
                f.write(json.dumps(pol))
        return pol
    return {}

def current_policy(capsule: str | None = None) -> dict:
    if capsule:
        p = os.path.join(POLICY_DIR, f"{capsule}.json")
        if os.path.exists(p):
            try: return json.load(open(p,"r",encoding="utf-8"))
            except Exception: pass
    if os.path.exists(POLICY_PATH):
        try: return json.load(open(POLICY_PATH,"r",encoding="utf-8"))
        except Exception: pass
    return {}
