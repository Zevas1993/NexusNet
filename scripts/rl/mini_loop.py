
#!/usr/bin/env python3
from __future__ import annotations
import random, json, os, time
from core.rl.verifiers import math_verify

def sample():
    a,b = random.randint(1,20), random.randint(1,20)
    return f"What is {a}+{b}?", a+b

def policy(prompt: str) -> str:
    # $0 placeholder policy: heuristic "compute" answer
    import re
    m = re.search(r'(\d+)\s*\+\s*(\d+)', prompt)
    if not m: return "I think it's 0."
    a,b = int(m.group(1)), int(m.group(2))
    return f"Answer: {a+b}"

def main(iters=50):
    rewards=[]
    for i in range(iters):
        q, truth = sample()
        ans = policy(q)
        r = math_verify(q, ans)
        rewards.append(r)
    os.makedirs("artifacts/rl", exist_ok=True)
    with open("artifacts/rl/mini_rewards.json","w") as f:
        json.dump({"avg_reward": sum(rewards)/len(rewards), "n": len(rewards)}, f, indent=2)
    print("avg_reward", sum(rewards)/len(rewards))
if __name__ == "__main__":
    main()
