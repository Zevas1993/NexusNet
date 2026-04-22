from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ...schemas import FederatedUpdatePacket


def build_update_packet(*, client_id: str, candidate_kind: str, artifact_path: str, lineage: str, metrics: dict | None = None, provenance: dict | None = None) -> FederatedUpdatePacket:
    signature_material = json.dumps(
        {
            "client_id": client_id,
            "candidate_kind": candidate_kind,
            "artifact_path": artifact_path,
            "lineage": lineage,
            "metrics": metrics or {},
            "provenance": provenance or {},
        },
        sort_keys=True,
    )
    signature = hashlib.sha256(signature_material.encode("utf-8")).hexdigest()
    if not Path(artifact_path).exists():
        provenance = {**(provenance or {}), "missing_artifact": True}
    return FederatedUpdatePacket(
        client_id=client_id,
        candidate_kind=candidate_kind,
        artifact_path=artifact_path,
        metrics=metrics or {},
        provenance=provenance or {},
        lineage=lineage,
        signature=signature,
    )
