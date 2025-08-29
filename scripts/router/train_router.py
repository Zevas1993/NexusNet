
#!/usr/bin/env python3
from __future__ import annotations
import argparse, yaml, os
from core.router.training_dataset import build_examples
from core.router.learner import SoftmaxRouter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", default="runtime/config/router.yaml")
    ap.add_argument("--logs", nargs="+", default=["runtime/logs/chat.log"])
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.cfg, "r", encoding="utf-8")) or {}
    lp = cfg.get("learned", {}).get("model_path", "runtime/router/learner.json")
    ex = build_examples(args.logs)
    labels = sorted(set(c for _, c in ex)) or ["generalist"]
    router = SoftmaxRouter(labels)
    for _ in range(args.epochs):
        for p, c in ex:
            router.fit_online(p, c)
    os.makedirs(os.path.dirname(lp), exist_ok=True)
    router.save(lp)
    print(f"Saved router to {lp} with classes={router.classes}")

if __name__ == "__main__":
    main()
