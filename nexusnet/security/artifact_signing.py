from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ed25519 import Ed25519Keypair


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def canonical_signed_payload(record: dict[str, Any]) -> str:
    return json.dumps(record, separators=(",", ":"), sort_keys=True)


def verify_signed_artifact_record(record: dict[str, Any]) -> bool:
    """Cryptographically verify an ed25519 artifact-signature record.

    Returns True only when the ed25519 signature over ``signed_payload`` validates against
    the embedded public key AND the signed claim fields match the record's own fields. This is
    the single source of truth for artifact-signature verification across the project.
    """
    try:
        public_key = bytes.fromhex(str(record["public_key"]))
        signature = bytes.fromhex(str(record["signature"]))
        signed_payload = str(record["signed_payload"])
        claim = json.loads(signed_payload)
    except (KeyError, TypeError, ValueError):
        return False
    if not Ed25519Keypair.verify(public_key, signed_payload.encode("utf-8"), signature):
        return False
    return all(
        str(claim.get(key)) == str(record.get(key))
        for key in ("artifact_path", "artifact_type", "hash", "schema_version")
    )


@dataclass(frozen=True)
class ArtifactSigner:
    keypair: Ed25519Keypair

    @classmethod
    def from_seed(cls, seed: bytes) -> "ArtifactSigner":
        return cls(keypair=Ed25519Keypair.from_seed(seed))

    def sign_file(self, path: Path, *, artifact_type: str) -> dict[str, Any]:
        signed_claim = {
            "artifact_path": str(path),
            "artifact_type": artifact_type,
            "hash": file_sha256(path),
            "schema_version": "artifact_signature_claim.v0.1",
        }
        signed_payload = canonical_signed_payload(signed_claim)
        signature = self.keypair.sign(signed_payload.encode("utf-8")).hex()
        return {
            **signed_claim,
            "signature_state": "signed_ed25519",
            "signature_algorithm": "ed25519",
            "public_key": self.keypair.public_key_hex,
            "signed_payload": signed_payload,
            "signature": signature,
        }
