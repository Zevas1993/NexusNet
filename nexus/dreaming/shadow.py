from __future__ import annotations

import json

from ..config import NexusPaths
from ..schemas import new_id, utcnow


class DreamShadowPool:
    def __init__(self, paths: NexusPaths):
        self.paths = paths

    def record_episode(self, *, seed: str, scenario: dict, outcome: dict, critique: dict) -> dict:
        dream_id = new_id("dream")
        payload = {
            "dream_id": dream_id,
            "seed": seed,
            "scenario": scenario,
            "outcome": outcome,
            "critique": critique,
            "status": "shadow",
            "created_at": utcnow().isoformat(),
        }
        destination = self.paths.artifacts_dir / "dreams" / f"{dream_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["artifact_path"] = str(destination)
        return payload
