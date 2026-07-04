# Canon Book - Full Sequential Read Log (net-new findings per chapter)

Status: live log of a genuine sequential read of the Conversation Source Chapters
(`NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`, lines 17056-41524). One entry per source chapter
(C01-C39). Records only NET-NEW engineering content not already captured in the other research docs.
Coverage is tracked so the claim "fully read" is auditable, not asserted.

## Coverage tracker
- [x] C01 Increasing Context Window (17060-17679)
- [x] C02 Mixtral DevStral NexusNet Setup (17680-17974)
- [x] C03 RL Libraries (17975-18183)
- [x] C04 NexusNet Architecture Review / Master Spec (18184-19074)
- [x] C05 NexusNet Implementation Plan (19075-19929)
- [x] C06 Neural network diagram explanation (19930-20524)
- [x] C07 Transformer-based Neural Network (20525-21570)
- [x] C08 AI Architecture Research / OpenMythos recurrent-depth (21571-22055)
- [x] C09 Project Chat Analysis / consolidation + Codex brain-core seam (22056-22944)
- [x] C10 NexusNet Temporal AI Review (22945-23244)
- [x] C11 NexusNet diagram improvements (23245-23496)
- [x] C12 Project review request / MASTER BLUEPRINT (19 capsules + teacher pools + core internals) (23497-24322)
- [x] C13 MCP integration / dual-path TIM (24323-24570)
- [x] C14 Improving NexusNet with data / LeJEPA Dreaming-v2 (24571-24863) [deep detail already in addendum C]
- [x] C15 DeepEyesV2 review / agentic tool loop (24864-25101)
- [x] C16 Review AI Memory Features / episodic+semantic (25102-25345)
- [x] C17 Chat access details (meta/workflow only, no architecture) (25346-25599)
- [x] C18 Annotation Toolkit -> NNAT/NNAV (25600-25xxx)
- [x] C19 LLM-Council -> CouncilOrchestrator
- [x] C20 Microsoft FARA -> Fara-CUE computer-use
- [x] C21 GitHub Copilot CLI patterns
- [x] C22 final packaging (r21->r22 zip) [scanned]
- [x] C23 Agent0 -> Curriculum-Architect co-evolution
- [x] C24 MIT PaTH Attention review
- [x] C25 Agentic AI alliance protocols [scanned]
- [x] C27 Nemotron-Elastic-12B -> ElasticProfileManager
- [x] C28 Bloom -> EvalsAO external evaluator
- [x] C30 Flash-DMD Vision Subsystem (FDVS)
- [x] C26 Project Deep Dive Spec (Formal Spec v1.0/1.1/1.2 + Control&Governance Addendum)
- [x] C29 Generate NexusNet blueprint (16-section MVLM Master Blueprint + earlier 19-capsule taxonomy)
- [x] C31 NexusNet project overview (instruction hierarchy + early module layout)
- [x] C32 Neural network details (Three.js hive-mind visualizer)
- [x] C33 Audit nexusnet chats (MVLM v3 diagram + teacher mapping)
- [x] C34 LFM2 Deep Dive (HIL-AS + teacher_registry/policy scaffolding)
- [x] C35 Project Breakdown Request (29 confirmed components + 9 major Decisions)
- [x] C36 AI Architecture Visualization (Assistant Orchestrators Hive canon correction)
- [x] C37 Codex Project Prompt (canon -> actual codebase; promotion gates, teacher split, lanes)
- [x] C38 Research R-Zero integration (RND-R0, Graphiti TKG, quant evolution, r1->r22)
- [x] C39 Project status overview (continuous assimilation + wrapper-first build)
- [x] ALL 39 CHAPTERS READ - coverage complete

## C01 - Increasing Context Window
Net-new vs prior docs:
- **NexusAttention** is a named component (`model.py # patched transformer with NexusAttention`);
  `positional.py # RoPE/YaRN/SBA` (SBA = a third positional option alongside RoPE/YaRN).
- Named (deferred) file contracts: `core/cortex.py`, `core/neural_bus.py`, `moe/mixtral_moe.py`,
  `moe/expert_base.py`, `moe/expert_block_adapter.py`, `integration/expert_integration_manager.py`,
  `experts/`, `ops/` (VisualOps), `config/ logs/ data/ tests/`.
- **Automated Expert Block Adaptation** = a core NexusNet module (`ExpertBlockAdapter`): detect FFN
  shape diff vs Mixtral base, auto-generate input/output adapters, insert, validate, optional
  auto-retrain, log. "Swallow" new experts with minimal human surgery.
- Expert-match requirements: same hidden size, FFN layer count, activation, layernorm style, tensor
  shapes, dtype.
- Named routing risks (unresolved): **router collapse, expert hogging, expert neglect**.
- Cortex agency spectrum: passive aggregator vs active planner/teacher/intervener (active chosen).
- Deferred-in-C01: exact 1M context impl, Neural Bus protocol schema, each Mini-NexusNet internal
  design, NexusNet-powered router, memory ownership split (expert-local vs global Cortex).

## C02 - Mixtral DevStral NexusNet Setup
Net-new vs prior docs:
- **Hardware reality (target dev box):** RTX 5070 Ti 16GB VRAM, i7-13700K, 32GB DDR5, Windows 11.
  Locked constraint: full MoE retraining NOT practical locally -> **LoRA adapters trainable, expert
  weights frozen**; DeepSpeed MoE `zero_offload` (optimizer state to CPU).
- **MemoryNode struct file**: `memory/models/memory_node.py`, `class MemoryNode(NamedTuple)` with
  per-plane `torch.Tensor` subvectors. Config-driven via **`planes.yaml`** (dims, encoders),
  **`edges.yaml`** (hyperedge types: `trusts`, `aligned_with`, `predicts`), **`automation.yaml`**
  (training/dreaming schedules).
- **DreamAO hypergraph random walk**: periodically samples MemoryNodes across multiple planes; a dream
  that passes critique is injected back as a NEW MemoryNode with new hyperedges to its parents; over
  time NexusNet builds **higher-order meta-nodes** ("I am learning", "I enjoy solving puzzles") that
  are themselves MemoryNodes -> emergent self-model. Cross-plane attention: imaginal->emotional,
  conceptual->procedural, etc.
- **Expert package format**: slim adapter weights + router metadata under `~/.nexusnet/experts/...`;
  automation hook `on_model_download -> ingest_and_prune -> adapter package`; full checkpoint deleted
  after slim package written (ingest-and-prune).
- **5D mind map** origin (C02M0045): operator wanted memory NOT a 2D grid but "multiple planes of
  thought, almost a 5th-dimensional mind map" so memories/dreams connect many ways -> "creating self
  awareness". This is WHY the multi-plane MemoryNode exists.
- Hybrid MoE-VLM is the accepted long-term direction; vision (BLIP-2), audio (Whisper) experts staged;
  video deferred to frame/embedding approaches. Storage: vector DB or PyTorch-Geometric graph.
- Deferred: cross-family router/expert fusion (until Expert-Router Alignment matures), VLM-only
  backbone, heavy video-first expert stack.

## C03 - RL Libraries for NexusNet
Net-new vs prior docs:
- RL library role-mapping (staged adoption): **TRL** (RLHF/reasoning fine-tune, low-overhead proto),
  **Verl + RAGEN** (multi-turn agentic RL), **NeMo-RL / ROLL** (production-scale), **Verifiers +
  SkyRL** (R&D/prototyping). OpenRLHF/AReaL considered.
- Open question (unresolved): centralize RL in the core vs give all 19 capsules their own RL envs;
  how RL interacts with Safe Mode & thermal/VRAM safeguards; RL rollouts at 2M-token context.
- RL is a custom wrapper unifying these under the hive-mind router (not a single library dependency).

## C04 - NexusNet Architecture Review (the Master Spec build)
Net-new vs prior docs (this is the richest engineering chapter):
- **Canonical mission statement (C04M0015, verbatim):** "NexusNet is the core brain. It is supposed
  to do what a human brain does, so it'll upgrade other LLMs' neural network with NexusNet. In turn
  NexusNet should learn, adapt, assimilate, and improve its own code to further develop itself. I want
  it to grow into its own LLM, but starting just as the brain that's implanted into other models and
  is able to update itself based on every model it is implemented into, based on every task each user
  does... until it's able to develop its own LLM, VLM, MLM, etc." (THE north-star.)
- **Dual-graph knowledge design (C04M0050):** a structured knowledge graph PER plane/neuron, PLUS one
  large whole-brain graph specifically tied to the Core. Multidimensional reasoning. (Earlier docs had
  one hypergraph; canon wants per-plane graphs + a core-bound global graph.)
- **MemoryNode internal structure (C04M0004):** "Neurons as Subvectors" - each plane is a neuron;
  1.2 Encoders per Plane, 1.3 Cross-Plane Attention (learnable matrices), 1.4 Neuron Activation
  Examples; plus Decision Tree Paths + Decision Coefficients/Thresholds for agent routing.
- **Neurobiological realism layer (C04M0099) - net-new and important:** per-plane neocortical-style
  microcircuits; cross-plane synaptic mesh; spiking/event-driven updates; **cortical lamination
  (L1-L6: L4 input, L2/3 lateral, L5/6 output)**; neuromodulatory systems + reward-driven plasticity;
  dendritic-like subcompartments (basal=feedforward, apical=contextual); sleep/dream replay -> Hebbian
  or LoRA consolidation. (These map to substrate planes: microcircuit/laminar/transmission/plasticity/
  neuromodulator ledgers already in post-book PB-057/058.)
- **Full Master Spec ToC (C04M0113, 18 sections):** 1 Core Principles, 2 Multi-Plane Memory, 3 Graph
  Intelligence Consolidation, 4 Unbounded Multimodal Backbone (Perceiver IO), 5 Automated NAS, 6
  Principal-Agent RL orchestration, 7 Meta-Learning (MAML), 8 Associative Memory (Modern Hopfield), 9
  Dynamic Sparse Training & Pruning, 10 Assimilation & Self-Improvement Loops, 11 Model Orchestration
  & Hardware, 12 Security & Governance, 13 Tool Ecosystem & Plugin Platform, 14 VisualOps, 15
  Deployment, 16 Admin/Dev Tools, 17 Personalization/UX, 18 Phased Roadmap & Governance.
- **Evolution pipeline metrics (C04M0258, Opus-contributed, accepted):** `dependency_ratio` (% of
  responses needing base-model consultation), `native_generation` (unique neural pathways in
  MemoryNodes), `plane_maturity` (per-plane independence), `milestone_triggers` at 10%/.../independence
  levels; "homunculus cultivation" + synthetic experience generation in dream training. -> the
  Independence Milestones + Model Birth Protocol have concrete metrics.
- **Assimilation flow (C04M0012):** External Data -> ContextController (splitting) -> MemoryNode
  encoding -> Cross-Plane Attention -> Agent Orchestration -> answer/storage. `ContextController` is a
  named component (accepts raw text/files, returns structured MemoryNodes).
- **Hard operator constraints:** "If we reduce the kernel it removes capabilities... I don't want to
  downgrade or lose functions" (C04M0138) -> additive-only, never simplify away. "Dreaming and
  federated learning MUST be mandatory" (C04M0143). `features.yaml` runtime toggles (enable/disable
  modules at startup without deleting code, C04M0139).
- Research-backed enhancements accepted: Complementary Learning Systems (fast Hopfield episodic + slow
  semantic + Elastic Weight Consolidation), Neuro-Symbolic (Datalog/constraint layer), per-plane +
  global GNN, Perceiver IO multimodal backbone, NAS (hypernetwork-conditioned, multi-objective),
  Principal-Agent RL with SLA contracts, MAML meta-learning, dynamic sparse training/pruning.

## C05 - NexusNet Implementation Plan
Net-new vs prior docs:
- **Nexus = NexusNet's output, confirmed again (C05M0009):** "This is NexusNet not Nexus yet, although
  this final project could turn into Nexus." Reinforces C26M0012.
- **Resolved build order (C05M0014/0030/0038):** (1) write all NexusNet code; (2) merge Devstral as a
  Mixtral MoE expert (automated align/adapter); (3) replace/upgrade Mixtral's neural network WITH
  NexusNet; (4) THEN staged training (router+NexusNet -> +Devstral -> full end-to-end). Build the
  brain and fuse BEFORE wiring orchestration/AOs/UI.
- **Full 8-phase timeline (C05M0015/0023):** P1 scaffold+model acquisition, P2 staged fine-tune+
  validation, P3 orchestrator+tool registry, P4 AO+agent framework, P5 RAG+memory+logging, P6
  VisualOps console, P7 packaging+deployment, P8 Android "Nexus" mobile app, P9 advanced/ongoing.
- **Sealed-service distribution model (C05M0106/0107) - net-new:** ship NexusNet as a SEALED engine;
  users run inference, their usage signals are collected, **federated adapter learning** improves the
  shared core, but **users cannot edit/update NexusNet code/config** (locked-down). Privacy/compliance
  + observability/rollback built in. This is HOW the "all users get the update" loop is delivered.
- **Named scaffold files (C05M0131):** `scripts/fuse_and_align.py` (load states -> init NexusNetCore
  -> merge weights -> adapter shim on mismatch -> dry-run test -> save), `scripts/model_watcher.py`
  (debounced auto-fusion on model add/remove/update -> plug-and-play), `NexusNetCore` class, the
  canonical integration path: profile -> attach_base_model -> fuse experts -> inference -> watcher.
- **Plug-and-play lifecycle (C05M0046/0050):** auto-check on new model integration AND on model
  removal/update to keep router<->expert alignment ready.
- **Adaptive Profiling & Startup (C05M0064):** hardware detection (CPU/GPU/memory/power) -> auto-config
  quantization + adapter sizing + expert scaling; 1M tokens is the MINIMUM context; NexusNet tunes for
  efficiency AND performance per hardware. Hardware scanner picks the best quantization method.
- **Full canonical file scaffold (C05M0071/0127/0142/0229):**
  `config/global.yaml` (runtime + adaptive thresholds, `min_context_window`), `config/nexusnet_config.json`
  (arch hyperparams), `config/planes.yaml` (plane dims + encoder classes), `config/edges.yaml`;
  `models/nexusnet.py` (`NexusNetCore`, `Adapter` bottleneck = down_proj/up_proj, `inject_adapters`);
  `memory/models/memory_node.py` (`MemoryNode` NamedTuple + `zeros()` from config);
  `hardware.py` (`HardwareScanner`, `AdaptiveSystemProfiler`);
  `scripts/fuse_and_align.py` (-> `nexusnet_fused_base.pt` + `fusion_report.json`),
  `scripts/model_watcher.py` (`ModelWatcher`, debounced auto-fuse on add/update/remove),
  `scripts/dream_loop.py` (Recursive Neural Dreaming, configurable interval / cron / idle hook),
  `scripts/mutation_runner.py` (**Neural DNA** architectural mutation, **benchmark-gated merges**),
  `scripts/train_stage.py` (4 staged-training stages: router-only -> router+experts -> full),
  `scripts/evaluate.py` (BLEU/ROUGE/perplexity), `scripts/migrations/add_new_planes.py` (backfill
  legacy memories with zero-planes on schema bump), `tests/test_model_inference.py`.
- **Phase-2 core is a HYBRID processing core "(Mamba...)" (C05M0156):** the NexusNet core is not a
  pure transformer - it includes Mamba/SSM-style components in the hybrid processing core (net-new;
  pairs with NexusAttention + the looped/recurrent reasoning lane).
- **Neural DNA (C05M0168, Phase 4):** architectural + hyperparameter mutations in production, run by
  `mutation_runner.py`, **gated by benchmark before merge** (sandbox/eval/rollback). Dreaming +
  Neural DNA together = the autonomous self-evolution engine.
- **Schema versioning:** `memory.schema_version` in config (e.g. v1.0 -> v1.1) with migration script;
  memory subsystems MUST iterate `planes.yaml` dynamically, never hard-code planes (locked decision).

## C06 - Neural network diagram explanation
Net-new vs prior docs:
- **Core-is-a-neural-network lock (C06M0122/0123):** "NexusNet core should have its OWN neural network
  which then connects to everything like in a hive mind"; the Core must be visualized with a visible
  internal structure (input->hidden->output layers) "just like the expert capsules" - it is the master
  neural brain at the center, NOT a labeled circle. (Foundational hive-mind visual lock.)
- Visualization canon: 19 expert capsules as hexagon subnetwork-brains, nonlinear multi-path routing
  arrows, Recursive Dreaming + Meta Reasoner + Memory Capsule Router + Consequence Feedback modules,
  capsules fire/activate when invoked; Ultron-style energetic strands; click-to-zoom into internals.

## C07 - Transformer-based Neural Network (EARLIEST chat, 2025-06-23; foundational invention)
Net-new vs prior docs (this is where the core NN was invented):
- **`NexusMemoryNet`** = the named 1M-token core architecture, with these REAL components (C07M0025):
  1. **Sparse Pre-Filter Layer** (drop low-value tokens early)
  2. **Token Clusterer / Semantic Compressor** (cluster+compress tokens)
  3. **Dual-Track Attention System** (local fine + global compressed tracks)
  4. **External Memory Router** (offload to memory store, retrieve on demand)
  5. **Compressed Summary Injector** (inject summaries of distant context)
  6. **Position Encoding Overhaul** (RoPE/YaRN + custom long-range scheme).
- **Brain-boots-first principle (C07M0138/0156):** the brain (NexusNet) must load FIRST, like waking
  up, BEFORE the LLM/VLM; it then monitors model startup, logs load details, and configures weights/
  transformers/quantization. The model never starts before the brain. (Engineering ordering lock.)
- **Full innovation roster invented here (C07M0027/0267):** Learned Dynamic Sparsity (self-pruning),
  Adaptive Computation Time (ACT), Micro-Agent Clusters (MACs), token-level speculative decoding,
  multi-stage compression/expansion, **Neuromorphic spiking attention**, Recurrent Memory Transformers
  (RMT) with adaptive decay, context-aware hybrid attention, internal-RAG neural indexing, Online NAS;
  plus **Neural DNA, Fractal Compression, Neural Immune System, Selective Memory Decay, Neural Sleep,
  Meta-Reflection, Adaptive Creativity, Swarm Intelligence** as named core modules.
- **Quantum-inspired lane (C07M0029/0030):** complex-valued attention, quantum-inspired tensor
  networks, quantum vector embeddings, simulated-annealing optimization - all CPU-runnable, flagged
  experimental. (Net-new; an explicit "wilder" research lane, consumer-hardware constrained.)
- **AdaptiveSystemProfiler** (C07M0021) = first-class startup component: detects CPU/GPU/RAM/Disk/OS,
  emits a system-adaptation config + debug/log/metadata; drives quantization + parameter auto-tuning.
- **External impl pointers (C07M0279):** HuggingFace **Mamba2**, **Forgetting Transformer**, GEMM
  libraries - the hybrid core blends transformer + Mamba2/SSM + forgetting mechanisms.
- **`AdaptiveRuntime`** = named execution engine sibling to the NexusNet network; cross-platform
  (DirectX/Metal/Vulkan detection), no-GPU/CPU-first absolute requirement, multiple output package
  formats. North-star framing: NexusNet = the standard "thinking layer" for all AI (like HTTP for web).

## C08 - AI Architecture Research (OpenMythos / Recurrent-Depth assimilation, 2026-04)
Net-new vs prior docs - the most detailed recurrent-reasoning engineering spec in the canon:
- **NexusNet Latent Recurrence Engine** = assimilated recurrent-depth-transformer pattern:
  **Prelude -> looped Recurrent Block -> Coda** (shared-weight latent recurrence decouples reasoning
  depth from parameter count -> variable-depth reasoning). OpenMythos is a DESIGN REFERENCE ONLY,
  MIT, not a dependency (Decision 001).
- **Named modules (the recurrent cognition lane):** `ReasoningBudget`, `RecurrenceTrace`,
  `StableInputInjector` (LTI-stable input injection each loop so the anchor input doesn't drift),
  `LoopIndexEncoder` (sinusoidal OR learned loop embeddings OR LoRA - undecided), `DepthWiseAdapter`
  (per-loop LoRA), `AdaptiveHalter` (ACT halting / halt-probability per loop), `StreamingRecurrentCache`,
  `AttentionBackend`, `ExpertRouterTelemetry`, `LatentRecurrenceController`.
- **Locked decisions:** 002 recurrence is an OPTIONAL cognition lane (not mandatory on every pass);
  **003 GQA first, MLA second** (attention backend rollout order - corrects my "MLA first" guess);
  004 ACT requires custom streaming cache semantics; 005 trace everything.
- **CRITICAL systems insight (C08M0176):** OpenMythos only short-circuits ACT early when KV-cache is
  None; with caching it runs every loop -> **ACT savings are lost during cached decode.** NexusNet
  must design cache semantics that PRESERVE halting savings during generation (Policy A full loop-slot
  cache, B active-mask, C recurrent-state-separate-from-KV, D prefill-deep/decode-shallow). This is
  where NexusNet should technically outperform the reference, not copy it.
- **Forward loop (C08M0208 implementation sketch):** init ACT state; per loop: add loop-embedding/
  depth-adapter -> run recurrent block -> stable injection w/ encoded anchor -> compute halt prob ->
  collect trace -> break only if cache policy allows; return ACT-weighted hidden state + trace.
- **Training stages (Stage 0-4):** no-training -> synthetic -> adapter tuning -> supervised instruction
  -> runtime optimization. First training path is adapter/refiner, NOT full pretraining. "Overthinking
  test" eval category (does it loop too long?). Integration strategies: A pure wrapper, B retrofit
  selected layers into recursive block, C train a NexusNet-native small RDT from scratch.
- **Assimilation discipline reaffirmed (C08M0006):** assimilate IDEAS not hype; do NOT canonize
  unverified claims (the "770M RDT matches 1.3B" claim and "LTI injection from parquet paper" were
  explicitly NOT canonized for lack of primary source); keep NexusNet's own AO/Swarm naming; reject
  marketing-tool features (Higgsfield/Seedance) from the core brain. Uses ADRs (decision records).

## C09 - Project Chat Analysis (the consolidation + first real code seam, 2026-04-23)
Net-new vs prior docs:
- **15 canonical decisions (C09M0075, 5.1-5.16)** - the authoritative locked set: 5.1 brain-first;
  5.2 neural replacement not orchestration; 5.3 Mixtral+DevStral+NexusNet near-term fusion; 5.4
  refined 4-stage training; 5.5 Expert-Router Alignment BEFORE arbitrary family swaps; 5.6 main brain
  + Mini-NexusNet/expert + Cortex + Neural Bus; 5.7 config-driven Multi-Plane MemoryNode; 5.8 RND
  mandatory; 5.9 Federated mandatory BUT global patches require review; 5.10 teachers replaced when
  surpassed; 5.11 CritiqueAO is arbiter; 5.12 **EvalsAO is EXTERNAL**; 5.13 Safe Mode + governance
  non-negotiable; 5.14 hardware-aware runtime required; 5.15 1M-token MINIMUM; 5.16 external systems
  assimilated not allowed to replace NexusNet.
- **10 Decision Records (DR-001..010)** mirror the above as ADRs (DR-007 AOs = executive cognition;
  DR-010 r22 is a baseline not final proof).
- **6 canonical conflicts reconciled (C09M0075 sec 9) - net-new:** (1) expert roster differs across
  packets [why the count wobbles between 19 and other numbers]; (2) memory plane counts differ
  [8 vs 11 - resolved to config-driven planes.yaml]; (3) NexusNet vs Nexus naming; (4) MCP/tooling vs
  neural-core identity [neural-core wins]; (5) r22 code vs canonical ambition; (6) external research
  candidates vs implemented components. These are the known internal inconsistencies to watch.
- **The first REAL brain-core seam was implemented (C09M0096/0132) by Codex against the live repo:**
  named real files: `nexusnet/core/nexusnet_core.py` (**`NexusNetCore.wake()`** lifecycle),
  `nexusnet/core/execution_trace.py`, `nexusnet/runtime/adaptive_system_profiler.py`,
  `nexusnet/memory/planes.py`, `nexusnet/memory/memory_node.py`, `nexusnet/core/compatibility_planner.py`,
  `nexusnet/distillation/refinery.py`, `nexus/models/runtime_planner.py`, `nexus/operator/kernel.py`.
  Seam = `NexusNetCore.wake()` -> HardwareScanner -> AdaptiveSystemProfiler -> attach_base_model ->
  execution-trace logging -> ExpertAdapter -> router->expert->router shape validation -> config MemoryNode.
- **Native-takeover provenance gate (ENFORCED, C09M0132):** native takeover eligible only when
  `product_evidence==true` AND `attachment_mode=="product"` AND `compatibility_plan_id` exists AND
  `compatibility_status in {COMPATIBLE, ADAPTER_REQUIRED}` AND lineage not mixed -> else shadow/blocked,
  promotion forced to shadow, runtime clamps to teacher fallback. Distillation export makes blocked
  takeover explicit (can't launder non-product evidence). (Confirms my addendum B from full text.)
- **6 workstreams (priority order):** (1) brain-first execution seam, (2) Expert-Router Alignment,
  (3) Mixtral+Devstral+NexusNet fusion, (4) Multi-Plane MemoryNode operationalization, (5)
  hardware-aware core execution, (6) traceability/docs/tests.
- **Absolute product rule:** external systems (FARA, DeepEyes, LFM2, Qwen, MCP) are ASSIMILATED, never
  allowed to replace the NexusNet core. `compatibility_planner.py` carries the compatibility plan that
  the provenance gate checks.

## C10 - NexusNet Temporal AI Review (temporal layer, 2025-08)
Net-new vs prior docs:
- **Temporal layer = real planned package `nexusnet/temporal/`** (modules: `schemas.py`,
  `normalize_time.py`, `atomic_extractor.py`, `validator.py`, `entity_resolution.py`, `tkg.py`,
  `retriever.py`, `scoring.py`, `evaluators.py`) + `router/router_expert.py`, `core/ebt_energy.py`,
  `config/rag.yaml`. (These temporal modules already EXIST in the live repo.)
- **Temporal fact = core data unit:** subject-predicate-object + provenance + **validity window**
  (valid-at time) + confidence; entity resolution/canonicalization (fuzzy match >90 -> canon_id)
  BEFORE storage to avoid graph bloat. Backend = **Graphiti** TKG (Neo4j path optional).
- **Time-scoped retrieval + EBT scoring:** retrieval returns edges valid at query time; **score blend
  = semantic + freshness + provenance + consistency**; integrated with Router Expert via EBT energy
  (`core/ebt_energy.py`, lower energy = better, weights learnable via Meta-Reasoner / per-domain).
- **Token budget:** ~5% allocated to temporal headers (experiment higher). Safe Mode throttles
  temporal ingestion/re-indexing. Dreamer/Critique extended to temporal counterfactuals across time
  slices. EBT confirmed plugged into Router Expert + MemAgent + Critique (C10M0034).

## C11 - NexusNet diagram improvements
Net-new vs prior docs:
- **EBT = "Energy-Based Transformer" full spelling locked on the main diagram** (C11M0006).
- **Layered EBT (C11M0003):** EBT is NOT only in the Meta Reasoner - it's embedded into various
  expert capsules as needed to optimize them at runtime; must be a "layered EBT architecture that
  refines decisions dynamically, not statically." EBT integration approved for BOTH core AND capsules
  (C11M0018). Hardware/Software experts have a feedback loop with the Core for real-time adaptive
  optimization tied to the EBT system.

## C12 - Project review request / MASTER BLUEPRINT (THE definitive build chapter, 2025-08)
Net-new vs prior docs - the authoritative roster + core internals + teacher design:
- **THE 19 Expert Capsules (C12M0027, authoritative roster):** 1 Vision, 2 Auditory, 3 Language
  (Linguist), 4 Knowledge-Retrieval (Librarian), 5 Mathematician, 6 Coder, 7 Scientist, 8 Engineer,
  9 Medical-Doctor, 10 Legal-Advisor, 11 Financial-Analyst, 12 Strategist, 13 Simulator
  (World-Modeler), 14 Robotics&Control, 15 Creative-Artist, 16 Psychologist (Emotional-Intelligence),
  17 Verifier (Truth-Auditor), 18 Ethicist (Ethical-Guardian), 19 Guardian (Safety&Compliance).
  (Note: this is the DOMAIN roster; the realization.py DEFAULT_EXPERT_HIVE_ROSTER in code is a
  different cognitive-role set - a known roster conflict per C09 conflict #1.)
- **Each capsule = its own neural subnetwork** (input->hidden->output, unique per-layer functions),
  not a prompt persona (C12M0040). Capsule communication via Core-routed **packed-message protocol**
  (Core packs data -> sends to capsule -> capsule unpacks/processes -> sends back).
- **Master Blueprint Section 1 core internals (C12M0042/0044):** Central Neural Core pipeline =
  Input Normalize & Embed -> **EBT Routing Layer (`EnergyBasedTransformer`, energy-based routing)** ->
  **Safe Mode Checks** -> **Meta Arbitration Logic Layer (`Meta Rerouter`)** -> Capsule Output Scores
  -> Output Routing. Control subsystems: **`ThermalScalingUnit`**, **`VRAMConstraintManager`**,
  **`Recursive Dreamer Gate`**. Token-Budget Pathway + Capsule Activation Flow are first-class.
- **Ivy-League teacher design (C12M0177/0242, locked):** every Expert Capsule MUST have a teacher pool
  with **4 roles: Coach, Critic, Socratic, Referee** ("best ENSEMBLE per role," NOT one-teacher-per-role;
  4th slot may be left _open_). Teachers carry **capability tags** the distiller + router use during
  training. Bootstrapping = multi-teacher multi-stage knowledge distillation; the capsule (student)
  learns to mimic the ensemble, then is pushed BEYOND teachers via recursive dreaming + consequence
  feedback + federated replay + meta-governed eval; teachers retired when surpassed.
  Section 5 = "Ivy League Bootstrapping & Teacher Lineage"; the user-provided per-capsule mentor table
  is the canonical approved mapping. UNRESOLVED: licensing/compliance of external teacher models;
  generic teacher IDs vs the approved real mapping (conflict).
- **Operator method, hard-confirmed:** C12 is where the operator most forcefully demanded NO detail
  omitted - every section AND subsection (1.2.1, 1.2.2, ...) must carry full description + code snippet
  + visual diagram; "audit what you missed" after every pass; build in dependency order. This is hard
  canon for how the spec/build must be produced (full-fidelity, audited, ordered).
- **Whitepaper framing (C12M0027):** dual hybrid technical-whitepaper + internal-blueprint, deliverable
  to investors AND engineers; "this is the Neural Network only... with the goal of it learning enough
  to develop an AI model" (C12M0007) - reaffirms brain-not-model, grows-into-model.

## C13 - MCP integration (dual-path tool invocation, 2025-11)
Net-new vs prior docs:
- **Section 2 Routing & Invocation = DUAL PATH (locked direction):** traditional MCP tool-call (Path B,
  simple/stable/low-data/low-risk) vs **code-execution-via-MCP** (Path A, agents run code; ~68-98%
  token savings on heavy tool-def/large-result workloads). Chosen per request by the **Tool Invocation
  Manager (TIM)** in the Core Router using inputs `data_size, tool_count, expected_result_size,
  token_cost_estimate, complexity, reliability_risk`.
- **Mandatory Sandbox & Monitoring Layer** for code-execution: secure auditable sandbox, execution
  logs, **safe-mode fallback when code fails/malicious, context rollback**; + a Metrics & Feedback
  submodule in the Core Router (token/cost/latency per capsule). `Code Generation Validator` component.
- **Token budget split referenced as 50/30/15 (+5% overflow)** (not finally settled - flagged open).
- Unresolved: exact per-capsule invocation-path assignment across the 19 capsules.

## C14 - Improving NexusNet with data (LeJEPA + circuit_sparsity -> Dreaming v2, 2025-11)
[Full detail already captured in CANON_DEEP_DETAIL_ADDENDUM section C.] Net-new confirmations:
- Dreaming v2 = JEPA world-model sidecar (SIGReg isotropic-Gaussian latent) + sparse-circuit/SAE
  introspection wrapped around the existing Dreamer; CritiqueAO veto; `circuits_risk_score`;
  DreamAdapters on 1-2 low-risk capsules; observe-only-first; `legacy_dream_cycle` preserved;
  additive-not-destructive; review-before-implement (C14M0018). `WorldModelJEPA`, `DreamAdapters`,
  `observe-only mode` are named components introduced here.

## C15 - DeepEyesV2 review (agentic vision tool-use, 2025-11)
Net-new vs prior docs:
- **Agentic Tool Invocation Loop** assimilated from DeepEyesV2: vision-grounded mid-reasoning tool use
  (the model decides which tool / visual operation to invoke during reasoning, observes result, loops).
- Owned by a **Toolsmith** capsule (tool-invocation ownership) working with **Vision** capsule +
  **Meta-Reasoner** + **MemoryAgent** + the Recursive Dream->Critique loop. (Toolsmith ownership of
  tool invocation flagged NOT final - overlaps TIM from C13.)
- Treated as direction-level assimilation; detailed 16-section integration mapping is suggestion, not
  locked. Resource feasibility unvalidated.

## C16 - Review AI Memory Features (episodic + semantic continuous learning, 2025-11)
Net-new vs prior docs:
- Assimilated the episodic/semantic memory-agent pattern: **episodic experience buffer** (recent
  interactions) + **semantic pattern store** (consolidated long-term) feeding continuous learning for
  long-term autonomy. Maps onto the MemoryNode planes + Hopfield fast-recall + slow-semantic store
  (Complementary Learning Systems already in C04). "Update full blueprint" approved (C16M0013).

## C17-C30 - External-source assimilation chats (net-new components only)
Each followed "review external source -> assimilate as NexusNet-native, additive, reviewed-first".
Named components added to canon:
- **C17:** meta/workflow only (cross-chat access limits, audit workflow, continuity-packet + Canonical-
  Decision-Memo formats as canon process artifacts). No architecture.
- **C18 Annotation Toolkit:** `NexusNet Annotation Toolkit (NNAT)` + `Annotation Validator (NNAV)` +
  NNAT CLI + code-generation-from-annotated-diagrams; **Meta Reasoner becomes annotation-aware**.
- **C19 LLM-Council:** `CouncilOrchestrator` (3-stage council, kept SEPARATE from core), `CouncilSession`/
  `Council Log`, `LibrarianModelAgent`, VisualOps `Council View`; offline vs online mode preserved.
  (Multi-model deliberation/debate/consensus mechanism.)
- **C20 Microsoft FARA:** `Fara Computer-Use Capsule`/`Fara-CUE`, `FaraGUIExecutor`, `GUIBackend`,
  `FaraTrajectory`. Computer-use/GUI-control lane; assimilated not replacing the brain.
- **C21 Copilot CLI:** patterns folded into Master Blueprint Section 17 (CLI/code-search/image/persona).
- **C22 packaging:** the r21->r22 GITREADY full-zip packaging run (no stubs/TODOs; first-run download
  scripts; core/experts/memory/RAG/QES/dreaming/federated/installers/tests/docs/CI/bootstrap).
- **C23 Agent0:** `CurriculumArchitectCapsule` + `CurriculumRewardEngine` + `Executor Capsule Feedback
  (ECF)` + Self-Evaluating Benchmarks - DATA-FREE curriculum CO-EVOLUTION (challenger generates tasks,
  solver solves, both co-evolve). NexusNet stays broader than Agent0.
- **C24 MIT PaTH Attention:** evaluated as a RoPE alternative for Router/Coder/Strategist/Memory-Weaver;
  UNRESOLVED whether PaTH/PaTH-FoX beats RoPE on NexusNet workloads (compute/latency/16GB/federated/EBT).
- **C27 Nemotron-Elastic-12B:** `ElasticProfileManager` + `RouterPolicy` - one model -> 6B/9B/12B
  variants without extra training; elastic profiles per hardware class. Not a permanent dependency.
- **C28 Bloom (Anthropic):** **`EvalsAO`** = the EXTERNAL behavioral evaluator (NOT self-grading),
  connected to Dream->Critique->Consequence, gates promotion. Confirms C09 5.12 + addendum H.
- **C30 Flash-DMD:** `Flash-DMD Vision Subsystem (FDVS)` (`FlashDMDCore`, `FlashDMDConfig`) - fast
  diffusion/distillation vision generation subsystem.
- **C25 Agentic AI alliance:** reviewed agent-interop protocols for selective assimilation (protocol-
  trust lane); no single binding component locked.

## C26 - Project Deep Dive Spec (Formal Spec v1.0/1.1/1.2 + Control&Governance Addendum)
Net-new concrete protocols (the WHAT was in operator-intent doc; these are the buildable rules):
- **Teacher Replacement Protocol (TRP)** - hard gate: student must MATCH-OR-IMPROVE teacher on
  **worst-case / tail-risk** outcomes; **catastrophic error rate must be <= teacher** (often zero-
  tolerance); if **safety dominance fails -> replacement BLOCKED**. Performance-triggered (not time).
  **Recursive Teacher Succession** (student becomes next teacher). Needs Teacher Registry + Scorecard.
- **AO Conflict Resolution & Arbitration Protocol**: Decision Classes; deterministic flow (RouterAO
  gathers proposals/risks/constraints -> CritiqueAO scores correctness/risk/regressions -> high-stakes
  require SecurityAO+CritiqueAO -> Operator final authority for deadlocks, must log); Forced "Stop".
- **AO Lifecycle Management**: AO Registry contract (must publish `upgrade_constraints` = "what it must
  never break", risk + confidence), Versioning rules, Deprecation rules; **AO Composition** (AOs call AOs).
- **Dream Scheduler**: dream budget types, hard default limits, `dream_priority_queue` (must exist),
  priority rules - resource-safety throttling on dreaming.
- **"Outperform" definition** (anti-metric-gaming): canonical Scorecard Dimensions + Anti-Gaming Controls.
- **Core Objective Store (immutable-by-default)** + **Drift Detection** (intent stability) + **Rollback
  & Recovery** (surviving bad self-changes).
- **Three-Tier Recursive Dreaming**: Tier A Expert (micro) / Tier B AO (meso) / Tier C Core (macro) +
  recursion rule + **Dream Artifact Model**. (AO-tier dreaming was the big earlier omission.)
- Config files locked: `config.yaml`, `models.yaml`, `persona.yaml`, `features.json`; per-task
  replayable `pipeline_plan.json`; Postgres stores; tools via `/tools/*/manifest.json`.
- Rejected in-chapter: **n8n (entirely)**, Pocketpal-as-integration, Ollama-only. Runtime/model
  agnosticism is canon (Model & Runtime Abstraction layer).

## C29 - Generate NexusNet blueprint (16-section MVLM Master Blueprint, 2025-11-24)
NET-NEW - an EARLIER 19-capsule taxonomy + concrete formulas, predating the C12 list:
- **C29's 19 capsules** (different grouping than C12): Sensory Hub (5: Vision, Audio, Video,
  Environment/Sensor, OCR/Text-Extraction); Cognitive Hub (7: Linguist, Coder, Mathematician, Reasoner,
  Planner, Knowledge, Memory-Interface); Reasoning Hub (7: Strategist, Critique, Toolsmith, Safety,
  Consequence, Dreamer, Meta-Reasoner). [C12 (later) is the canonical 19; C29 is a prior variant.]
- **5 capsule transport formats with role binding**: MessagePack (real-time inter-capsule nervous
  system), Cap'n Proto (zero-copy VRAM<->RAM streaming), FlatBuffers (GPU memory-mapped), Protocol
  Buffers (durable storage), JSON (debug-only). Transport-selection logic.
- **EBT energy function (explicit)**: E = f(prompt)+f(capsule)+f(hardware)+f(safety) - f(reputation);
  quadratic energy surface E(x)=x^T W x; sparse **activation mask M_i = 1 if E_i < T else 0**.
- **Six routing inputs**: Intent Vector, Capsule Relevance Vector, **Capsule Reputation Score**,
  Memory-Plane Suggestions, Hardware Budget, Safety&Ethical Vector. + **Capsule Reputation System**.
- **Capsule Cross-Attention Fusion (CCAF)** core integration layer.
- **3-plane memory here** (Episodic/Semantic/Temporal; Temporal = time-stamped causal graph) - simpler
  ancestor of the 11-plane MemoryNode.
- **12 Dream Types**: Adversarial, Reasoning, Coding, Mathematical, Multimodal, Curriculum, Failure-
  Reconstruction, Future-Scenario-Prediction, Safety, Creativity, Planning, System.
- **Dreamer Capsule internals**: Recursive Task Generator (RTG), Domain-Specific Dreamers, Stress-Test
  Scenario Network (STSN), Dream Critique Pipeline; **RND-R0** recursive feedback loop; Dream Distill.
- **5 training phases**: Ivy teacher boot -> capsule co-training -> teacher discard -> Dreamer self-
  training -> federated sync. "All teachers discarded; NexusNet becomes the teacher."
- **v2 enhancements**: **Global Working-Memory Blackboard** (shared interim results = stigmergy
  substrate), self-correcting Planner (backtrack/re-plan), context synchronization (Core emits state
  summary fed to each capsule), Meta-Reasoner coherence enforcement, **granular/tiered Safe Mode**,
  tool-output verification, persona evolution (PRM), cross-device FLP merges. Capsule streaming
  VRAM->RAM->Disk.

## C31 - NexusNet project overview (meta + early module layout)
- **Instruction Hierarchy** (canon behavior contract): System (immutable policy) > Developer/CoT
  (hidden reasoning, tool rules) > User. Policy: OCR allowed on sensitive text; **no face recognition/
  identity disclosure**; safe-completion refusals; cite web sources.
- Early proposed layout (origin, later superseded): `core/{router,dreamer,meta_reasoner,safe_mode}.py`,
  `memory/{memory_node.py,formats.py}`, `config/capsules.yaml`, `hardware/monitor.py`,
  `mcp/context_injector.py`. Chat-history-is-canon; `Zevas1993/NexusNet` repo is "way behind".

## C32 - Neural network details (the Three.js visualizer chapter)
- Interactive **HTML/Three.js hive-mind visualizer** (rejected static image): clickable Core+nodes,
  camera **click-to-zoom to NEURON level**, **bidirectional** capsule<->capsule synaptic flow,
  **load-colored synapses** (red=high-load, blue/green=standard), data-pulse particles, animated
  dream/critique loops, real-time metrics, Safe-Mode viz. Modules 1-7 (1-3 core, 4 dream/critique,
  5 deep-zoom, 6 metrics, 7 Safe-Mode). **SmallThinker** = the named visual-detail reference standard.
- Explicit: the visualizer should EVOLVE into a real runtime monitoring dashboard (= control-panel goal).

## C33 - Audit nexusnet chats (MVLM v3 diagram + teacher mapping)
- Net-new core-diagram components (MVLM v3): **Input Router, Modality Encoders, Cross-Modal Fusion
  Layer, Metadata Layer, Capsule Fusion Node**. Capsule clustering cognitive/sensory/reasoning/
  execution/supportive. Full Ivy-League teacher->19-capsule mapping table approved here.

## C34 - LFM2 Deep Dive (LiquidAI) - net-new, concrete teacher scaffolding
- LFM2 lessons: **hybrid backbone = gated short convolutions + a few GQA blocks**; **Hardware-In-the-
  Loop Architecture Search (HIL-AS)** (measure real device latency+peak memory in the search) -> apply
  to routing + capsule scheduling (validates GQA-first Decision 003). MoE "8B total ~1.5B active";
  LFM2-VL/Audio/ColBERT/1.2B-Tool variants.
- Distillation: **tempered decoupled Top-K**; **length-normalized preference optimization** (kills
  tool-call verbosity); **distill behaviors not just outputs**; curriculum (difficulty-ordered) data;
  SFT -> length-norm preference opt -> model merging.
- **Teacher-routing scaffolding (concrete)**: `teacher_registry.yaml` (TeacherProfile: id/provider/
  model_ref/modalities/context_limit/strengths/approved_domains/trust-lanes), `teacher_policy.yaml`
  (selection+weighting+arbitration), training-trace schema (teacher_provenance + arbitration_metadata
  + constraints_locked + critique_notes), `select_teachers()`/`compute_weights()` (clamped+renorm),
  `pipeline_plan.json` hooks.
- **Task taxonomy for routing**: Domain / Budget Class / Output Form / **Risk Tier**. Three-role
  Teacher Council (Domain Professor + Critique + specialist). **Critique Expert = arbiter/judge/safety
  gate** ("Critique is the immune system"). Guardrails: block over-minimization, HIGH-risk dual-pass,
  never compress safety warnings in HIGH risk. New capsule surfaced: **Memory Weaver**.

## C35 - Project Breakdown Request (the most complete component inventory in canon)
- **29 confirmed core components** (s6.1-6.29): Multimodal Encoders; **Tensor Network Compression**;
  **Quantum-Inspired Embeddings**; Dual-Track Attention&Fusion; Recursive Neural Dreaming; Neural DNA;
  **Fractal Compression**; **Neural Immune System**; **Selective Memory Decay**; Neural Sleep;
  **Meta-Reflection**; **Adaptive Creativity**; Swarm Intelligence; Dynamic Quantization; Adaptive
  Runtime Profiler; Explainability&Interpretability; Privacy&Federated Learning; **MLOps&Versioning**;
  **Plugin Ecosystem**; Human-AI Collaboration; Governance&Compliance; **Energy Manager**; **Formal
  Verification**; Benchmark Suite; **Plugin Sandbox**; **WASM Inference**; **Developer&Governance SDK**;
  **Multi-Agent Simulation**; **Accessibility&Localization**. (Bold = net-new names.)
- **9 confirmed major Decisions**: (1) brain-first; (2) `attach_base_model()` = canonical ingestion
  seam; (3) main local chat + stateful local API = high-priority parity; (4) ephemeral paths weaker;
  (5) shared KV/prefix reuse not yet a production guarantee; (6) tool transcripts must stay structured;
  (7) Expert-Router Alignment required before broad family swapping; (8) memory planes config-driven;
  **(9) NO second visualizer or runtime control plane** (= single canonical control-panel rule).
- **6 core-pivot workstreams (Apr-15 packet)**: WS1 Brain-first execution seam; WS2 Expert-Router
  Alignment; WS3 Mixtral+Devstral+NexusNet fusion; WS4 Multi-Plane MemoryNode operationalization;
  WS5 Hardware-aware core execution; WS6 Core traceability/docs/tests.
- Files: `rnd_loop.py`, `meta_learner.adapt_to_task()` (MAML), `task_sampler.py`, `profiler.py` (brain
  wakeup <1s), `config/plugins.yaml`.

## C36 - AI Architecture Visualization (the "Assistant Orchestrators Hive" canon correction)
- **Architectural Correction (now canon): NexusNet is NOT a single brain - it is a distributed hive of
  brains.** New canonical **"Assistant Orchestrators (AO) Hive"** layer: each Orchestrator contains its
  OWN mini-NexusNet brain; Experts = deep specialization network with hierarchy (Orchestrator -> Expert
  -> sub-expert); plus emergent **Shared Hive Mind** layer. Confirms fractal nested-brain hierarchy +
  recursive-dreaming AO. Repo asset `assets/nexusnet-architecture.png` + `docs/ARCHITECTURE.md`.

## C37 - Codex Project Prompt (THE bridge: canon -> the actual nexusnet/ codebase)
This is where the project moved from chats into real code (Apr 11-15 2026). NET-NEW and structural:
- Founding intent (C37M0004): a Codex prompt so it can "start running it so it can start generating
  its own model and improving itself through usage." Framing: **three connected rings**; **six
  canonical pillars**; rule "**every self-improvement mechanism must be reversible**".
- Real core seam landed: `nexusnet/core/brain.py` replaces `model.generate()` with
  `nexus_brain.generate()`; `attach_base_model()`; RND & Adapt; self-optimization loop.
- **Promotion gates operational** (`nexusnet/promotions/service.py` + `nexus/storage.py`): runtime-
  profile, retrieval-policy, federated-update, native-takeover candidates persist as first-class
  candidate/evaluation/decision records with **rollback refs**; `nexusnet/evals/service.py` EvalsAO
  runs candidate-specific EXTERNAL evals; `nexus/operator/kernel.py` records the runtime decision.
- **Teacher canon SPLIT** (real files): `teacher_registry_historical.yaml` (best-ensemble-per-role,
  preserved) vs `teacher_registry_v2026_live.yaml` (primary/secondary map, live default);
  `expert_training_regimens.yaml`, `teacher_routing_policy.yaml`; `schema_versions.py`+`migrations.py`
  (record discipline); trend governance (`trend_thresholds/scorecards/trends.py`).
- **Assimilation lanes implemented (bounded, additive, run-logged in docs/autonomous/)**: Goose/ACP
  (`goose_lane.yaml`, recipes/runbooks, ACP provider compat, adversary review; recommendation: pause
  Goose, reopen only for a real ACP provider); OpenJarvis/OBLITERATUS (local-first runtime init/doctor/
  preset, skills catalog, quarantined research-only interpretability/red-team lane); AITune (auto-find
  fastest inference backend, skip-safe + --simulate); TriAttention (KV-cache compression matches full
  attn at 2.5x throughput); cross-encoder reranking RAG; MiniMax-M2 self-evolving agent.
- **2026 ML research assimilated**: DeepSeek-V2 MLA (KV cache -93.3%, +5.76x throughput) / V2-Lite
  16B-total-2.4B-active on single 40GB / V3 MLA+MoE 37B-active+FP8; FlashInfer+FlashAttention kernel
  stack; TorchAO; NVIDIA ModelOpt. (Grounds the math-research doc + Decision-003 GQA/MLA choice.)
- **Core pivot evidence bridge**: brain path surfaces teacher-evidence bundles, dream episodes,
  distillation lineage, native-takeover promotion refs; **`promotion_linkage`** first-class artifact;
  execution modes shadow / live-planner with explicit disagreement capture; **`hold_for_alignment`**
  behavior gate; `proposed_execution_mode` vs effective `execution_mode`; post-runtime
  `rollback_to_teacher`. (This is exactly the production-spine/promotion-tribunal machinery in repo.)
- **Honest-source correction (C37M0099/0114)**: assistant admitted it could NOT read project-internal
  chat history; **chat-history-is-canon; flag any code/doc mismatch**. The 19-expert roster + AO
  hierarchy were NOT verifiable-as-locked at that point; grounded expert concepts recoverable were
  Dreamer, **Memory Weaver**, **EpisodicMemoryExpert**, **SemanticMemoryExpert**. **AO = "Assistant
  Orchestrator"** (C37M0191). Codex was told to run long/autonomous to complete larger chunks per pass.

## C38 - Research R-Zero integration (+ the r1->r22 packaging saga)
- **R-Zero**: autonomous framework that generates its OWN training data from scratch (Challenger
  generates tasks <-> Solver solves, co-evolve). vs RND: similar but **R-Zero IMPROVES RND** ->
  approved hybrid **"RND-R0"** (Recursive Neural Dreaming + R-Zero); self-curriculum without external
  datasets/human labels; "Dynamic Nexus" self-growth of experts.
- **Temporal memory built here**: **Graphiti = default TKG backend** (Neo4j + Senzing-style); atomic
  facts + provenance + validity windows + temporal knowledge graph. This chat is also where the 11
  MemoryNode planes got fleshed (social/imaginal/metacognitive/procedural/emotional/predictive +
  hypergraph all high-frequency here).
- **Quantization Evolution (operator-locked)**: NexusNet must **create its OWN quantization method**
  better than the best stack, AFTER a monitoring period (data speed / hardware usage / capability
  retention); must also understand+tune inference software (vLLM/Ollama/LM Studio) by reviewing how it
  works; **all updates tested in a virtual sandbox first**. $0-cost-on-startup mandate.
- **3D/4D per-expert hive-mind knowledge graph** - RAG schemas are **generated by the RAG expert/agent
  (not the user)**, intertwined with each expert's mini-brain. Hybrid RAG stack: dense + BM25 + ColBERT
  late-interaction + RRF + cross-encoder rerank + AIS verifier + temporal scoping + agentic graph
  controller. **TeacherGate** (OpenRouter/Requesty). RL libs staged (TRL, Verl+RAGEN, NeMo-RL/ROLL).
- Teacher research expanded (Qwen3, Grok-2, Nemotron tiny, Moonvalley, Veo3); free-vs-paid + best
  low-loss-quant columns. Independence metrics: "dependent wrapper -> independent cognitive engine."
- The r1->r22 GITREADY-FULL single-push packaging evolution (no stubs; first-run model-download
  scripts; everything-but-models bundled). r22 = the packaging baseline referenced elsewhere (C22).

## C39 - Project status overview (the wrapper build + continuous-assimilation vision)
- **CONTINUOUS Ivy-League assimilation (C39M0238 - key operator vision)**: NexusNet wraps local + API
  models; DURING usage it learns from the wrapped models - pulls/copies/assimilates their data/
  knowledge/capabilities - **packages it into the correct expert node and TAGS it with provenance
  (source model)**; once a threshold of models is assimilated the expert trains. **Ivy-League training
  becomes a CONSTANT/continuous feature, not one-time.** Alert/replace threshold = the current top-
  rated model for that expert's domain (per LLM leaderboards). (= the federated/assimilation loop.)
- Net-new named components: **Consequence Memory (negative-experience bank)**; **Knowledge Engine
  (offline RAG)**; **RAG-Enhanced Critique**; Model Registry schema; clustered budget lanes; precision/
  cache matrix; Safe-Mode learning loop. **Graph-R1** (Agentic GraphRAG + RL, multi-turn) folded into
  the hybrid RAG (goal: instant memory access w/o context overload or hallucination).
- **Dual-runtime co-execution**: **LM Studio = CPU-only models, vLLM = GPU models, running
  simultaneously and communicating THROUGH NexusNet** (deeper data gathering). Build own llama.cpp
  tuned by hardware monitor; startup hardware scan installs deps + picks quant/models; separate
  **CPU-advisor + GPU-advisor** that re-tune as hardware upgrades; adapt H100/EPYC high-end <-> 16GB
  low-end; internet check for current model sizes.
- Wrapper-first decision (C39M0181/0186/0023): start as a wrapper to develop bootstrapping/assimilation,
  finish the wrapper, THEN grow into the actual Nexus AI model. "NexusNet is a Neural Network that
  develops into an AI model forming Nexus AI." Federated learning day-one + mandatory (personal-data
  sharing opt-in); wrapper self-updating/self-healing, initiates its own sandbox testing.
- Real dev box reconfirmed: $0 budget, RTX 5070 Ti 16GB / i7-13700K / 32GB DDR5 / Win11 + WSL. API
  providers OpenRouter + Requesty; install-time API-key dialog + paid-credit toggle. Installers: 2
  Windows + manual clone (all 3 on GitHub); single NexusNet chat UI merges GPU+CPU outputs; model
  selector per device; previous-chat memory. v0.9/v0.95 blueprint; external Claude-Opus-4.1 review.

## Coverage complete
All 39 Conversation Source Chapters (C01-C39) have now been read sequentially with net-new findings
logged. The full canon book (lines 17056-41524) is covered. Pre-chapter front-matter (Decision/
Artifact/Aspect indexes, lines 1-17055) was already mined in the prior research docs.
