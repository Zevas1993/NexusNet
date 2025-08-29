
from __future__ import annotations
import os, yaml, random, json
from datetime import datetime
from pathlib import Path

def synthesize_prompts(n: int = 20) -> list[str]:
    seeds = [
        "Explain this repo's architecture in 5 bullets.",
        "Summarize latest ingest about {topic}.",
        "Propose 3 tests for module X.",
        "Find contradictions in these two statements: A vs B.",
        "Draft a privacy policy clause for data deletion."
    ]
    return [random.choice(seeds) for _ in range(n)]

def main(cfg_path: str = "runtime/config/rzero.yaml"):
    cfg = {}
    if os.path.exists(cfg_path):
        with open(cfg_path,"r",encoding="utf-8") as f: cfg = yaml.safe_load(f) or {}
    outdir = Path(cfg.get("out_dir","runtime/rzero"))
    outdir.mkdir(parents=True, exist_ok=True)
    prompts = synthesize_prompts(cfg.get("batch_size", 20))
    # save a dataset shard
    shard = {"created": datetime.utcnow().isoformat()+"Z", "prompts": prompts}
    with open(outdir / "dataset.json", "w", encoding="utf-8") as f:
        json.dump(shard, f, indent=2)
    print("R-Zero generated shard at", outdir / "dataset.json")

if __name__ == "__main__":
    main()
