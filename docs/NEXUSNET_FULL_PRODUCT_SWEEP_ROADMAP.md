# NexusNet Full Product Sweep Roadmap

Status source of truth: `nexusnet.canon.NexusNetCanonRegistry` and the read-only `/ops/brain/canon`, `/ops/brain/research-candidates`, and `/ops/brain/product-status` API surfaces.

## Locked

- NexusNet remains the neural-core brain. Tools, RAG, MCP, A2A, AG-UI, and UI surfaces are mediated capabilities, not cognition authority.
- The repository split remains canonical: `nexusnet/` is the brain/core and `nexus/` is the platform/API/runtime shell.
- The 19 v2026 live expert capsules remain the locked starting roster.
- Teacher models are replaceable capability providers, not permanent cognition.
- Memory now has a controller layer with store, retrieve, update, summarize, archive, discard, dereference, and provenance lookup operations.

## Candidate

- Graphiti/Zep, MemOS-family research, A-MEM, AgeMem, MemexRL, MCP, A2A, AG-UI, TRL v1, verl, SkyRL, OSWorld, UI-TARS, Qwen3-VL, LFM2.5, vLLM, SGLang, LMCache, torchao, DeepEval, and OpenAI agent eval patterns are tracked through the Assimilation Registry.
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
- `/ops/brain/product-status` distinguishes locked, candidate, unresolved, disabled, diagnostic-only, and research-only surfaces.
