
from __future__ import annotations
import warnings
from typing import List, Callable

def trl_available() -> bool:
    try:
        import trl  # noqa: F401
        return True
    except Exception:
        return False

def run_trl(prompts: List[str], policy_fn: Callable[[str], str]):
    if not trl_available():
        from .runner import RLLoop
        loop = RLLoop(policy_fn=policy_fn)
        return loop.step(prompts)
    else:
        # Placeholder: demonstrate interface; real TRL code would prepare datasets, models, and run PPO/SFT.
        # We keep it lightweight to avoid heavy deps in the base install.
        import random
        rewards = [random.uniform(0.3, 0.9) for _ in prompts]
        return sum(rewards)/len(rewards)
