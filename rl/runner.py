
from __future__ import annotations
from typing import List, Callable
from .rewards import simple_reward

class RLLoop:
    def __init__(self, policy_fn: Callable[[str], str], update_fn: Callable[[List[tuple]], None] | None = None):
        self.policy_fn = policy_fn
        self.update_fn = update_fn

    def step(self, prompts: List[str]) -> float:
        traj = []
        for p in prompts:
            a = self.policy_fn(p)
            r = simple_reward(p, a)
            traj.append((p,a,r))
        if self.update_fn:
            self.update_fn(traj)
        return sum(r for _,_,r in traj)/max(1,len(traj))
