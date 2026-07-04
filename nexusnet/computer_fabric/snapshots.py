from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class SnapshotRewindRecorder:
    def record(self, *, session_dir: Path, artifact_paths: list[Path], policy: dict[str, Any]) -> dict[str, Any]:
        artifact_hash_set = [
            {
                "path": str(path),
                "checksum": f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}",
            }
            for path in artifact_paths
            if path.exists()
        ]
        snapshot = {
            "checkpoint_id": f"checkpoint-{session_dir.name}",
            "created_at": utcnow().isoformat(),
            "filesystem_snapshot": "session-artifacts",
            "artifact_hash_set": artifact_hash_set,
            "env_manifest": {
                "provider": policy.get("provider"),
                "network_policy": policy.get("network_policy"),
                "filesystem_policy": policy.get("filesystem_policy"),
            },
            "dependency_lock": {
                "mode": "record-only",
                "lockfile_present": False,
            },
            "rollback_status": "rewind-ready-session-artifacts-only",
        }
        cleanup = {
            "created_at": utcnow().isoformat(),
            "cleanup_scope": "session-artifacts",
            "host_cleanup_required": False,
            "proof_status": "recorded",
        }
        (session_dir / "snapshot-rewind.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
        (session_dir / "cleanup-proof.json").write_text(json.dumps(cleanup, indent=2, sort_keys=True), encoding="utf-8")
        return {"snapshot": snapshot, "cleanup": cleanup}
