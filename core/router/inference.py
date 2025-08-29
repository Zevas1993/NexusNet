
from __future__ import annotations
import os, yaml
from typing import List, Tuple
from .learner import SoftmaxRouter

class LearnedRouter:
    def __init__(self, cfg_path: str = "runtime/config/router.yaml"):
        self.cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8")) or {}
        lp = self.cfg.get("learned", {}).get("model_path", "runtime/router/learner.json")
        self.top_k = int(self.cfg.get("learned", {}).get("top_k", 3))
        self.early_exit_ebt = float(self.cfg.get("learned", {}).get("early_exit_ebt", 0.65))
        self.model = SoftmaxRouter.load(lp) if os.path.exists(lp) else SoftmaxRouter([])

    def suggest(self, prompt: str) -> List[Tuple[str, float]]:
        if not self.cfg.get("learned", {}).get("enabled", False):
            return []
        return self.model.predict_topk(prompt, k=self.top_k)
