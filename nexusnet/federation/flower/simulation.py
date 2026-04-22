from __future__ import annotations

from .client import FlowerFederatedClient
from .coordinator import FlowerCoordinator


class FlowerSimulationHarness:
    def __init__(self, coordinator: FlowerCoordinator):
        self.coordinator = coordinator

    def run(self, *, candidate_kind: str, artifact_path: str, lineage: str, metrics: dict | None = None, provenance: dict | None = None) -> dict:
        client = FlowerFederatedClient(client_id="local-sim")
        packet = client.package_update(
            candidate_kind=candidate_kind,
            artifact_path=artifact_path,
            lineage=lineage,
            metrics=metrics,
            provenance=provenance,
        )
        submission = self.coordinator.submit(packet)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "transport": "flower-simulated",
            "submission": submission,
        }
