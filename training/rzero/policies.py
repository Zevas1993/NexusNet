
from typing import List, Dict
from .grpo import GRPOTrainer, GRPOConfig
from ..backends.hf import HFBackend, HFConfig
from .format import extract_between, format_ok

class Policy:
    def __init__(self, model_id: str, role: str, device: str = "cpu"):
        self.role = role
        self.backend = HFBackend(HFConfig(model_id=model_id, device=device))
        self.grpo = GRPOTrainer(self.backend, GRPOConfig())

    @classmethod
    def load(cls, model_id: str, role: str, device: str = "cpu"):
        return cls(model_id, role, device)

    def generate_questions(self, seeds: List[str], n: int) -> List[str]:
        prompts = []
        for i in range(n):
            seed = seeds[i % max(1, len(seeds))] if seeds else "general reasoning"
            prompt = ("You are a Challenger. Generate ONE challenging but solvable problem. "
                      "Wrap it with <question>...</question> and include an empty <answer></answer>."
                      f"\nDomain: {seed}\n<question>")
            prompts.append(prompt)
        out = self.backend.generate(prompts)
        fixed = []
        for t in out:
            if not format_ok(t): t = "<question>" + t + "</question>\n<answer></answer>"
            fixed.append(t)
        return fixed

    def answer(self, question: str, k: int) -> List[str]:
        prompt = f"Solve the problem. Output only inside <answer> tags.\n{question}"
        outs = self.backend.generate([prompt]*k)
        ans = []
        for t in outs:
            a = extract_between(t, "<answer>", "</answer>") or t.strip()
            ans.append(a)
        return ans

    def update_grpo(self, inputs: List[str], rewards: List[float] = None):
        if self.role == "challenger":
            if rewards is None: raise ValueError("Challenger requires rewards")
            return self.grpo.step([""]*len(inputs), inputs, rewards)
        else:
            import json
            prompts, comps, R = [], [], []
            for s in inputs:
                ex = json.loads(s); prompts.append(ex["q"]); comps.append(ex["label"]); R.append(1.0)
            return self.grpo.step(prompts, comps, R)
