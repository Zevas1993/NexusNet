from __future__ import annotations

from typing import Any


BASELINE_MODEL = {
    "provider_id": "frontier-baseline",
    "model_id": "strong-default-model",
    "cost_per_1m_input": 6.0,
    "cost_per_1m_output": 24.0,
}


def build_cost_ledger(
    *,
    trace_id: str,
    agent_id: str,
    selected_route: dict[str, Any],
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    estimated = _cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_price=float(selected_route.get("cost_per_1m_input") or 0.0),
        output_price=float(selected_route.get("cost_per_1m_output") or 0.0),
    )
    baseline = _cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_price=BASELINE_MODEL["cost_per_1m_input"],
        output_price=BASELINE_MODEL["cost_per_1m_output"],
    )
    return {
        "trace_id": trace_id,
        "agent_id": agent_id,
        "provider_id": selected_route["provider_id"],
        "model_id": selected_route["model_id"],
        "input_tokens_estimated": input_tokens,
        "output_tokens_estimated": output_tokens,
        "estimated_cost_usd": estimated,
        "baseline_provider_id": BASELINE_MODEL["provider_id"],
        "baseline_model_id": BASELINE_MODEL["model_id"],
        "baseline_cost_usd": baseline,
        "estimated_savings_usd": round(max(baseline - estimated, 0.0), 8),
        "raw_prompt_exported": False,
        "request_content_redacted": True,
    }


def _cost(*, input_tokens: int, output_tokens: int, input_price: float, output_price: float) -> float:
    total = ((input_tokens / 1_000_000) * input_price) + ((output_tokens / 1_000_000) * output_price)
    return round(total, 8)
