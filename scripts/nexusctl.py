
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, requests

def cmd_temporal_ingest(args):
    payload = {"texts": args.texts, "source": args.source, "url": args.url}
    r = requests.post(f"{args.base}/temporal/ingest", json=payload, timeout=30)
    print(r.status_code, r.text)

def cmd_temporal_asof(args):
    r = requests.get(f"{args.base}/temporal/as_of", params={"query": args.query, "date": args.date, "limit": args.limit}, timeout=30)
    print(r.status_code, r.text)

def cmd_bakeoff(args):
    import subprocess, sys
    cp = subprocess.run([sys.executable, "scripts/quantlab/run_bakeoff.py"], check=False)
    print("Bakeoff finished with", cp.returncode)

def main():
    ap = argparse.ArgumentParser(prog="nexusctl", description="NexusNet Admin CLI")
    ap.add_argument("--base", default="http://127.0.0.1:8000", help="API base URL")
    sub = ap.add_subparsers(dest="sub")

    p1 = sub.add_parser("temporal-ingest")
    p1.add_argument("texts", nargs="+")
    p1.add_argument("--source", default="cli")
    p1.add_argument("--url", default=None)
    p1.set_defaults(func=cmd_temporal_ingest)

    p2 = sub.add_parser("temporal-asof")
    p2.add_argument("query")
    p2.add_argument("date")
    p2.add_argument("--limit", type=int, default=20)
    p2.set_defaults(func=cmd_temporal_asof)

    p3 = sub.add_parser("bakeoff")
    p3.set_defaults(func=cmd_bakeoff)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help(); sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
