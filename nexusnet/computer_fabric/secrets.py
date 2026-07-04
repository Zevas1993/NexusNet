from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nexus.schemas import utcnow


class SecretsBroker:
    def bind(self, *, session_dir: Path, session_id: str, secret_ref: str | None, provider_id: str) -> list[dict[str, Any]]:
        if not secret_ref:
            return []
        binding = {
            "binding_id": f"secretbinding_{uuid4().hex[:12]}",
            "session_id": session_id,
            "secret_ref": secret_ref,
            "secret_value_persisted": False,
            "mount_mode": "reference-only",
            "allowed_provider": provider_id,
            "redaction_policy": "never-log-secret-values",
            "ttl": "session",
            "audit_ref": f"audit://computer-fabric/{session_id}/secret-binding",
            "created_at": utcnow().isoformat(),
        }
        (session_dir / "secret-bindings.json").write_text(json.dumps({"bindings": [binding]}, indent=2, sort_keys=True), encoding="utf-8")
        return [binding]
