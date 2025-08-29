
import os, json
from typing import List
from .cfg import RZeroConfig
from .engine import RZeroEngine
def run_iterations(model_id: str, seeds: List[str], iterations: int = 3, experiment: str = "default", device: str = "cpu"):
    cfg = RZeroConfig(experiment=experiment); eng = RZeroEngine(model_id, cfg, device=device)
    os.makedirs(cfg.out_dir, exist_ok=True)
    metrics_path = os.path.join(cfg.out_dir, f"metrics-{experiment}.jsonl")
    out = []
    for i in range(iterations):
        rep = eng.iterate(seeds); rep["iter"] = i+1
        with open(metrics_path, "a", encoding="utf-8") as f: f.write(json.dumps(rep)+"\n")
        out.append(rep)
    return {"experiment": experiment, "iterations": iterations, "metrics_log": metrics_path, "reports": out}
