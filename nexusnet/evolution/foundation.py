from __future__ import annotations

from collections.abc import Mapping

from nexusnet.evolution.contracts import FoundationCheck


FOUNDATION_PREREQUISITES = (
    "canon",
    "mother_brain_authority",
    "isolation",
    "neural_bus",
    "hive_blackboard",
    "evidence",
    "checkpoint",
    "replay",
    "governance",
    "rollback",
)
CLAIM_BOUNDARY = "reference-presence-is-not-semantic-proof"


class FoundationVerifier:
    def __init__(self, evidence_refs: Mapping[str, str | None]):
        self._evidence_refs = dict(evidence_refs)

    def verify(self) -> list[FoundationCheck]:
        checks = []
        for prerequisite in FOUNDATION_PREREQUISITES:
            evidence_present = prerequisite in self._evidence_refs
            evidence_ref = self._evidence_refs.get(prerequisite)
            status = (
                "missing"
                if evidence_present and evidence_ref is None
                else "verified"
                if evidence_present
                else "unverified"
            )
            checks.append(
                FoundationCheck(
                    foundation_id=f"foundation:{prerequisite}",
                    status=status,
                    evidence_ref=evidence_ref,
                    claim_boundary=CLAIM_BOUNDARY,
                )
            )
        return checks
