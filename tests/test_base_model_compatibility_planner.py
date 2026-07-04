from __future__ import annotations

import json

from nexusnet.core.compatibility_planner import BaseModelCompatibilityPlanner, CompatibilityStatus


def test_equal_hidden_dimensions_are_compatible():
    plan = BaseModelCompatibilityPlanner().plan(
        metadata={"model_name": "local-llama", "model_family": "llama", "vocab_size": 32000},
        router_hidden_dim=4096,
        expert_hidden_dim=4096,
        strict_product_mode=True,
    )

    assert plan.status == CompatibilityStatus.COMPATIBLE
    assert plan.adapter_recommendation is None
    assert plan.ok_for_product_attach is True


def test_mismatched_bridgeable_dimensions_require_adapter():
    plan = BaseModelCompatibilityPlanner().plan(
        metadata={"model_name": "devstral-coder", "model_family": "devstral", "vocab_size": 32000},
        router_hidden_dim=4096,
        expert_hidden_dim=6144,
        strict_product_mode=True,
    )

    assert plan.status == CompatibilityStatus.ADAPTER_REQUIRED
    assert plan.adapter_recommendation["adapter_type"] == "projection"
    assert plan.adapter_recommendation["output_shape"][-1] == 4096
    assert plan.ok_for_product_attach is True


def test_missing_strict_product_dimensions_are_unverified():
    plan = BaseModelCompatibilityPlanner().plan(
        metadata={"model_name": "unknown-local", "model_family": "unknown"},
        strict_product_mode=True,
    )

    assert plan.status == CompatibilityStatus.UNVERIFIED
    assert plan.ok_for_product_attach is False
    assert "missing-router-hidden-dim" in {issue.code for issue in plan.issues}
    assert "missing-expert-hidden-dim" in {issue.code for issue in plan.issues}


def test_invalid_shape_or_metadata_is_unsupported():
    plan = BaseModelCompatibilityPlanner().plan(
        metadata={"model_name": "bad-local", "vocab_size": 0, "parameter_count": -1},
        router_hidden_dim=-1,
        expert_hidden_dim=4096,
        strict_product_mode=True,
    )

    assert plan.status == CompatibilityStatus.UNSUPPORTED
    assert plan.ok_for_product_attach is False
    assert {"invalid-router-hidden-dim", "invalid-vocab-size", "invalid-parameter-count"} <= {
        issue.code for issue in plan.issues
    }


def test_plan_output_is_json_serializable():
    plan = BaseModelCompatibilityPlanner().plan(
        metadata={"model_name": "local-qwen", "model_family": "qwen", "vocab_size": 151936},
        router_hidden_dim=3584,
        expert_hidden_dim=3584,
        strict_product_mode=True,
    )

    dumped = plan.model_dump(mode="json")
    assert dumped["status"] == "COMPATIBLE"
    assert dumped["compatibility_plan_id"]
    json.dumps(dumped)
