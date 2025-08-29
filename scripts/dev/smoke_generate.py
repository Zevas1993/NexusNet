
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from core.orchestrator import Orchestrator

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--capsule", default=None)
    ap.add_argument("--prompt", default="Say hello briefly.")
    args = ap.parse_args()
    o = Orchestrator()
    out = o.generate(args.prompt, capsule=args.capsule)
    print(json.dumps({"out": out, "policy_choice": getattr(o, "_policy_choice", {})}, indent=2))
