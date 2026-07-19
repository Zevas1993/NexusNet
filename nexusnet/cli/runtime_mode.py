from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from nexus.config import build_paths
from nexusnet.runtime.accelerator_packs.route_selection import RuntimeModeStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect or set the NexusNet accelerator execution mode")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("mode", choices=("Auto", "CPU", "GPU", "Both"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = build_paths(args.project_root.resolve())
    store = RuntimeModeStore(paths.state_dir / "runtime-acceleration-mode.json")
    payload = store.set_mode(args.mode) if args.command == "set" else store.status()
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
