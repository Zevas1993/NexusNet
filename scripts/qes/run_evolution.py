#!/usr/bin/env python3
from __future__ import annotations
import argparse, yaml
from quantlab.qes.manager import run_evolution, current_policy

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--capsule", default=None)
    ap.add_argument("--trials", type=int, default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(open("runtime/config/qes.yaml","r",encoding="utf-8"))
    trials = args.trials or int(cfg.get("budget",{}).get("trials",16))
    pol = run_evolution(args.capsule, trials)
    print("Winner:", pol or current_policy())
