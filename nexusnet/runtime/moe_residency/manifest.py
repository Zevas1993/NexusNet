from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import torch.nn as nn


_SAFE_LAYER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_KEYS = {
    "manifest_id", "model_ref", "layer_id", "format", "root_dir",
    "experts", "source_provenance_refs",
}
_RECORD_KEYS = {"expert_id", "layer_id", "path", "size_bytes", "sha256", "tensor_names"}
_MAX_MANIFEST_BYTES = 4 * 1024 * 1024


class ExpertIntegrityError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExpertTensorRecord:
    expert_id: int
    layer_id: str
    path: str
    size_bytes: int
    sha256: str
    tensor_names: tuple[str, ...]


@dataclass(frozen=True)
class ExpertTensorManifest:
    manifest_id: str
    model_ref: str
    layer_id: str
    format: str
    root_dir: str
    experts: tuple[ExpertTensorRecord, ...]
    source_provenance_refs: tuple[str, ...]

    def record(self, expert_id: int) -> ExpertTensorRecord:
        for record in self.experts:
            if record.expert_id == expert_id:
                return record
        raise KeyError(f"expert {expert_id} is not present in manifest")

    def write_json(self, path: str | Path) -> Path:
        destination = Path(path)
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(temporary, destination)
        return destination

    @classmethod
    def read_json(
        cls,
        path: str | Path,
        *,
        expected_model_ref: str | None = None,
        expected_layer_id: str | None = None,
        expected_expert_count: int | None = None,
    ) -> "ExpertTensorManifest":
        source = Path(path)
        if source.is_symlink():
            raise ExpertIntegrityError("manifest path or size is unsafe")
        try:
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(source, flags)
            try:
                stat = os.fstat(descriptor)
                if stat.st_size > _MAX_MANIFEST_BYTES:
                    raise ExpertIntegrityError("manifest path or size is unsafe")
                with os.fdopen(descriptor, "rb", closefd=False) as handle:
                    raw = handle.read(_MAX_MANIFEST_BYTES + 1)
            finally:
                os.close(descriptor)
            if len(raw) > _MAX_MANIFEST_BYTES:
                raise ExpertIntegrityError("manifest path or size is unsafe")
            payload = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ExpertIntegrityError("manifest is not valid bounded UTF-8 JSON") from exc
        if not isinstance(payload, dict) or set(payload) != _MANIFEST_KEYS:
            raise ExpertIntegrityError("manifest schema does not match the supported contract")
        if payload["format"] != "safetensors":
            raise ExpertIntegrityError("manifest format must be safetensors")
        model_ref = payload["model_ref"]
        layer_id = payload["layer_id"]
        if not isinstance(model_ref, str) or not model_ref:
            raise ExpertIntegrityError("manifest model_ref is invalid")
        if not isinstance(layer_id, str) or not _SAFE_LAYER_ID.fullmatch(layer_id) or ".." in layer_id:
            raise ExpertIntegrityError("manifest layer_id is invalid")
        if expected_model_ref is not None and model_ref != expected_model_ref:
            raise ExpertIntegrityError("manifest model_ref does not match expected model")
        if expected_layer_id is not None and layer_id != expected_layer_id:
            raise ExpertIntegrityError("manifest layer_id does not match expected layer")
        raw_records = payload["experts"]
        raw_refs = payload["source_provenance_refs"]
        if not isinstance(raw_records, list) or not raw_records:
            raise ExpertIntegrityError("manifest requires a non-empty expert list")
        if not isinstance(raw_refs, list) or not all(isinstance(ref, str) for ref in raw_refs):
            raise ExpertIntegrityError("manifest provenance refs are invalid")
        records: list[ExpertTensorRecord] = []
        for expected_id, raw in enumerate(raw_records):
            if not isinstance(raw, dict) or set(raw) != _RECORD_KEYS:
                raise ExpertIntegrityError("expert record schema is invalid")
            relative = Path(raw["path"]) if isinstance(raw["path"], str) else Path("..")
            tensor_names = raw["tensor_names"]
            if (
                raw["expert_id"] != expected_id
                or raw["layer_id"] != layer_id
                or relative.is_absolute()
                or ".." in relative.parts
                or relative.parent != Path(".")
                or not isinstance(raw["size_bytes"], int)
                or isinstance(raw["size_bytes"], bool)
                or raw["size_bytes"] <= 0
                or not isinstance(raw["sha256"], str)
                or not _SHA256.fullmatch(raw["sha256"])
                or not isinstance(tensor_names, list)
                or not tensor_names
                or not all(isinstance(name, str) and name for name in tensor_names)
            ):
                raise ExpertIntegrityError("expert record content is invalid")
            records.append(
                ExpertTensorRecord(
                    expert_id=expected_id,
                    layer_id=layer_id,
                    path=str(relative),
                    size_bytes=raw["size_bytes"],
                    sha256=raw["sha256"],
                    tensor_names=tuple(tensor_names),
                )
            )
        if expected_expert_count is not None and len(records) != expected_expert_count:
            raise ExpertIntegrityError("manifest expert count does not match expected topology")
        canonical_id = _canonical_manifest_id(model_ref, layer_id, records, tuple(raw_refs))
        if payload["manifest_id"] != canonical_id:
            raise ExpertIntegrityError("manifest_id does not match canonical manifest content")
        return cls(
            manifest_id=canonical_id,
            model_ref=model_ref,
            layer_id=layer_id,
            format="safetensors",
            root_dir=str(source.parent.resolve()),
            experts=tuple(records),
            source_provenance_refs=tuple(raw_refs),
        )


def _canonical_manifest_id(
    model_ref: str,
    layer_id: str,
    records: Iterable[ExpertTensorRecord],
    source_provenance_refs: tuple[str, ...],
) -> str:
    identity_payload = {
        "model_ref": model_ref,
        "layer_id": layer_id,
        "experts": [asdict(record) for record in records],
        "source_provenance_refs": list(source_provenance_refs),
    }
    return "expert-manifest:" + hashlib.sha256(
        json.dumps(identity_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def package_swiglu_experts(
    experts: Iterable[nn.Module],
    output_dir: str | Path,
    *,
    model_ref: str,
    layer_id: str,
    source_provenance_refs: tuple[str, ...] = (),
) -> ExpertTensorManifest:
    """Write one immutable safetensors shard per native SwiGLU expert."""
    try:
        from safetensors.torch import save_file
    except ImportError as exc:
        raise RuntimeError("safetensors is required for tiered expert packaging") from exc
    if not _SAFE_LAYER_ID.fullmatch(layer_id) or ".." in layer_id:
        raise ValueError("layer_id must be a safe identifier without path traversal")
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    records: list[ExpertTensorRecord] = []
    required = {
        "w_gate.weight",
        "w_gate.bias",
        "w_value.weight",
        "w_value.bias",
        "w_out.weight",
        "w_out.bias",
    }
    for expert_id, expert in enumerate(experts):
        state = {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in expert.state_dict().items()
        }
        if set(state) != required:
            raise TypeError("tiered execution currently requires native SwiGLUExpert tensors")
        relative_path = f"layer-{layer_id}-expert-{expert_id}.safetensors"
        shard_path = root / relative_path
        if shard_path.parent.resolve() != root:
            raise ValueError("expert shard path must remain inside output_dir")
        temporary_path = root / f".{relative_path}.tmp"
        save_file(state, str(temporary_path))
        os.replace(temporary_path, shard_path)
        shard_bytes = shard_path.read_bytes()
        records.append(
            ExpertTensorRecord(
                expert_id=expert_id,
                layer_id=layer_id,
                path=relative_path,
                size_bytes=len(shard_bytes),
                sha256=hashlib.sha256(shard_bytes).hexdigest(),
                tensor_names=tuple(sorted(state)),
            )
        )

    manifest_id = _canonical_manifest_id(model_ref, layer_id, records, source_provenance_refs)
    manifest = ExpertTensorManifest(
        manifest_id=manifest_id,
        model_ref=model_ref,
        layer_id=layer_id,
        format="safetensors",
        root_dir=str(root),
        experts=tuple(records),
        source_provenance_refs=source_provenance_refs,
    )
    manifest.write_json(root / "manifest.json")
    return manifest
