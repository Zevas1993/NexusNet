from __future__ import annotations

import argparse
import json
from pathlib import Path

from nexusnet.runtime.accelerator_packs.registry import RuntimePackRegistry


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nexusnet-runtime-packs")
    parser.add_argument("command", choices=("status", "plan"))
    parser.add_argument("--home", type=Path, default=Path.home() / ".nexusnet")
    return parser


def main() -> int:
    args = _parser().parse_args()
    registry = RuntimePackRegistry(args.home / "runtime-packs" / "registry.json")
    snapshot = registry.snapshot()
    payload = {
        "command": args.command,
        "pack_count": len(snapshot.records),
        "active_pack_ids": sorted(snapshot.active_versions),
        "downloads_require_consent": True,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
