from __future__ import annotations

import hashlib
import json
from typing import Any

from .schemas import ModelExecutionFingerprint, RuntimeModelMetadata


class UnsupportedModelFeatureError(ValueError):
    def __init__(self, features: list[str]) -> None:
        self.features = sorted({str(feature) for feature in features if str(feature)})
        super().__init__(f"unsupported model execution features: {', '.join(self.features)}")


_SYNTHETIC_FIXTURE = {
    "architecture_family": "synthetic-transformer",
    "parameter_count": 125_000_000,
    "tensor_bytes": 250_000_000,
    "quantization": "fp16",
    "context_length": 2048,
    "layer_count": 12,
    "expert_count": 0,
    "experts_per_token": 0,
    "modalities": ["text"],
}


def synthetic_model_fingerprint() -> ModelExecutionFingerprint:
    return _build_fingerprint(_SYNTHETIC_FIXTURE, source_kind="trusted-synthetic")


def fingerprint_from_metadata(metadata: dict[str, Any]) -> ModelExecutionFingerprint:
    normalized = {
        "architecture_family": str(metadata["architecture_family"]).strip().lower(),
        "parameter_count": int(metadata["parameter_count"]),
        "tensor_bytes": int(metadata["tensor_bytes"]),
        "quantization": str(metadata["quantization"]).strip().lower(),
        "context_length": int(metadata["context_length"]),
        "layer_count": int(metadata["layer_count"]),
        "expert_count": int(metadata.get("expert_count", 0)),
        "experts_per_token": int(metadata.get("experts_per_token", 0)),
        "modalities": sorted({str(item).strip().lower() for item in metadata.get("modalities", ["text"]) if str(item).strip()}),
    }
    return _build_fingerprint(normalized, source_kind="metadata")


def fingerprint_from_runtime_metadata(
    metadata: RuntimeModelMetadata | dict[str, Any],
) -> ModelExecutionFingerprint:
    normalized = metadata if isinstance(metadata, RuntimeModelMetadata) else RuntimeModelMetadata.model_validate(metadata)
    if normalized.unknown_or_unsupported_features:
        raise UnsupportedModelFeatureError(normalized.unknown_or_unsupported_features)
    canonical = normalized.model_dump(mode="json", exclude={"provenance_ref"})
    canonical["architecture_family"] = normalized.architecture_family.strip().lower()
    canonical["quantization"] = normalized.quantization.strip().lower()
    canonical["modalities"] = sorted({item.strip().lower() for item in normalized.modalities})
    canonical["operator_families"] = sorted({item.strip().lower() for item in normalized.operator_families})
    canonical["custom_operator_requirements"] = sorted(
        {item.strip().lower() for item in normalized.custom_operator_requirements}
    )
    canonical["rights_and_artifact_refs"] = sorted(
        {
            f"artifact-ref::{hashlib.sha256(item.encode('utf-8')).hexdigest()[:24]}"
            for item in normalized.rights_and_artifact_refs
            if item
        }
    )
    graph_digest = _digest(
        {
            "operators": canonical["operator_families"],
            "tensors": canonical["tensor_groups"],
            "state": canonical["state_and_kv_contract"],
            "sparsity": canonical["sparsity_and_router_contract"],
            "dynamic_shapes": canonical["dynamic_shape_contract"],
        }
    )
    return ModelExecutionFingerprint(
        fingerprint_id=f"model-fingerprint::{_digest(canonical)[:24]}",
        graph_digest=graph_digest,
        source_kind="metadata",
        **canonical,
    )


def _build_fingerprint(metadata: dict[str, Any], *, source_kind: str) -> ModelExecutionFingerprint:
    canonical = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    return ModelExecutionFingerprint(
        fingerprint_id=f"model-fingerprint::{digest}",
        source_kind=source_kind,
        **metadata,
    )


def _digest(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
