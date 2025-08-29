
#!/usr/bin/env python3
from __future__ import annotations
import os, yaml, json
from pathlib import Path
from quantlab.harness import bakeoff

def call_engine(cand: dict, prompt: str) -> str:
    # Minimal engine dispatch: call orchestrator.generate() with defaults.
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    # In a full implementation, we'd pass engine/quant overrides to the orchestrator/engine layer.
    out = orch.generate(prompt)
    return out.get("text","")

def main():
    cfg = yaml.safe_load(open("runtime/config/quantlab.yaml","r",encoding="utf-8"))
    q = cfg.get("bakeoff", {})
    if not q.get("enabled", False):
        print("QuantLab bakeoff disabled in quantlab.yaml. Enable bakeoff.enabled to run.")
        return
    prompt = q.get("prompt","Hello, world.")
    cands = q.get("candidates", [])
    results = bakeoff(cands, prompt, call_engine)
    outp = Path(q.get("results_path","runtime/quantlab/bench.json"))
    outp.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"prompt": prompt, "results": results}, open(outp,"w",encoding="utf-8"), indent=2)
    print("Wrote bakeoff results to", outp)

if __name__ == "__main__":
    main()
