from __future__ import annotations
import random
TEMPLATES = {
    "code": ["Write a Python function to {task}."] ,
    "math": ["Solve: {a}+{b}*{c} and explain."] ,
    "general": ["Summarize the topic: {topic} in 3 bullets."]
}

def generate_items(capsule: str, n: int) -> list[dict]:
    out = []
    for _ in range(n):
        t = random.choice(TEMPLATES.get(capsule, TEMPLATES["general"]))
        sample = t.format(task="reverse a list", a=2,b=3,c=4, topic="distributed systems")
        item = {"prompt": sample, "target": "TODO", "capsule": capsule, "difficulty": random.choice(["easy","medium","hard"]), "provenance": "synthetic-teacher", "license": "synthetic"}
        out.append(item)
    return out
