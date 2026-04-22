from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from nexusnet.memory.memory_node import MemoryNode


def main() -> None:
    parser = argparse.ArgumentParser(description="Add new MemoryNode planes to root config/planes.yaml without freezing plane count.")
    parser.add_argument("--project-root", default=".", help="Workspace root containing config/ and runtime/config/")
    parser.add_argument("--plane-name", action="append", required=True, help="Plane name to add.")
    parser.add_argument("--conceptual-plane", default="conceptual", help="Conceptual parent for added planes.")
    parser.add_argument("--projection-role", action="append", default=["semantic"], help="Projection role to apply.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    memory_node = MemoryNode(project_root=project_root)
    payload = memory_node.summary()["raw_config"]
    existing = {item["plane_name"] for item in payload.get("planes", [])}
    for plane_name in args.plane_name:
        if plane_name in existing:
            continue
        payload.setdefault("planes", []).append(
            {
                "plane_name": plane_name,
                "conceptual_plane": args.conceptual_plane,
                "description": f"Added plane '{plane_name}' through the MemoryNode migration helper.",
                "aliases": [],
                "projection_roles": list(dict.fromkeys(args.projection_role)),
                "token_budget_ratio": 0.05,
                "status_label": "UNRESOLVED CONFLICT",
            }
        )
    memory_node.root_config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    print(memory_node.root_config_path)


if __name__ == "__main__":
    main()
