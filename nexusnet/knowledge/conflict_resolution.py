from __future__ import annotations

from collections import defaultdict
from typing import Any


def resolve_claim_conflicts(claims: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_field: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        field = str(claim.get("field") or "").strip()
        if field:
            by_field[field].append(claim)

    accepted: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for field in sorted(by_field):
        field_claims = by_field[field]
        values = sorted({str(claim.get("value") or "") for claim in field_claims})
        if len(values) <= 1:
            accepted.append(
                {
                    "field": field,
                    "value": values[0] if values else "",
                    "source_refs": sorted({str(claim.get("source_ref")) for claim in field_claims if claim.get("source_ref")}),
                }
            )
            continue
        conflicts.append(
            {
                "field": field,
                "candidate_values": [
                    {
                        "value": value,
                        "source_refs": sorted(
                            {
                                str(claim.get("source_ref"))
                                for claim in field_claims
                                if str(claim.get("value") or "") == value and claim.get("source_ref")
                            }
                        ),
                    }
                    for value in values
                ],
                "resolution": "conflict_requires_review",
                "resolution_policy": "deterministic-no-silent-overwrite",
            }
        )
    return accepted, conflicts
