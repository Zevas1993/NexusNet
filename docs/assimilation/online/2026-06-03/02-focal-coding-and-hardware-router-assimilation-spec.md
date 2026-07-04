# Focal Coding And Hardware Router Assimilation Spec

Status: candidate assimilation packet
Date added: 2026-06-03
Canon entries: `PB-2026-06-03-099` through `PB-2026-06-03-100`
Primary canon addendum: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
Primary ledger: `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`

## Source Evidence

Primary source refs:

- `https://thenewstack.io/jetbrains-mellum2-open-source-coding-model/` (operator pointer; access returned HTTP 403 during this pass)
- `https://blog.jetbrains.com/ai/2026/06/mellum2-goes-open-source-a-fast-model-for-ai-workflows/`
- `https://huggingface.co/JetBrains/Mellum2-12B-A2.5B-Thinking`
- `https://arxiv.org/abs/2605.31268`
- `F:/NexusNet/NexusNet/.codex-remote-attachments/019e8ca7-5bc8-7781-b1f5-227dab1adfd2/8432ce0e-4327-45d7-a426-767ec8291463/1-Photo-1.jpg`
- `https://github.com/Pavelevich/llm-checker/blob/main/README.md`
- `https://www.npmjs.com/package/llm-checker`

Local package metadata check:

- `npm view llm-checker name version license description repository.url dist.tarball --json`
- Observed package: `llm-checker`
- Observed version: `3.5.15`
- Observed repository: `git+https://github.com/Pavelevich/llm-checker.git`
- Observed binaries from `npm view llm-checker dependencies optionalDependencies bin --json`: `llm-checker`, `ollama-checker`, `llm-checker-mcp`
- Observed license field: `SEE LICENSE IN LICENSE`; this requires explicit license review before any dependency use.

Existing NexusNet anchors:

- `docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md`
- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `nexusnet/teachers/capability_cards.py`
- `nexusnet/teachers/teacher_routing_policy.yaml`
- `ui/control-panel/app.js`
- `tests/test_teacher_registry.py`
- `tests/test_teacher_routing.py`
- `tests/test_tool_action_harness.py`
- `tests/test_hive_neural_network_internals.py`

## Assimilation Verdicts

Assimilate two targets with different runtime boundaries:

1. **Focal Coding Model Lane**: candidate model-route target for Mellum2-style specialized coding work.
2. **Hardware-Aware Local Model Fit Recommender**: candidate control-plane target for hardware scan, task-category model recommendation, and backend/quantization fit.

Neither target authorizes automatic model promotion, direct distillation, automatic package installation, automatic model download, autonomous write access, or bypass of existing sandbox/eval/governance gates.

## PB-2026-06-03-099 - Focal Coding Model Lane

Accepted pattern:

Mellum2 is useful to NexusNet as a specialized coding model route. The target is not "replace NexusBrain with Mellum2." The target is "give NexusNet a governed local or low-cost coding lane for narrow coding work where a focused coding model can draft, complete, triage, or test faster than a general route."

Candidate tasks:

- Code completion and localized patch drafting.
- Test generation for already-scoped behavior.
- Static-review triage and issue clustering.
- Harness, policy, and adapter boilerplate proposals.
- Repo-local summarization where context is bounded and citations can be preserved.
- Shadow comparison against existing coding providers.

Implementation path:

1. Add a model passport before adding any runtime route.
2. Record model id, source refs, license/card status, model-size notes only where source-verified, allowed task families, blocked task families, compatible backends, hardware constraints, eval suite, and rollback route.
3. Add the candidate to the provider registry as `review_required` or `shadow_only`.
4. Add a coding route policy that permits Mellum2 only for bounded coding tasks until eval proof exists.
5. Run it through a NexusNet coding scorecard: completion quality, test generation quality, diff minimality, regression rate, hallucinated API rate, policy compliance, and latency/cost.
6. Expose route decisions and scorecards in the Control Panel before any operator-visible recommendation is treated as trusted.
7. Keep all proposed writes under existing ToolActionHarness, sandbox, test, and review gates.

Required tests:

- Model passport rejects missing source, license, or rollback route.
- Coding route policy allows bounded shadow coding tasks and blocks governance/security/credential tasks.
- Provider registry marks the route `review_required` until license and eval evidence exist.
- ToolActionHarness still mediates every write-like proposal from the route.
- Regression scorecard blocks promotion when repo tests fail or hallucinated APIs exceed threshold.
- Control Panel route evidence includes model id, task family, gate state, and rollback provider.

Security and policy gates:

- Re-check exact model card, license, and permitted use before runtime integration.
- Block teacher, distillation, or training use unless rights explicitly permit it.
- Block high-risk autonomous planning, credential handling, policy override, and production mutation tasks.
- Preserve rollback to the prior coding provider.

## PB-2026-06-03-100 - Hardware-Aware Local Model Fit Recommender

Accepted pattern:

The screenshot points to a practical operator workflow:

1. Install `llm-checker`.
2. Run `llm-checker hw-detect`.
3. Run `llm-checker recommend --category coding`.

NexusNet should assimilate the workflow as a native control-plane capability: detect local hardware, score viable local models by task category, explain the recommendation, and keep the result available to routing and operator UI. The external npm package can be an optional reference adapter, but the core doctrine should be NexusNet-owned.

Implementation path:

1. Define a `HardwareSnapshot` schema with CPU, RAM, GPU, VRAM, backend, OS, accelerator tags, timestamp, privacy class, and redaction status.
2. Define a `ModelFitScorecard` with task category, candidate model, quantization, backend, memory budget, expected latency, privacy/cost score, source/license state, eval confidence, and recommendation rationale.
3. Add deterministic fixture tests for low-end, midrange, high-memory GPU, integrated-GPU, and unknown-hardware profiles.
4. Connect the scorecard to Edge Workload Router and provider registry as evidence, not as automatic route mutation.
5. Store local scan evidence in project-root artifacts with redacted fields.
6. Add a Control Panel view for current hardware tier, blocked oversized models, viable local routes, and why a recommendation was made.
7. Evaluate `llm-checker` as a read-only adapter only after npm package integrity, dependency, binary, license, and telemetry review.

Required tests:

- Hardware fixture produces deterministic tier and redaction status.
- `category=coding` returns ranked candidates with rationale and no install side effects.
- Low VRAM blocks oversized candidates and explains the block.
- Unknown package or unclear license returns `review_required`.
- Hardware evidence redacts serial numbers, full user paths, and private host identifiers.
- No automatic npm install, model download, provider mutation, or route promotion occurs.
- Optional external adapter can be disabled without disabling the native scorecard.

Security and policy gates:

- Never run global `npm install -g` from NexusNet automation without explicit operator approval.
- Never download models from the recommendation lane without a separate approved action.
- Never federate raw hardware identifiers, serials, hostnames, usernames, or full local paths.
- Treat CLI output as external evidence until normalized and validated by NexusNet-owned schema.
- Keep package and dependency provenance review separate from model recommendation quality.

## Promotion Boundary

`PB-2026-06-03-099` can move from candidate to a code-backed candidate only after a model passport, shadow route policy, eval scorecard, route evidence, and rollback proof exist.

`PB-2026-06-03-100` can move from candidate to a code-backed candidate only after a native hardware snapshot schema, model-fit scorecard, privacy redaction tests, no-side-effect tests, and Control Panel evidence exist.

Neither target can become a live production route without sandbox/eval/governance approval and a replayable rollback path.
