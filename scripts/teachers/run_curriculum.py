#!/usr/bin/env python3
from __future__ import annotations
import argparse
from teachers.orchestrator import run_curriculum

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--capsule", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--n", type=int, default=50)
    args = ap.parse_args()
    out = args.out or f"data/lake/curricula/{args.capsule}.jsonl"
    n = run_curriculum(args.capsule, out, args.n)
    print("Wrote:", out, "items:", n)
