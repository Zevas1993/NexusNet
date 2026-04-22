from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower() or "artifact"


class RetrievalRerankArtifactStore:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir

    def write_evidence_bundle(self, *, policy_mode: str, payload: dict[str, Any]) -> str:
        artifact_id = new_id("retrievalev")
        relative = Path("retrieval") / "rerank-evidence" / _slug(policy_mode) / f"{artifact_id}.json"
        destination = self.artifacts_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "artifact_id": artifact_id,
            "artifact_kind": "retrieval-rerank-evidence-bundle",
            "policy_mode": policy_mode,
            "created_at": utcnow().isoformat(),
            "payload": payload,
        }
        destination.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        return str(destination)

    def write_review_payload(self, *, policy_mode: str, payload: dict[str, Any]) -> str:
        artifact_id = new_id("retrievalreview")
        relative = Path("retrieval") / "rerank-review" / _slug(policy_mode) / f"{artifact_id}.json"
        destination = self.artifacts_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "artifact_id": artifact_id,
            "artifact_kind": "retrieval-rerank-review",
            "policy_mode": policy_mode,
            "created_at": utcnow().isoformat(),
            "payload": payload,
        }
        destination.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        return str(destination)

    def write_review_markdown(self, *, policy_mode: str, report_id: str, markdown: str) -> str:
        relative = Path("retrieval") / "rerank-review" / _slug(policy_mode) / f"{_slug(report_id)}.md"
        destination = self.artifacts_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
        return str(destination)
