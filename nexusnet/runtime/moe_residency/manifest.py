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
        destination.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return destination


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

    identity_payload = {
        "model_ref": model_ref,
        "layer_id": layer_id,
        "experts": [asdict(record) for record in records],
        "source_provenance_refs": list(source_provenance_refs),
    }
    manifest_id = "expert-manifest:" + hashlib.sha256(
        json.dumps(identity_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
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
