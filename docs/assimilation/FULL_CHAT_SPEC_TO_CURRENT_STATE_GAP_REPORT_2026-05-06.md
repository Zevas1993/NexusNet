# Full Chat Spec To Current State Gap Report - 2026-05-06

Status: read-only comparison against the live NexusNet workspace.

Scope:

- 134 online assimilation spec files under `docs/assimilation/online/2026-05-06/`.
- 10 watched-video assimilation spec files under `docs/assimilation/videos/2026-05-06/`.
- The online packet README, video packet README, and final missing-piece synthesis.
- Current workspace code, tests, and UI surfaces. Several matching files are currently uncommitted or untracked, so this report describes the live workspace state, not a clean release baseline.

## Executive Verdict

The full chat-created spec corpus is not asking for one more model. It is asking for NexusNet to become a governed developmental substrate: a system that knows its own capabilities, simulates futures before action, tests causal mechanisms, preserves diverse growth candidates, sleeps/consolidates, and promotes only through explicit evidence gates.

Current NexusNet is much closer than a blank slate. The workspace already contains strong scaffolded or code-backed surfaces for:

- growth cycles, teacher council evidence, dry-run student birth, rollback, and production-spine replay;
- self-review, policy scanning, eval registry, verifier search, artifact trust, protocol trust, and KAC runtime gates;
- memory quality, engram indexing, compiled knowledge artifacts, retrieval planning, GraphRAG/rerank lanes, and source-status discipline;
- runtime routing, quantization/cataloging, cache ledgers, model passports, workload scorecards, and provider registries;
- computer-use planning, operator events, browser profile/context policy, and Control Panel scorecards.

The main gap is integration depth. The pieces exist as many scorecards, registries, sidecars, and safety gates, but the final synthesis target is not present as a single `DevelopmentalCortexKernel` contract. There is no live kernel that continuously binds:

- `NexusBodySchema`
- `ReferenceFrameStore`
- latent `WorldModel`
- `CausalInterventionLab`
- `GrowthArchive`
- intrinsic motivation/learning-progress queue
- sleep/consolidation planner
- `PromotionTribunal`

This means NexusNet currently has a strong governance skeleton and many organs of a growth system, but not the unified developmental cortex that the full packet identifies as the highest-upside differentiator.

## Evidence Basis

Representative current workspace evidence:

- `nexusnet/growth/engine.py:19` defines `HiveModelGrowthEngine`; `start_dry_run` writes material scouting, curriculum, teacher council, dataset, student, training, eval, reviewer, and rollback artifacts.
- `nexusnet/growth/engine.py:1108` defines `_growth_gate`, which blocks growth when KAC runtime context or adapter-training evidence is not allowed.
- `nexusnet/growth/production_spine.py:18` defines `NexusNetProductionSpine`; `run_completion_cycle` sequences training, child execution, Hive MoE routing, tensor runtime, teacher council, sealed evals, registry, federation, dream execution, runtime foundry, deep replay, and productization.
- `nexusnet/dreaming/engine.py:16` defines `RecursiveDreamEngine`; `run_cycle` is shadow-only and records KAC-gated dream variants into memory, experiments, and governance events.
- `nexusnet/core/self_review.py:43` defines `SelfReviewGate`; reviews require independent reviewers, verifier refs, eval/evidence refs, and policy scan clearance before shadow acceptance.
- `nexusnet/knowledge/compiler.py:35` defines `KnowledgeArtifactCompiler`; compilation records source digests, citations, conflicts, permission filtering, source-ref security, artifact trust preview, freshness, and raw-retrieval fallback boundaries.
- `nexusnet/memory/quality_ledger.py:51` defines `MemoryQualityLedger`; claims carry answerability, source status, evidence strength, contradiction refs, evaluator refs, uncertainty, and policy scan state.
- `nexusnet/memory/engram_index.py:39` defines `NexusEngramIndex`; it is explicit sidecar memory, not hidden model-weight authority.
- `nexusnet/policy/kernel.py:100` defines `PolicyKernel`; built-in rules cover training approval, eval gates, memory provenance, canon claim source status, tool sandboxing, protocol trust, artifact provenance, and codegraph/test expectations.
- `nexusnet/security/artifact_trust.py:33` defines `ArtifactTrustRegistry`; it scans artifacts and deep replay bundles for license, provenance, checksum, signature, pickle risk, policy state, and promotion blockers.
- `nexusnet/protocols/trust.py:31` defines `ProtocolTrustRegistry`; protocol adapters require identity, consent, permissions, and revocation envelopes.
- `nexusnet/evals/registry.py:53` defines `EvalRegistry`; suites and shadow runs are promotion-gated by benchmark refs, held-out state, verifiers, traces, evidence, operator approval, and policy.
- `nexusnet/evals/verifier_search.py:24` defines `VerifierSearchRegistry`; candidate selection stays shadow-only until human review.
- `nexusnet/runtime/inference_economy_router.py:52` defines `InferenceEconomyRouter`; routing uses privacy gates, task specificity, scoring, model assignment, fallbacks, cost ledgers, governance gates, and policy scans.
- `nexusnet/runtime/cache_ledger.py:61` defines `EffectiveContextCacheLedger`; effective-context and KV-cache claims require measurement, privacy, redaction, evidence, and quantization gate status.
- `nexusnet/vision/computer_use.py:49` defines `MultimodalComputerUseController`; computer-use planning is observe-first, local-first, sandbox/policy gated, and trace replay bounded.
- `ui/control-panel/app.js` renders scorecards for runtime, self-review, protocol trust, policy, cache ledger, engram memory, knowledge artifacts, growth engine, eval registry, artifact trust, memory quality, and concept telemetry.

## Maturity Scale

- M0: absent from current workspace.
- M1: documented/spec-only or canon-only.
- M2: code scaffold or registry exists, but mostly records plans/evidence instead of executing the target.
- M3: code plus tests or UI-backed scorecards exist, but it is still gated/shadow/replay-first.
- M4: active production behavior with live execution, rollback, tests, and operator promotion paths.

Most of the current NexusNet matching surfaces are M2-M3. The final developmental cortex is M1-M2 because its ingredients exist, but the unified kernel does not.

## Full Spec Coverage By Rank Band

| Spec band | What the specs demanded | Current state | Maturity | Main gap |
| --- | --- | --- | --- | --- |
| Online 1-15 | Agent routing ladder, step/process/navigation benchmarks, belief revision, document certification, workflow verification, protocol trust, embeddable agent core, open model runtime ladder, commerce-style delegation, observability, agent UI protocols | Runtime routing, policy, protocol trust, KAC, memory quality, retrieval planning, and Control Panel scorecards exist. Open-first routing is present in code shape, not fully benchmark-certified. | M2-M3 | External benchmark adapters and protocol/UI negotiation are not yet runnable certification lanes. |
| Online 16-31 | Terminal/mobile/browser/desktop/code/tool/use-case benchmarks plus Inspect-style evaluation spine | Eval registry, verifier search, computer-use plans, operator events, and tests exist. | M2-M3 | No first-class BrowserGym, OSWorld, Terminal-Bench, SWE-bench, BFCL, tau/SABER, or Inspect-compatible runnable harness layer has been productized. |
| Online 32-56 | Red-team stack, OWASP/Five Eyes guidance, policy-as-code, identity delegation, sandbox tiering, RAG evals, runtime/cache/gateway/budget control, provenance, AI BOM, workflow engines, prompt governance | PolicyKernel, ArtifactTrustRegistry, ProtocolTrustRegistry, KAC, cache ledger, runtime router, runtime workload scorecards, red-team services, signing, and Control Panel surfaces exist. | M3 for core registries; M1-M2 for external standards | Rules are Python-local, not yet OPA/Cedar/FGA/Object-Capability tokens. Supply-chain receipts, BOM graphing, and release trust are partial, not complete. |
| Online 57-71 | Grammar-constrained decoding, parallel tool DAGs, adaptive reasoning effort, reflective optimization, context playbooks, object capabilities, hermetic task capsules, CRDT state, formal checking, property tests, evidence DAGs, speculative decoding, verifier search, learned cascades, lineage ledgers | Verifier search exists. Runtime routing, cache ledgers, KAC, evidence refs, tests, and policy surfaces cover parts of this band. | M1-M3 depending target | Grammar kernel, tool DAG compiler, learned cascade router, formal/property testing as promotion gates, content-addressed evidence DAG, and durable lineage ledger are not unified. |
| Online 72-98 | Deep authority and isolation primitives: effect types, WASM components, confidential execution, event sourcing, feature flags, proof-carrying actions, semantic cache, federated learning, syscall sensors, chaos, FGA, TUF, reversible patch log, Starlark, CUE, SES, Biscuit, SCITT, zkVM, private compute, replay snapshots, reproducible builds, Landlock/seccomp, VC/DID, taint flow, seL4, CHERI | NexusNet has local policy, artifact trust, signing, sandbox/service placeholders, trace/replay surfaces, and operator-gated computer-use plans. | Mostly M1-M2; some M3 for policy/trust/signing | The authority-integrity spine is not implemented as typed capabilities, observed effects, reversible transactions, signed receipts, or OS-level isolation. |
| Online 99-108 | Deep ops spine: command/telemetry bus, deterministic failure foundry, runtime monitor synthesis, assurance cases, PROV/RO-Crate, C2PA, capability RPC, trusted time receipts, digital twins, incremental projections | Control Panel and visualizer expose many scorecards. Artifact trust and replay bundles exist. Concept telemetry and GenAI observability registry exist. | M1-M3 | No deterministic simulation failure foundry, generated runtime monitors, SACM assurance graph, PROV/RO-Crate export, C2PA evidence layer, trusted time receipts, or incremental projection engine. |
| Online 109-122 | Brain mapping, connectome simulation, whole-brain emulation boundary, organoid ethics, neuromorphic substrate, microcircuit reconstruction, global workspace router, active inference, hippocampal replay, morphogenesis, developmental AI, memory palace, Lullian search, symbolic change calculus | Current workspace has Hive substrate, memory planes, dream loops, concept telemetry, growth engine, and policy boundaries. The specs themselves correctly reject consciousness-uploading and lost-civilization claims as implementation evidence. | M1-M2 | No executable connectome/reference-frame circuit layer, neuromorphic event substrate, homeostatic state vector, hippocampal replay scheduler, or morphogenetic repair primitive. |
| Online 123-134 | Final missing-piece stack: cortical reference frames, latent world model, continuous self/body schema, causal intervention cortex, GFlowNet diverse candidates, intrinsic motivation, semantic pointers, neural cellular growth, liquid cortex, viability kernel, open-ended self-improvement archive, developmental cortex | Some ingredients exist: growth engine, production spine, dream engine, memory/KAC, evals, verifier search, self-review, policy, artifact trust, runtime routing, Control Panel. | M1-M2 overall; M3 for existing ingredient systems | No `DevelopmentalCortexKernel`, `NexusBodySchema`, `ReferenceFrameStore`, `WorldModel`, `CausalInterventionLab`, `GrowthArchive`, intrinsic motivation queue, semantic pointer substrate, cellular growth engine, viability gate, or unified `PromotionTribunal`. |
| Videos 1-10 | Frontier small model training, Jarvis operator shell, self-updating Space Agent surface, agentic RAG, GitNexus codegraph gate, synthetic truth guard, interpretability plane, Darwin Godel lineage, AlphaEvolve verifier search, TARS computer-use operator | Strong matches exist for synthetic truth guard, self-review, verifier search, growth lineage, KAC/retrieval, codegraph instructions, concept telemetry, computer-use planning, runtime routing, and Control Panel. | M2-M3 | Video targets are mostly assimilated as governance/scorecard surfaces, not as full runnable benchmark/product lanes. Jarvis remains UX/tool-surface inspiration only unless license and authority risk are resolved. |

## Domain Gap Matrix

| Domain | Covered specs | Current NexusNet evidence | Current maturity | Priority gap | Recommended next action |
| --- | --- | --- | --- | --- | --- |
| Model/runtime economy | Online 1, 12, 41, 49, 50, 52, 57-59, 68, 70, 78, 113, 131; Video 1 | `InferenceEconomyRouter`, provider registry, model scoring, quantization catalog, QES/AITune surfaces, cache ledger, runtime workload scorecards, model passport | M3 for deterministic routing and ledgers; M1-M2 for learned/speculative/runtime-neuro targets | Runtime decisions are evidence-rich but not yet a learned cascade or speculative/event-driven substrate | Build a `RuntimeDecisionLedger` that normalizes route, cache, quantization, cost, eval, and fallback evidence; keep learned cascade shadow-only |
| Memory/KAC/retrieval | Online 4, 6-8, 21, 24, 39, 48, 53, 61, 67, 71, 75, 78, 103, 108, 117, 120, 129; Video 4, 6, 7 | KAC, memory quality, engram index, retrieval planner, GraphRAG/rerank modules, concept telemetry, Control Panel cards | M3 for KAC/memory quality/engram; M1-M2 for advanced memory architecture | Missing reference-frame store, content-addressed evidence DAG, event-sourced trace log, incremental projections, semantic pointer binding, and sleep consolidation planner | Implement `ReferenceFrameStore` over KAC, engrams, retrieval, and trace refs before adding a latent world model |
| Governance/authority/security | Online 3, 9-10, 13, 20, 32-33, 43-47, 51, 54, 62, 72-90, 93-98, 102, 104-106, 111-112, 115, 132; Video 5, 6, 10 | PolicyKernel, ProtocolTrustRegistry, ArtifactTrustRegistry, ArtifactSigner, project-local keys, browser profile policy, operator events, computer-use policy gates | M3 for local registries; M1-M2 for high-assurance primitives | Authority is rule-scanned, but not expressed as typed effect/capability tokens with observed-effects tracing and reversible transactions | Create an authority-integrity spine: effect manifest, capability grant record, observed-effect receipt, rollback record, artifact trust receipt |
| Tool/browser/desktop/workflow control | Online 2, 5, 11, 14-18, 20, 25-28, 34-36, 40, 47, 55, 58, 63-64, 73, 80-81, 84-87, 92, 94, 99-100, 105, 107; Video 2, 3, 5, 10 | MultimodalComputerUseController, OperatorEventRegistry, BrowserContextMemory, BrowserProfilePolicy, runtime gateway/ACP surfaces, Control Panel operator panels | M2-M3 | Plans and policy boundaries exist, but no real browser/desktop benchmark harness, task capsule runner, tool DAG compiler, WASM sandbox, or deterministic replay snapshot is productized | Add a `ToolActionHarness` that replays read-only browser/desktop/shell actions under policy and emits operator-event receipts |
| Evals/verifiers/research loops | Online 2-8, 16-20, 22-23, 25-39, 48, 50, 56, 65-66, 69, 100-101, 126-128, 133; Videos 3, 6, 8, 9 | EvalRegistry, VerifierSearchRegistry, red-team services, assimilation scorecards, self-review gate, growth/production-spine eval stages | M3 for local eval/shadow gates; M1-M2 for external benchmark execution | Eval surfaces are not yet one normalized Inspect-style evidence model with external benchmark adapters | Build one eval event schema first, then attach Terminal-Bench/SWE/BFCL/BrowserGym/OSWorld as adapters |
| Growth/self-improvement | Online 22, 29, 37, 60-61, 69, 79, 109-134; Videos 3, 8, 9 | HiveModelGrowthEngine, ProductionSpine, RecursiveDreamEngine, SelfReviewGate, EvalRegistry, VerifierSearchRegistry, ArtifactTrustRegistry | M3 for shadow growth/eval/replay; M1-M2 for developmental cortex primitives | Current self-improvement is evidence-gated but not developmental: no body schema, world model, causal lab, curiosity frontier, GFlowNet archive, or tribunal contract | Start the P0 `DevelopmentalCortexKernel` as an orchestrator over existing modules, not a new autonomous mutator |
| Observability/UI/assurance | Online 10, 14-15, 42, 75, 99, 102-108; Videos 5, 7, 10 | Control Panel renderers, visualizer, concept telemetry, GenAI observability registry, replay/artifact trust surfaces | M2-M3 | Control Panel has many snapshots, but not a maintained event-sourced projection system or assurance-case graph | Add append-only event records and projection builders before expanding visual UI complexity |

## What Is Already Strong

1. Governance-first posture: most dangerous lanes are shadow-only, candidate-only, or blocked pending human/operator review.
2. Source-status discipline: KAC, memory quality, artifact trust, and policy rules all reinforce provenance instead of treating generated claims as truth.
3. Growth and replay skeleton: `HiveModelGrowthEngine` and `NexusNetProductionSpine` already encode the right general shape: teacher review, sealed eval, rollback, replay, and productization gates.
4. Control Panel breadth: many of the spec domains already have operator-visible scorecards, which is valuable for commercial readiness.
5. Open-first runtime direction: routing, provider registry, quantization, cache, workload, and model-passport surfaces align with the open/local cost-efficiency specs.

## What Must Not Be Claimed Yet

Do not claim current NexusNet has any of the following as implemented product behavior:

- consciousness upload, whole-brain emulation, or sentience;
- a continuous `NexusBodySchema`;
- a learned latent `WorldModel` or JEPA/Dreamer-style imagination engine;
- cortical reference frames as executable local models;
- causal intervention experiments that prove mechanisms rather than correlations;
- GFlowNet or intrinsic-motivation-driven candidate selection;
- neural cellular automata growth or regenerative graph/circuit repair;
- semantic pointer/vector-symbolic binding;
- trusted time receipts, SCITT receipts, C2PA credentials, or PROV/RO-Crate evidence exports;
- object-capability token delegation, FGA/Zanzibar authz graph, WASM/SES plugin compartments, syscall/eBPF observed-effects tracing, or Landlock/seccomp enforcement;
- deterministic simulation failure foundry or runtime monitor synthesis.

Some of those ideas exist in docs, specs, tests, or adjacent registries. They are not yet unified live features.

## P0 Missing-Piece Implementation Ladder

The highest-leverage implementation path is not another broad research pass. It is a narrow kernel that unifies the strongest existing pieces.

1. Define `DevelopmentalCortexKernel` as a non-mutating orchestrator.
   - Inputs: trace refs, current task, runtime route, memory/KAC refs, policy state, eval state, growth state.
   - Outputs: `body_schema_snapshot`, `reference_frame_updates`, `dream_request`, `causal_test_request`, `growth_archive_candidate`, `promotion_tribunal_case`.
   - Boundary: no production mutation; emits evidence and requests only.

2. Add `NexusBodySchema`.
   - Build from current registries: provider catalog, runtime router, cache ledger, quantization catalog, policy rules, protocol trust, artifact trust, memory/KAC status, eval registry, computer-use permissions.
   - Purpose: NexusNet should know what tools/models/memory/policies it has, what is degraded, what is blocked, and what it is allowed to do.

3. Add `ReferenceFrameStore`.
   - Store local frames for project, artifact, tool, model, memory region, user goal, task, and runtime state.
   - Use existing KAC, engram index, retrieval planner, GraphRAG/rerank, memory quality, and trace refs.
   - Purpose: avoid flattening everything into one prompt context.

4. Upgrade dreaming into simulation requests.
   - Keep `RecursiveDreamEngine` shadow-only.
   - Add deterministic scenario seeds, expected-outcome fields, reality-gap metrics, and policy-gated replay refs.
   - Do not claim latent world-model learning until a real encoder/predictor/evaluator exists.

5. Add `CausalInterventionLab`.
   - Start with deterministic, non-production interventions: prompt variant, route variant, retrieval source removal, cache on/off, tool disabled/enabled, policy stricter/looser in simulation.
   - Record causal confidence as `confirmed`, `refuted`, or `unknown`.

6. Add `GrowthArchive`.
   - Store diverse candidate improvements from verifier search, dream variants, eval deltas, failure reports, KAC gaps, and runtime/cost anomalies.
   - Preserve weird but promising candidates; do not collapse to only the current top score.

7. Add `PromotionTribunal`.
   - Unify SelfReviewGate, EvalRegistry, PolicyKernel, ArtifactTrustRegistry, MemoryQualityLedger, growth gate, rollback evidence, and operator approval.
   - Output one decision: rejected, archived, shadow, canary-requested, or active-requested.
   - Active remains impossible without explicit operator approval and artifact trust.

## Bottom Line

The full chat spec packet says the missing piece is not "AI that secretly grows itself." The grounded version is a governed developmental cortex that turns NexusNet's existing modules into a coherent growth loop. Current NexusNet already has many of the safety gates, ledgers, and scorecards required for that loop. The next build should stitch them into a single developmental contract before adding more isolated research targets.
