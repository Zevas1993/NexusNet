from __future__ import annotations

from .update_packet import build_update_packet


class FlowerFederatedClient:
    def __init__(self, client_id: str):
        self.client_id = client_id

    def package_update(self, *, candidate_kind: str, artifact_path: str, lineage: str, metrics: dict | None = None, provenance: dict | None = None):
        return build_update_packet(
            client_id=self.client_id,
            candidate_kind=candidate_kind,
            artifact_path=artifact_path,
            lineage=lineage,
            metrics=metrics,
            provenance=provenance,
        )
