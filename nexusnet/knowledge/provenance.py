from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_ref(payload: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()}"


def source_digest(source: dict[str, Any]) -> str:
    digest_payload = {
        "source_ref": source.get("source_ref"),
        "title": source.get("title"),
        "text": source.get("text"),
        "source_url": source.get("source_url"),
        "permission_state": source.get("permission_state"),
        "privacy_class": source.get("privacy_class"),
        "license_state": source.get("license_state"),
        "rbac_scope": source.get("rbac_scope") or [],
        "claims": source.get("claims") or [],
    }
    return sha256_ref(digest_payload)
