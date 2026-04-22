from __future__ import annotations

import json

from ..config import NexusPaths


class DatasetRefinery:
    def __init__(self, paths: NexusPaths):
        self.paths = paths

    def write_dataset(self, *, name: str, samples: list[dict], metadata: dict | None = None) -> str:
        destination = self.paths.artifacts_dir / "foundry" / "datasets" / f"{name}.jsonl"
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for sample in samples:
                handle.write(json.dumps(sample) + "\n")
        manifest = {
            "name": name,
            "sample_count": len(samples),
            "metadata": metadata or {},
        }
        manifest_path = destination.with_suffix(".manifest.json")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return str(destination)

