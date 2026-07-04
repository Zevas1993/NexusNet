"""Birth-capability manifest: does the wrapper have EVERY capability needed to birth the best MoE model?

Canon target: a USABLE WRAPPER with all the capabilities needed to birth a model, so it can take the
BEST outputs over time, train, and birth the best MoE model. This module enumerates those required
capabilities and VERIFIES each one's real mechanism is present in the codebase (an import-existence
check, not a static claim). It honestly separates two things:
  - CAPABILITY PRESENCE: is the mechanism that provides this capability actually built? (checked here)
  - PRODUCT COMPLETENESS: is it wired into the live wrapper, at scale, exercised by real usage over
    time? (NOT claimed here - that is the larger wrapper-product build + the long-horizon growth).
"""
from __future__ import annotations

import importlib
from typing import Any

# Each capability -> the real symbol that provides it (module path, attribute).
BIRTH_CAPABILITIES: list[dict[str, str]] = [
    {"key": "wrap_and_capture", "desc": "capture wrapped-model outputs during usage",
     "module": "nexusnet.hive.continuous_assimilation", "symbol": "ContinuousAssimilationLoop"},
    {"key": "provenance_tagging", "desc": "tag each capture with its source model",
     "module": "nexusnet.hive.continuous_assimilation", "symbol": "AssimilationRecord"},
    {"key": "best_output_curation", "desc": "take the BEST outputs over time (quality-curated)",
     "module": "nexusnet.hive.continuous_assimilation", "symbol": "ContinuousAssimilationLoop"},
    {"key": "quality_scoring", "desc": "score outputs on held-out quality gates",
     "module": "nexusnet.hive.net.eval_gates", "symbol": "evaluate_capsule_gates"},
    {"key": "expert_routing", "desc": "route knowledge to the correct expert node",
     "module": "nexusnet.hive.net.governed_routing", "symbol": "GovernedSparseRouter"},
    {"key": "distillation_training", "desc": "train experts from teacher soft targets",
     "module": "nexusnet.hive.net.distill", "symbol": "train_with_distillation"},
    {"key": "continuous_training", "desc": "Ivy-League training is continuous, not one-time",
     "module": "nexusnet.hive.continuous_assimilation", "symbol": "ContinuousAssimilationLoop"},
    {"key": "moe_composition", "desc": "compose experts into one MoE",
     "module": "nexusnet.hive.net.expert_assimilation", "symbol": "fuse_moe_layers"},
    {"key": "architecture_search", "desc": "evolve the best architecture genome",
     "module": "nexusnet.hive.net.meta_evolution", "symbol": "evolve_architecture"},
    {"key": "efficiency_optimization", "desc": "invent the best bit-model / quant",
     "module": "nexusnet.hive.net.efficiency_autopilot", "symbol": "EfficiencyAutopilot"},
    {"key": "recursive_dreaming", "desc": "recursive neural dreaming -> gated training",
     "module": "nexusnet.hive.net.recursive_dream_training", "symbol": "recursive_dream_train"},
    {"key": "federated_learning", "desc": "aggregate learning across users (governed)",
     "module": "nexusnet.hive.net.governed_federation", "symbol": "governed_federated_round"},
    {"key": "teacher_replacement", "desc": "replace teachers with native experts ASAP",
     "module": "nexusnet.hive.wrapper_orchestrator", "symbol": "WrapperAgentOrchestrator"},
    {"key": "birth_gating", "desc": "independence milestones / TRP gate the birth",
     "module": "nexusnet.hive.net.birth", "symbol": "independence_milestones"},
    {"key": "wrapper_absorption", "desc": "born model absorbs the wrapper's features",
     "module": "nexusnet.hive.net.absorption", "symbol": "absorb_wrapper"},
    {"key": "born_export", "desc": "export the born model to runtime formats",
     "module": "nexusnet.hive.net.quantize_export", "symbol": "export_birthed_model"},
    {"key": "born_serving", "desc": "serve the born model independently of the wrapper",
     "module": "nexusnet.hive.net.born_serving", "symbol": "BornModelRunner"},
    {"key": "self_improvement_all_aspects", "desc": "improve every aspect of itself",
     "module": "nexusnet.hive.self_improvement_engine", "symbol": "SelfImprovementEngine"},
    {"key": "real_data_birth", "desc": "train + birth a real model on real data",
     "module": "nexusnet.hive.net.real_birth", "symbol": "run_real_birth"},
    {"key": "full_birth_pipeline", "desc": "compose every lane into one birth pipeline",
     "module": "nexusnet.hive.net.full_birth", "symbol": "full_birth"},
]


def _present(module: str, symbol: str) -> bool:
    try:
        return hasattr(importlib.import_module(module), symbol)
    except Exception:
        return False


def birth_capability_manifest() -> dict[str, Any]:
    """Verify each birth-required capability's mechanism exists. Honest capability-presence report."""
    rows = []
    for cap in BIRTH_CAPABILITIES:
        present = _present(cap["module"], cap["symbol"])
        rows.append({**cap, "present": present})
    present_count = sum(1 for r in rows if r["present"])
    total = len(rows)
    return {
        "surface_id": "birth-capability-manifest",
        "capabilities": rows,
        "total": total,
        "present": present_count,
        "missing": [r["key"] for r in rows if not r["present"]],
        "all_capabilities_present": present_count == total,
        "capability_presence_ratio": round(present_count / total, 4) if total else 0.0,
        "claim_boundary": (
            "capability-presence-only; product-wiring + scale + real-usage-over-time are separate and "
            "are the larger wrapper-product build, not asserted by this manifest"
        ),
    }
