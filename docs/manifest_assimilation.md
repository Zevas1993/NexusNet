# Manifest Assimilation For NexusNet

Status: live-control-plane implementation
Canon entry: PB-2026-05-03-053
Source: https://github.com/mnfst/manifest
Source reverified: 2026-05-31, see `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`

## Decision

NexusNet assimilates Manifest as an inference-economy pattern, not as the NexusNet brain.

The 2026-05-31 source check confirms the current `mnfst/manifest` repository is reachable, MIT-licensed, and still describes smart model routing for agents with complexity/specificity routing, provider mixing, cost tracking, fallbacks, local providers, and OpenAI-compatible routing. This strengthens the existing NexusNet inference-economy posture, but does not promote Manifest above NexusBrain policy, privacy gates, route audit logs, or local benchmark evidence.

Manifest-style routing becomes a subordinate runtime layer:

1. NexusBrain and policy decide whether a call may leave local execution.
2. The InferenceEconomyRouter classifies the task by specificity and complexity.
3. The router selects the cheapest acceptable provider/model that meets capability thresholds.
4. Fallbacks and cost/baseline evidence are recorded.
5. Execution remains shadow/canon-bound until the calling NexusNet surface authorizes use.

## What Was Assimilated

- Configurable multi-dimensional deterministic scoring instead of a fixed dimension count.
- Explicit override and policy route precedence before generic complexity scoring.
- Specificity routing for coding, browsing, data analysis, image/video, social/email/calendar, and trading.
- Tiered assignment for simple, standard, complex, reasoning, and default routes.
- Local provider support for Ollama, LM Studio, llama.cpp, and OpenAI-compatible local endpoints.
- Optional Manifest adapter using `manifest/auto`.
- Manifest telemetry opt-out requirement via `MANIFEST_TELEMETRY_DISABLED=1`.
- Response metadata capture for Manifest `X-Manifest-*` headers.
- Cost ledger with actual estimated cost and strong-baseline estimated cost.
- Redacted trace metadata with no raw prompt export.

## NexusNet Boundary

Manifest does not replace:

- NexusBrain authority
- hive substrate routing
- AO/expert governance
- sandbox/eval gates
- operator approval
- privacy rules
- cost and trace ledgers

Safety and privacy policy always execute before cost optimization.

## Live Implementation

- `nexusnet/runtime/inference_economy_router.py`
- `nexusnet/runtime/manifest_adapter.py`
- `nexusnet/runtime/model_scoring.py`
- `nexusnet/runtime/task_specificity_router.py`
- `nexusnet/runtime/model_tier_assignment.py`
- `nexusnet/runtime/provider_registry.py`
- `nexusnet/runtime/provider_fallbacks.py`
- `nexusnet/runtime/inference_cost_ledger.py`
- `config/inference_routing.yaml`
- `/ops/brain/inference-economy-router`
- `/ops/brain/inference-economy-router/route`
- `/ops/brain/canon/inference-economy-router`

## Promotion Gate

The v0 route decision is a shadow routing decision. A caller may execute through the selected provider only when the caller has its own permission, privacy, sandbox, eval, and human approval gates satisfied.
