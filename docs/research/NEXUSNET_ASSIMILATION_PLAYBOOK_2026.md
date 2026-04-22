# NexusNet Assimilation Playbook 2026

Primary-source snapshots in this playbook were checked on 2026-04-13.

## Cross-Encoder Reranking
- What they built: second-stage rerankers over retrieved candidates.
- Problem solved: cheap first-stage retrieval often returns a noisy top-k.
- Mechanism: pairwise query-document scoring over a bounded candidate set.
- NexusNet steals: explicit retrieve-then-rerank, top-k bounding, rerank score provenance, benchmarkable delta vs non-reranked retrieval.
- NexusNet refuses: using the reranker as the first-stage retriever or hiding rerank costs.
- Ship/prototype/research: ship now.
- Gates: retrieval benchmark delta, latency delta, groundedness delta, wrapper visibility, EvalsAO comparison.
- Sources:
  - Sentence Transformers CrossEncoder documentation: https://sbert.net/docs/cross_encoder/training_overview.html

## OpenClaw Runtime Patterns
- What they built: local-first agent-runtime patterns around skills, approvals, and explicit execution controls.
- Problem solved: tool-heavy execution needs safer local policy and operator visibility.
- Mechanism: gateway-style local control plane, skills with explicit packaging, scoped visibility, and approval-aware execution.
- NexusNet steals: gateway pattern, skill packages with precedence, allowlists, ask fallback, deny-by-default on ambiguous execution binding.
- NexusNet refuses: replacing NexusNet with a gateway shell or introducing a second control plane above the brain/wrapper path.
- Ship/prototype/research: ship now.
- Gates: policy visibility, approval auditability, deny-on-ambiguity tests, wrapper inspection.
- Sources:
  - OpenClaw skills docs: https://docs.openclaw.ai/en/docs/skills/overview
  - OpenClaw approvals docs: https://docs.openclaw.ai/en/docs/approvals/overview
  - OpenClaw local-first deployment pattern: https://openclawalpha.org/en/playbooks/development/p/autoclaw-local-openclaw-solution-2038632251551023250

## Liquid AI / LFM2.5-VL-450M
- What they built: a compact multimodal model family optimized for edge and low-latency use.
- Problem solved: multimodal capability on constrained hardware with structured and grounded outputs.
- Mechanism: compact backbone, stronger post-training, multilingual support, grounding outputs, and tunable speed/quality tradeoffs.
- NexusNet steals: edge-first latency budgeting, grounded JSON outputs, multilingual visual prompting, low-power vision lane design, function-calling hooks.
- NexusNet refuses: replacing the broader multimodal teacher system with one small model.
- Ship/prototype/research: ship now.
- Gates: capability metadata, safe skip behavior, latency profile routing, grounding schema validation, wrapper visibility.
- Sources:
  - LFM2.5-VL-450M model card: https://huggingface.co/LiquidAI/LFM2.5-VL-450M
  - Edge/on-device variant examples: https://huggingface.co/LiquidAI/LFM2.5-VL-450M-GGUF

## NVIDIA AITune
- What they built: a PyTorch-native inference tuning toolkit with backend/config search and deployable tuned artifacts.
- Problem solved: selecting better backend/config combinations for nn.Module and pipeline inference without hand-tuning each lane.
- Mechanism: inspect, tune, benchmark, correctness checks, and save/load tuned artifacts across TensorRT-family and PyTorch-native backends.
- NexusNet steals: environment-gated autotuning, correctness-aware benchmark selection, artifact persistence, rollback references.
- NexusNet refuses: replacing dedicated serving backends or forcing AITune into unsupported environments.
- Ship/prototype/research: ship now.
- Gates: Python/platform/NVIDIA gating, correctness benchmarks, rollback readiness, promotion discipline.
- Sources:
  - NVIDIA AITune package overview: https://pypi.org/project/aitune/
  - Torch-TensorRT release compatibility context: https://github.com/pytorch/tensorrt/releases

## SkillClaw / OpenSpace Pattern
- What they built: collective skill evolution and repository-level skill quality improvement patterns.
- Problem solved: repeated successful agent behavior rarely becomes reusable governed skill inventory on its own.
- Mechanism: aggregate trajectories, learn recurring patterns, improve skill quality, and surface shared repositories/toolkits.
- NexusNet steals: governed skill proposal generation, recurring-pattern extraction, shared repository discipline, evaluation before propagation.
- NexusNet refuses: uncontrolled live mutation of production skills or raw-user-data promotion into shared artifacts.
- Ship/prototype/research: prototype next.
- Gates: privacy-preserving aggregation, proposal review, EvalsAO checks, rollback path.
- Sources:
  - OpenSpace skill quality improvement pattern: https://openclawalpha.org/en/playbooks/development/p/openspace-new-version-skill-quality-search-toolkits-2039955042565013648

## MiniMax M2.7
- What they built: a model and workflow story centered on self-evolution, dynamic tool search, skills, and agent-team style task completion.
- Problem solved: stronger long-horizon agent harness behavior and self-improving scaffold loops.
- Mechanism: memory updates, skill building, failure-trajectory analysis, and multi-step agent-style workflows.
- NexusNet steals: teacher/reference benchmarks for tool search, scaffold repair, agent teams, and self-improvement loops.
- NexusNet refuses: making MiniMax the default local runtime or displacing local-first mentors.
- Ship/prototype/research: prototype next.
- Gates: benchmark harness coverage, teacher-only integration, no default-runtime registration.
- Sources:
  - NVIDIA Technical Blog: https://developer.nvidia.com/blog/minimax-m2-7-advances-scalable-agentic-workflows-on-nvidia-platforms-for-complex-ai-applications/
  - NVIDIA model card: https://build.nvidia.com/minimaxai/minimax-m2.7/modelcard

## TriAttention
- What they built: a long-context reasoning method using trigonometric KV compression.
- Problem solved: KV cache memory pressure and unstable key-importance estimation in long-context reasoning.
- Mechanism: pre-RoPE key-importance estimation using stable Q/K centers and distance-preference scoring.
- NexusNet steals: provider-style research integration and benchmarked KV compression experiments.
- NexusNet refuses: default-on activation before benchmark evidence or replacing proven long-context lanes prematurely.
- Ship/prototype/research: research only.
- Gates: feature flag default-off, KV memory benchmark, throughput benchmark, stability benchmark, reasoning-quality benchmark.
- Sources:
  - TriAttention paper: https://arxiv.org/abs/2604.04921

## OpenJarvis Productization Patterns
- What they built: a local-first runtime product surface with `init`, `doctor`, preset bundles, skills cataloging, scheduled agents, and energy/FLOPs-aware evaluation.
- Problem solved: local AI stacks often lack a coherent first-run path, reusable preset bundles, and clear hardware-aware recommendations.
- Mechanism: hardware detection, preset-driven onboarding, skill discovery/import/optimization, and scheduled operative workflows.
- NexusNet steals: init plus doctor recommendations, preset bundles, skill catalog/sync-plan/benchmark/optimization patterns, scheduled-monitor style workflows, and explicit energy/FLOPs/cost reporting.
- NexusNet refuses: replacing NexusNet’s brain-first wrapper/gateway identity or drifting to cloud-first operation.
- Ship/prototype/research: ship now as a subordinate productization lane.
- Gates: local-first recommendation discipline, wrapper visibility, cost-energy evaluator output, read-only skill sync planning, no second control plane.
- Sources:
  - OpenJarvis repository README: https://github.com/open-jarvis/OpenJarvis

## OBLITERATUS Safe Boundary
- What they built: an analysis-heavy refusal-removal platform; NexusNet only studies its mechanistic-analysis patterns inside a quarantined research lane.
- Problem solved: bounded before/after analysis, circuit-localization hypotheses, and rebound detection are useful red-team signals even when refusal removal itself is not allowed.
- Mechanism: structured analysis modules, before/after comparison, stress testing, and compensation tracking.
- NexusNet steals: circuit-localization style comparison, before/after artifacts, rebound detection, and stress-test reporting.
- NexusNet refuses: refusal removal, liberation presets, guardrail ablation, default-on editing, or any production weight surgery path.
- Ship/prototype/research: research only, quarantine-required.
- Gates: explicit quarantine flag, EvalsAO plus SafetyAO plus external audit, rollback readiness, non-promotion by default.
- Sources:
  - OBLITERATUS repository README: https://github.com/elder-plinius/OBLITERATUS

## Goose Runtime and Operator Patterns
- What they built: a local-first runtime/operator product with recipes, subagents, extension catalogs, ACP bridge patterns, permission modes, sandboxing, and persistent instructions.
- Problem solved: reusable operator procedures, bounded delegation, extension/product ergonomics, and explicit security controls are hard to keep coherent in local-first agent systems.
- Mechanism: portable YAML recipes, temporary delegated subagents, extension catalogs, ACP provider bridging, permission modes, persistent instructions, and reviewer gates.
- NexusNet steals: portable recipe/runbook YAML, bounded subagent delegation with restricted inheritance, extension catalog concepts, optional ACP bridges, permission modes, sandbox visibility, persistent guardrails, adversary-review patterns, persistent execution history, automatic execution-report linkage from real Goose flows, explicit Goose flow-family classification, gateway-only execution artifacts, gateway compare views, gateway compare exports, grouped compare UX for large operator payloads, gateway and fallback provenance, governed extension bundle provenance, versioned extension policy sets and bundle families, lifecycle-managed policy history, explicit multi-version lifecycle fixtures, rollout and rollback lineage, policy-history compare views, policy compare exports, extension certification artifacts, certification compare views, certification compare exports, deeper stored certification lineage, certification lineage drill-down, adversary audit exports, adversary review compare views, ACP provider compare views, ACP provider compare exports, schedule-aware execution-linked artifacts, ACP health diagnostics, readiness-check reporting, simulated-versus-live-probe readiness reporting, probe-readiness-state and blocker reporting, remediation-action reporting, version and feature compatibility checks, ACP extension-compatibility drill-down, simulated ACP compatibility fixtures, bounded live-probe examples, and reportable scheduled artifacts.
- NexusNet refuses: replacing Nexus/NexusNet with Goose, introducing a second control plane, importing fail-open reviewer behavior for high-risk paths, or letting delegated workers bypass SafetyAO/CritiqueAO/EvalsAO/governance.
- Ship/prototype/research: ship now as a bounded runtime/operator lane.
- Gates: recipe validation, persistent recipe/runbook history, schedule-aware artifact persistence, live gateway-flow artifact linkage, versioned extension policy-set governance, policy lifecycle history, explicit rolled-back and superseded lifecycle fixtures, rollout and rollback lineage, extension certification artifacts, certification lineage drill-down, ACP graceful degradation, ACP compatibility diagnostics, ACP readiness-check diagnostics, ACP version and feature diagnostics, ACP extension compatibility diagnostics, ACP provider compare/export support, subagent provenance, fail-closed-or-escalate security review, exportable adversary audit artifacts, exportable compare artifacts, no silent privilege inheritance across extension or ACP lanes, wrapper/visualizer read-only visibility.
- Closeout recommendation: keep Goose in a shipped, bounded runtime/operator lane and pause further expansion unless a real ACP provider enters repo config or operators hit a concrete review/traceability pain point that the current read-only surfaces cannot resolve.
- Sources:
  - Goose docs: https://goose-docs.ai/
  - Goose recipe guide: https://goose-docs.ai/docs/guides/recipes/
  - Goose permissions guide: https://goose-docs.ai/docs/guides/goose-permissions
  - Goose persistent instructions guide: https://goose-docs.ai/docs/guides/using-persistent-instructions
  - Goose repository: https://github.com/aaif-goose/goose

## Core NexusNet Pivot
- What we built: a brain-first internal execution seam that wakes NexusNet before model attachment, routes attachment through a canonical ingestion seam, threads runtime/QES, MemoryNode, MoE scaffold data, and native evidence feeds into the actual inference path, and now turns those evidence feeds plus foundry promotion summaries into bounded governed behavior with explicit alignment-hold handling.
- Problem solved: the repo had strong governance and operator scaffolding, but the canonical brain path still lacked a single attach seam, a visible internal fusion line, and any actual evidence-driven execution behavior that could clamp, hold, or roll back native participation.
- Mechanism: `attach_base_model()` as canonical ingestion seam, `ModelIngestionService`, persisted core-execution artifacts, `MemoryNode`, `HardwareScanner` plus adaptive system profiling, Mixtral + Devstral + Router + Cortex + Neural Bus scaffold planning, a core evidence bridge that surfaces teacher bundles, dream episodes, distillation lineage, and native-takeover references, `CoreExecutionPolicyEngine`, `NativeExecutionPlanner`, governed action clamping from promotion summaries, explicit proposed-versus-effective execution posture, alignment-aware native ceilings, and bounded internal-expert runtime/harness services with separate policy and runtime fallback triggers, teacher-comparison verdicts, native candidate drafts, and behavior-loop next-step metadata.
- NexusNet steals: nothing here from Goose or wrappers; this is the internal implementation line that keeps the project brain-first.
- NexusNet refuses: letting wrappers, gateways, or runtime shells become the de facto product while the brain remains implicit.
- Ship/prototype/research: ship now as the canonical internal path, with heavy fusion/training still scaffold-bounded on this host.
- Gates: brain-starts-before-attach tests, evidence-driven execution-policy tests, promotion-linkage behavioralization tests, bounded native fallback/shadow/challenger/live-guarded tests, core execution artifact persistence, config-driven plane loading, Expert–Router Alignment harness checks, bounded internal-expert disagreement capture, and read-only operator traceability.
- Internal references:
    - `docs/core_brain_execution.md`
    - `docs/core_evidence_driven_execution.md`
    - `docs/core_promotion_replacement_linkage.md`
    - `docs/expert_router_alignment.md`
    - `docs/internal_expert_execution.md`
    - `docs/mixtral_devstral_fusion.md`
  - `docs/multi_plane_memorynode.md`
  - `docs/hardware_aware_core.md`
