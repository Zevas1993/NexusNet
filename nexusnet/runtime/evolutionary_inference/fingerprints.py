from __future__ import annotations

import hashlib
import json
from typing import Any

from .schemas import ModelExecutionFingerprint


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


def _build_fingerprint(metadata: dict[str, Any], *, source_kind: str) -> ModelExecutionFingerprint:
    canonical = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    return ModelExecutionFingerprint(
        fingerprint_id=f"model-fingerprint::{digest}",
        source_kind=source_kind,
        **metadata,
    )
