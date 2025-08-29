
import json
from typing import List, Dict
from .cfg import RZeroConfig
from .policies import Policy
from .rewards import composite_reward
from .labeling import filter_informative_band, write_curated_jsonl
from .format import format_ok

class RZeroEngine:
    def __init__(self, base_model_id: str, cfg: RZeroConfig, device: str = "cpu"):
        self.cfg = cfg
        self.challenger = Policy.load(base_model_id, "challenger", device=device)
        self.solver = Policy.load(base_model_id, "solver", device=device)

    def challenger_phase(self, seeds: List[str]) -> Dict:
        questions = self.challenger.generate_questions(seeds, n=self.cfg.n_candidates)
        evals, items = [], []
        from collections import Counter
        for q in questions:
            fmt = format_ok(q)
            samples = self.solver.answer(q, k=self.cfg.k_samples)
            c = Counter(samples); _, votes = c.most_common(1)[0]
            correct_rate = votes / max(1, len(samples))
            evals.append({"correct_rate": correct_rate, "format_ok": fmt})
            items.append({"question": q, "samples": samples, "format_ok": fmt})
        rewards = composite_reward(evals, questions, self.cfg.repetition_bleu_threshold, self.cfg.repetition_penalty_strength)
        ch = self.challenger.update_grpo(questions, rewards)
        curated = filter_informative_band(items, *self.cfg.informative_band)
        path = write_curated_jsonl(curated, self.cfg.out_dir, self.cfg.experiment)
        return {"curated_path": path, "n_candidates": len(questions), "n_curated": len(curated), "challenger_metrics": ch}

    def solver_phase(self, curated_path: str) -> Dict:
        lines = [json.loads(x) for x in open(curated_path, "r", encoding="utf-8")]
        inputs = [json.dumps({"q": ex["question"], "label": ex["label"]}, ensure_ascii=False) for ex in lines]
        sv = self.solver.update_grpo(inputs, rewards=None)
        return {"trained_on": len(inputs), **sv}

    def iterate(self, seeds: List[str]) -> Dict:
        ch = self.challenger_phase(seeds)
        sv = self.solver_phase(ch["curated_path"])
        return {"challenger": ch, "solver": sv}
