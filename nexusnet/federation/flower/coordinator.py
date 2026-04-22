from __future__ import annotations

import json
from pathlib import Path

from nexus.storage import NexusStore

from ...promotions import PromotionService
from ...schemas import GlobalImprovementCandidate
from ..base import FederatedCoordinator


class FlowerCoordinator(FederatedCoordinator):
    def __init__(self, *, store: NexusStore | None = None, artifacts_dir: Path | None = None, promotions: PromotionService | None = None):
        self._packets = []
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.promotions = promotions

    def submit(self, packet):
        self._packets.append(packet)
        packet_artifact = None
        if self.artifacts_dir is not None:
            destination = self.artifacts_dir / "federation" / "packets" / f"{packet.packet_id}.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(packet.model_dump(mode="json"), indent=2), encoding="utf-8")
            packet_artifact = str(destination)
        candidate = GlobalImprovementCandidate(
            packet_id=packet.packet_id,
            subject=f"federated-update::{packet.candidate_kind}",
            provenance={
                "client_id": packet.client_id,
                "artifact_path": packet.artifact_path,
                "lineage": packet.lineage,
                "signature": packet.signature,
                "packet_artifact": packet_artifact,
            },
        )
        promotion_candidate = None
        if self.promotions is not None:
            promotion_candidate = self.promotions.create_candidate(
                candidate_kind="federated-update",
                subject_id=candidate.subject,
                baseline_reference="federated-shadow-baseline",
                challenger_reference=packet.artifact_path,
                lineage=packet.lineage,
                rollback_reference=f"federated::{packet.packet_id}",
                traceability={
                    "packet": packet.model_dump(mode="json"),
                    "packet_artifact": packet_artifact,
                    "global_candidate": candidate.model_dump(mode="json"),
                },
            )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "packet": packet.model_dump(mode="json"),
            "candidate": candidate.model_dump(mode="json"),
            "promotion_candidate": promotion_candidate.model_dump(mode="json") if promotion_candidate else None,
        }

    def status(self) -> dict:
        promotion_count = len(self.promotions.list_candidates(candidate_kind="federated-update")) if self.promotions is not None else 0
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "packet_count": len(self._packets),
            "candidate_global_improvements": promotion_count or len(self._packets),
            "notes": ["Local discoveries remain candidate global improvements until review, external evaluation, and rollout approval complete."],
        }
