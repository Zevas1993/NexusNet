from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class ArtifactTrustBridge:
    def scan_after_final_bundle(
        self,
        *,
        session_dir: Path,
        session_id: str,
        artifact_index: dict[str, Any],
    ) -> dict[str, Any]:
        final_bundle = {
            "session_id": session_id,
            "created_at": utcnow().isoformat(),
            "source_refs": ["manifest.json", "policy.json", "events.jsonl", "artifact-index.json"],
            "artifact_count": len(artifact_index.get("artifacts", [])),
            "trust_outputs_excluded_from_source_bundle": True,
        }
        (session_dir / "final-artifact-bundle.json").write_text(json.dumps(final_bundle, indent=2, sort_keys=True), encoding="utf-8")
        bridge = {
            "session_id": session_id,
            "created_at": utcnow().isoformat(),
            "scan_order": "final-bundle-before-trust-scan",
            "source_bundle_ref": "final-artifact-bundle.json",
            "trust_output_ref": "artifact-trust-bridge.json",
            "trusted_artifact_count": len([item for item in artifact_index.get("artifacts", []) if item.get("trust_status") == "trusted"]),
            "blocked_artifact_count": len([item for item in artifact_index.get("artifacts", []) if item.get("trust_status") == "blocked"]),
            "promotion_allowed": False,
            "trust_outputs_excluded_from_source_bundle": True,
        }
        (session_dir / "artifact-trust-bridge.json").write_text(json.dumps(bridge, indent=2, sort_keys=True), encoding="utf-8")
        return bridge
