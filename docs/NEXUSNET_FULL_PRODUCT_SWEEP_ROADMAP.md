# NexusNet Full Product Sweep Roadmap

Status source of truth: `nexusnet.canon.NexusNetCanonRegistry` and the `/ops/brain/canon`, `/ops/brain/research-candidates`, `/ops/brain/memory-os`, `/ops/brain/security/protocol/*`, `/ops/brain/runtime/context-assembly`, `/ops/brain/training/*`, and `/ops/brain/product-status` API surfaces.

## Locked

- NexusNet remains the neural-core brain. Tools, RAG, MCP, A2A, AG-UI, and UI surfaces are mediated capabilities, not cognition authority.
- The repository split remains canonical: `nexusnet/` is the brain/core and `nexus/` is the platform/API/runtime shell.
- The 19 v2026 live expert capsules remain the locked starting roster.
- Teacher models are replaceable capability providers, not permanent cognition.
- Memory now has a controller layer with store, retrieve, update, summarize, archive, discard, dereference, and provenance lookup operations.
- Memory OS records are persisted under the project artifacts directory so lifecycle/provenance facts survive service rebuilds.

## Candidate

- Graphiti/Zep, MemOS-family research, A-MEM, AgeMem, MemexRL, MCP, A2A, AG-UI, TRL v1, verl, SkyRL, OSWorld, UI-TARS, Qwen3-VL, LFM2.5, vLLM, SGLang, LMCache, torchao, DeepEval, and OpenAI agent eval patterns are tracked through the Assimilation Registry.
- Assimilation candidates now support audited status/maturity updates; registry changes remain explicit overlays rather than silent replacements of locked canon.
- Candidate runtimes are not runnable simply because they are registered. They require health, security, eval, and provenance evidence before promotion.
- OpenRLHF is marked `candidate_requires_pin` because the research refresh found future-dated README entries relative to 2026-04-26.

## Unresolved

- Exact EBT scoring weights remain unresolved. The contract is locked; the formula is not.
- The one-million-token goal is an effective-context architecture target, not a raw-context promise.

## Gated

- Real model training is gated until canon, traces, evals, memory provenance, license metadata, and protocol security pass.
- External tools are denied or held until signed/allowlisted server definitions, identity metadata, sandboxing, permissions, user consent, and audit logging pass.
- Dream, simulation, and consequence loops remain shadow-only and cannot mutate production memory or models.

## Operator Checks

- `python -m pytest --collect-only -q` is the baseline import and collection gate.
- `tests/test_full_product_sweep_scaffold.py` validates the product sweep contracts.
- `tests/test_product_sweep_operationalization.py` validates the operational Memory OS, protocol security, EBT, eval, and training-gate surfaces.
- `tests/test_product_sweep_deepening.py` validates durable Memory OS persistence, audited assimilation updates, protocol server registration/consent gates, effective-context assembly, and artifact-backed training dataset export.
- `/ops/brain/product-status` distinguishes locked, candidate, unresolved, disabled, diagnostic-only, and research-only surfaces.

## Operational Surfaces

- `/ops/brain/research-candidates/{candidate_id}/status` records audited living Assimilation Registry updates with status, maturity, evidence, and notes.
- `/ops/brain/memory-os/*` stores, persists, updates, retrieves, archives, discards, dereferences, and audits provenance for controller-level memory facts.
- `/ops/brain/security/protocol/*` evaluates MCP/A2A/AG-UI tool attempts, registers signed/allowlisted protocol servers, records accept/decline/cancel consent decisions, and exposes audit events without executing denied or held tools.
- `/ops/brain/runtime/context-assembly` exposes the effective-context planner for raw prompt, rolling summary, memory planes, indexed evidence, and KV/cache reuse.
- `/ops/brain/ebt/*` exposes the pluggable EBT contract and diagnostic route scoring while formula weights remain unresolved.
- `/ops/brain/evals/scenarios` exposes trace-first eval scenarios for route choice, tool correctness, memory recall, critique quality, and policy violations.
- `/ops/brain/training/export-record` validates training export records and keeps checkpoint promotion gated behind eval, license, security, and provenance proof.
- `/ops/brain/training/export-dataset` writes JSONL and manifest artifacts before any checkpoint promotion is considered.
