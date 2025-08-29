
from __future__ import annotations
import yaml

from core.orchestrator import Orchestrator
from rl.trl_runner import run_trl

def main(cfg_path: str = "runtime/config/rl.yaml"):
    cfg = {}
    try:
        cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8")) or {}
    except Exception:
        pass
    prompts = cfg.get("prompts", ["Explain NexusNet briefly.", "List 2 safety policies."])
    orch = Orchestrator()
    def policy_fn(p: str) -> str:
        out = orch.generate(p)
        return out.get("text","")
    avg = run_trl(prompts, policy_fn)
    print("Average reward:", avg)

if __name__ == "__main__":
    main()
