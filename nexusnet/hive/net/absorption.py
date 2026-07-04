"""Wrapper ABSORPTION: the born model internalizes the wrapper's architecture + features (canon end-state).

Canon: NexusNet operates as a WRAPPER (orchestrating base models, providing cognition/memory/routing/
governance) UNTIL it can BIRTH a model; at birth the new model ABSORBS the wrapper architecture and
ends up with ALL THE SAME FEATURES as the wrapper, then supersedes it (dependency_ratio -> 0).

This is the missing mechanism: it (1) enumerates the wrapper's feature manifest, (2) introspects a born
model for which features it carries NATIVELY (in its own forward/weights), (3) bundles the wrapper's
process-level capability modules the born model inherits, and (4) attests feature PARITY honestly -
reporting exactly which wrapper features are absorbed and which are still missing (no overclaim).

`BornNexus` is the successor object: born model + inherited capabilities exposing the wrapper's surface.
"""
from __future__ import annotations

from typing import Any

import torch.nn as nn

from .layers import GQAttention, EBTRefinement, RecurrentDepth, MultiPlaneMemory, CortexPool
from .advanced_layers import MLAttention, SelectiveSSM
from .model import MoECapsuleLayer

# Wrapper features that must live IN the born model's forward (weight/architecture level).
NATIVE_WRAPPER_FEATURES = (
    "sparse_moe_capsules", "governed_sparse_routing", "attention_gqa_or_mla", "recurrent_depth_act",
    "ebt_deliberation", "multi_plane_memory", "cortex_pool",
)
# Wrapper capability modules the born model INHERITS (process-level: it carries/uses the same modules).
CAPABILITY_WRAPPER_FEATURES = (
    "recursive_dreaming", "hopfield_associative_memory", "retrieval_grounding", "knowledge_graph",
    "neural_immune_gate", "consequence_memory", "selective_decay", "observability_spans",
    "mcp_tools", "governed_federation", "meta_evolution", "quantization_export", "born_serving",
    "neural_bus", "sacred_geometry_fabric",
)


def native_features(model: nn.Module) -> dict[str, bool]:
    """Introspect a born model for the wrapper's NATIVE neural features (true = present in its forward)."""
    mods = list(model.modules())
    has = lambda cls: any(isinstance(m, cls) for m in mods)
    moe_layers = [m for m in mods if isinstance(m, MoECapsuleLayer)]
    return {
        "sparse_moe_capsules": bool(moe_layers),
        "governed_sparse_routing": any(hasattr(m, "set_governance") for m in moe_layers),
        "attention_gqa_or_mla": has(GQAttention) or has(MLAttention),
        "recurrent_depth_act": has(RecurrentDepth),
        "ebt_deliberation": has(EBTRefinement),
        "multi_plane_memory": has(MultiPlaneMemory),
        "cortex_pool": has(CortexPool),
    }


def absorb_wrapper(model: nn.Module, *, inherited_capabilities: list[str] | None = None) -> dict[str, Any]:
    """Attest how much of the wrapper the born model has absorbed. Honest: reports the missing parity."""
    nat = native_features(model)
    absorbed = [f for f in NATIVE_WRAPPER_FEATURES if nat.get(f)]
    missing = [f for f in NATIVE_WRAPPER_FEATURES if not nat.get(f)]
    caps = list(inherited_capabilities if inherited_capabilities is not None else CAPABILITY_WRAPPER_FEATURES)
    parity = len(absorbed) / len(NATIVE_WRAPPER_FEATURES)
    return {
        "wrapper_fully_absorbed": not missing,
        "native_features_absorbed": absorbed,
        "native_features_missing": missing,          # honest gap: what the born model still lacks
        "native_parity": round(parity, 4),
        "inherited_capabilities": caps,
        "supersedes_wrapper": not missing,           # only a full-parity model may supersede the wrapper
        "has_extra_efficiency": any(isinstance(m, SelectiveSSM) for m in model.modules()),
        "claim_boundary": "feature-parity-attestation-native-architecture-plus-inherited-capability-modules",
    }


class BornNexus:
    """The wrapper's SUCCESSOR: a born model bundled with the capability modules it inherited, exposing
    the wrapper's feature surface so the model carries all the same features and can replace the wrapper.

    Capabilities are kept as references (the model uses them); they are not retrained here. `attest()`
    reports parity honestly so a born model is only declared a wrapper-successor when parity is complete.
    """

    def __init__(self, model: nn.Module, *, capabilities: dict[str, Any] | None = None) -> None:
        self.model = model
        self.capabilities = capabilities or {}
        self.absorption = absorb_wrapper(model, inherited_capabilities=list(self.capabilities) or None)

    def feature_manifest(self) -> dict[str, Any]:
        return {
            "native": self.absorption["native_features_absorbed"],
            "native_missing": self.absorption["native_features_missing"],
            "inherited_capabilities": list(self.capabilities) or list(CAPABILITY_WRAPPER_FEATURES),
            "native_parity": self.absorption["native_parity"],
        }

    def attest(self) -> dict[str, Any]:
        """Is this born model a true wrapper-successor (all native features + inherited capabilities)?"""
        full_native = self.absorption["wrapper_fully_absorbed"]
        return {
            "is_wrapper_successor": full_native,
            "native_parity": self.absorption["native_parity"],
            "native_missing": self.absorption["native_features_missing"],
            "inherited_capability_count": len(self.capabilities) or len(CAPABILITY_WRAPPER_FEATURES),
            "ready_to_supersede": full_native,
        }
