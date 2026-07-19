from __future__ import annotations

import hashlib
import math
from typing import Any, Iterable


class SemanticPointerMemory:
    """Deterministic vector-symbolic binding for composable NexusNet concepts."""

    def __init__(self, *, dimensions: int = 1024) -> None:
        if dimensions < 256:
            raise ValueError("dimensions must be at least 256")
        self.dimensions = dimensions
        self._bindings: dict[str, dict[str, Any]] = {}

    def pointer(self, label: str) -> list[float]:
        values: list[float] = []
        counter = 0
        while len(values) < self.dimensions:
            digest = hashlib.sha256(f"{label}:{counter}".encode("utf-8")).digest()
            values.extend(1.0 if byte & 1 else -1.0 for byte in digest)
            counter += 1
        scale = math.sqrt(self.dimensions)
        return [value / scale for value in values[: self.dimensions]]

    def bind(self, left: list[float], right: list[float]) -> list[float]:
        self._validate(left, right)
        scale = math.sqrt(self.dimensions)
        return [left[index] * right[index] * scale for index in range(self.dimensions)]

    def unbind(self, bound: list[float], key: list[float]) -> list[float]:
        return self.bind(bound, key)

    def bind_many(self, *vectors: list[float]) -> list[float]:
        if not vectors:
            raise ValueError("at least one vector is required")
        result = list(vectors[0])
        for vector in vectors[1:]:
            result = self.bind(result, vector)
        return result

    def bundle(self, vectors: Iterable[list[float]]) -> list[float]:
        items = list(vectors)
        if not items:
            raise ValueError("at least one vector is required")
        for item in items:
            self._validate(item)
        summed = [sum(item[index] for item in items) for index in range(self.dimensions)]
        norm = math.sqrt(sum(value * value for value in summed)) or 1.0
        return [value / norm for value in summed]

    def similarity(self, left: list[float], right: list[float]) -> float:
        self._validate(left, right)
        left_norm = math.sqrt(sum(value * value for value in left)) or 1.0
        right_norm = math.sqrt(sum(value * value for value in right)) or 1.0
        return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)

    def record_binding(
        self,
        *,
        binding_id: str,
        labels: list[str],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        if not labels:
            raise ValueError("labels are required")
        vector = self.bind_many(*(self.pointer(label) for label in labels))
        vector_digest = hashlib.sha256(
            b"".join(float(value).hex().encode("ascii") for value in vector)
        ).hexdigest()[:16]
        record = {
            "binding_id": binding_id,
            "labels": list(labels),
            "dimensions": self.dimensions,
            "vector_digest": vector_digest,
            "evidence_refs": sorted(set(evidence_refs)),
            "status": "recorded" if evidence_refs else "blocked",
            "raw_vector_persisted": False,
            "production_mutation_allowed": False,
        }
        self._bindings[binding_id] = record
        return dict(record)

    def compare_claims(
        self,
        *,
        claim_a: dict[str, str],
        claim_b: dict[str, str],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        same_slot = (
            claim_a.get("subject") == claim_b.get("subject")
            and claim_a.get("predicate") == claim_b.get("predicate")
        )
        different_value = claim_a.get("object") != claim_b.get("object")
        return {
            "surface_id": "semantic-pointer-contradiction-detector",
            "contradiction": bool(same_slot and different_value),
            "claim_a_digest": self._claim_digest(claim_a),
            "claim_b_digest": self._claim_digest(claim_b),
            "evidence_refs": list(evidence_refs),
            "production_mutation_allowed": False,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "semantic-pointer-memory",
            "runtime_state": "live-bound" if self._bindings else "ready",
            "dimensions": self.dimensions,
            "binding_count": len(self._bindings),
            "bindings": [dict(item) for item in self._bindings.values()],
        }

    def _validate(self, *vectors: list[float]) -> None:
        if any(len(vector) != self.dimensions for vector in vectors):
            raise ValueError(f"vectors must have {self.dimensions} dimensions")
        if any(not math.isfinite(value) for vector in vectors for value in vector):
            raise ValueError("vectors must contain only finite values")

    @staticmethod
    def _claim_digest(claim: dict[str, str]) -> str:
        payload = "\x1f".join(str(claim.get(key, "")) for key in ("subject", "predicate", "object"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
