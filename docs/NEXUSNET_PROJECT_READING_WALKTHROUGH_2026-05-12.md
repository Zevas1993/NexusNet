# NexusNet Project Reading Walkthrough - 2026-05-12

Status: audit guide for patent, architecture, and repo-hygiene review.

Purpose: give a new reviewer a reliable reading path through NexusNet without forcing them to open every raw transcript, every implementation file, or every generated runtime artifact first.

This document is a map. It does not replace the patent packet, the canon book, or the live code. It tells a reviewer what to read, why to read it, and when to stop and verify against the source files.

## Reader Roles

Use this order depending on the reviewer role.

| Reader | Main goal | Primary path |
| --- | --- | --- |
| Patent helper | Understand the invention, support chart, claims, and filing packet | Path A, then Path B, then Path C |
| Technical architect | Understand the live architecture and implementation maturity | Path B, then Path D, then Path E |
| Repo cleanup lead | Fix Git, staging, public/private boundaries, and folder organization | Path F, then Path B, then Path D |
| Implementation agent | Continue building NexusNet safely | Path B, then Path D, then Path G |

## Global Rules Before Reading

1. Treat `NexusNet` as the brain/core and `Nexus` as the host/platform shell.
2. Treat `Hive Mind` as formal architecture terminology, not branding flavor.
3. Treat `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` as the exhaustive source map, not as a concise onboarding document.
4. Treat research candidates as candidate material until they pass registry, license, privacy, runtime, eval, and governance gates.
5. Treat the current working tree as dirty and mixed. Do not mass-stage, move, delete, or rewrite files without the Git reorganization plan.
6. Keep implemented features, candidate designs, patent embodiments, and future vision separated.

## Path A - Patent Packet First

Start here when the goal is patent application support.

1. `patent/nexusnet_micro_entity_packet_2026-05-01/00_USE_AND_LIMITS.md`
   - Establishes legal caution and what must be personally verified.
   - Important because the packet is a drafting aid, not a patentability opinion.

2. `patent/nexusnet_micro_entity_packet_2026-05-01/README_PRO_SE_PACKET.md`
   - Gives the packet purpose, working title, and official USPTO source links.
   - Current packet title: `Hive Mind Harness for Artificial Intelligence with Governed Sparse Routing`.

3. `patent/nexusnet_micro_entity_packet_2026-05-01/03_INVENTION_DISCLOSURE_RECORD.md`
   - Defines the short invention description and the inventive concepts to preserve.
   - Use this to collect inventor, ownership, disclosure, and sale information before filing.

4. `patent/nexusnet_micro_entity_packet_2026-05-01/04_NONPROVISIONAL_SPECIFICATION_DRAFT.md`
   - Read the Field, Background, Summary, Definitions, and Detailed Description.
   - This is the best patent-style description of the system.

5. `patent/nexusnet_micro_entity_packet_2026-05-01/05_CLAIMS_DRAFT.md`
   - Read independent claims 1, 15, and 23 first.
   - Then read dependent claims 2-14, 16-22, and 24-25.
   - Keep a list of any claim element that is only future vision or only partially implemented.

6. `patent/nexusnet_micro_entity_packet_2026-05-01/06_ABSTRACT_DRAFT.md`
   - Confirms the short abstract narrative.

7. `patent/nexusnet_micro_entity_packet_2026-05-01/07_DRAWING_BRIEF_DESCRIPTION_AND_REFERENCE_NUMERALS.md`
   - Maps figures to system pieces.
   - Then inspect the SVG drawings under `patent/nexusnet_micro_entity_packet_2026-05-01/drawings/`.

8. `patent/nexusnet_micro_entity_packet_2026-05-01/11_SOURCE_CANON_TO_CLAIM_SUPPORT_CHART.md`
   - This is the claim support bridge.
   - It points from claim elements to canon docs and selected implementation files.

9. `patent/nexusnet_micro_entity_packet_2026-05-01/08_PRIOR_ART_AND_DIFFERENTIATOR_WORKSHEET.md`
   - Use this before filing claims.
   - It separates common AI/RAG/agent/MoE patterns from NexusNet's asserted differentiators.

10. `patent/nexusnet_micro_entity_packet_2026-05-01/10_IDS_WORKSHEET.md`
    - Use for references that may need practitioner review for IDS handling.

11. `patent/nexusnet_micro_entity_packet_2026-05-01/09_FILING_CHECKLIST_AND_PATENT_CENTER_STEPS.md`
    - Use after the technical read is complete and the filing path is being chosen.

12. `patent/nexusnet_micro_entity_packet_2026-05-01/02_USPTO_FORM_FIELD_WORKSHEETS.md` and `letters/`
    - Use only when preparing official forms and cover materials.

## Path B - Canon In The Right Order

Read this path before arguing about what NexusNet is.

1. `README.md`
   - First-pass repo identity.
   - Locks the public opening: `# NexusNet Neural Core AI Brain`.
   - Explains the active split between `nexusnet/` and `nexus/`.

2. `docs/NEXUSNET_CANON_MATRIX.md`
   - The compact constitutional split:
     - `NexusNet` equals locked brain/core canon.
     - `AOs` equal locked assistant-orchestrator canon.
     - `Nexus` equals strong accepted host/platform direction.

3. `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
   - Do not read linearly on first pass.
   - Read:
     - `How To Read This Book`
     - `Master Table Of Contents`
     - `2026 Research Refresh Integration Addendum`
     - `Updated Canon Overlay Matrix`
     - `Control Panel Requirements Now Binding`
     - `Source Coverage`
     - `Concept Index`
     - `Decision And Canon Marker Index`
     - `Unresolved And Risk Marker Index`
   - Then search inside it for:
     - `brain-first`
     - `Hive Mind`
     - `Cortex`
     - `Neural Bus`
     - `Mini-NexusNet`
     - `multi-plane`
     - `promotion`
     - `checkpoint`
     - `sandbox`
     - `federated`

4. `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
   - Read after the complete book.
   - This is where later locked clarifications live, including neural harness doctrine, Hive Neural Substrate, self-research, sandbox promotion, NeuralBus, HiveBlackboard, checkpoint rewind, and the teacher pairing refresh.

5. `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
   - Read as a ledger of post-book candidates and canon additions.
   - Pay special attention to local-first state and cache boundaries.

6. `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
   - Read to understand how public research candidates were mapped onto NexusNet without silently replacing canon.

7. `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`
   - Read for the open-first model/runtime direction and the no-cost/local-first bias.

## Path C - Patent Claim Support Walkthrough

After Path A and Path B, verify each patent element against the source record.

1. Brain-mediated neural core service
   - Patent claim refs: 1, 14, 15, 23.
   - Read `docs/core_brain_execution.md`.
   - Inspect `nexusnet/core/brain.py`.

2. Hive node registry
   - Patent claim refs: 1, 2, 23.
   - Read `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`.
   - Inspect `nexusnet/hive/substrate.py` and `nexusnet/canon/realization.py`.

3. Neural bus and typed activations
   - Patent claim refs: 1, 3, 15, 23.
   - Read the Neural Bus and activation sections in the Hive Neural Substrate design.
   - Verify current implementation state in `nexusnet/hive/substrate.py`.

4. Cortex router and sparse expert routing
   - Patent claim refs: 1, 6, 15, 23.
   - Read `docs/expert_router_alignment.md`.
   - Inspect `nexusnet/moe/cortex/service.py` and router-alignment modules.

5. Multi-plane memory and engram layer
   - Patent claim refs: 1, 5, 15, 23.
   - Read `docs/multi_plane_memorynode.md`, `docs/compiled_knowledge_artifact_layer.md`, and `docs/SELF_IMPROVEMENT_LAYER.md`.
   - Inspect `nexusnet/memory/planes.py`, `nexusnet/memory/engram_index.py`, and `nexusnet/knowledge/compiler.py`.

6. Recurrent deliberation and exit gates
   - Patent claim refs: 1, 4, 15, 23.
   - Read the recurrent deliberation sections in the Hive Neural Substrate design and `docs/core_evidence_driven_execution.md`.
   - Inspect `nexusnet/core/execution_policy.py`, `nexusnet/core/native_execution.py`, and `nexusnet/growth/production_spine.py`.

7. Immune governance kernel
   - Patent claim refs: 1, 10, 13, 15, 23.
   - Read `docs/core_promotion_replacement_linkage.md` and policy sections in the patent packet.
   - Inspect `nexusnet/policy/kernel.py`, `nexusnet/security/`, and artifact trust modules.

8. Checkpoint and rewind ledgers
   - Patent claim refs: 1, 11, 15, 23.
   - Read the post-book addendum sections on checkpoint rewind.
   - Inspect `nexusnet/hive/substrate.py` and `nexusnet/growth/production_spine.py`.

9. Candidate assimilation, sandbox, and sidebar
   - Patent claim refs: 10, 16, 24.
   - Read `docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md`.
   - Inspect `nexusnet/growth/engine.py`, `nexusnet/growth/production_spine.py`, `nexusnet/core/self_review.py`, and `nexusnet/core/self_improvement/`.

10. VisualOps control panel
    - Patent claim refs: 7, 18.
    - Read the control panel requirements in the complete canon book.
    - Inspect `ui/control-panel/app.js`, `ui/control-panel/index.html`, and `nexusnet/canon/realization.py`.

11. Federated learning boundary
    - Patent claim refs: 12, 20, 25.
    - Read the patent specification's federated learning section and post-book addendum federation sections.
    - Inspect `nexusnet/federation/` and federation entries in `nexusnet/hive/substrate.py`.

12. Native MoE evolution path
    - Patent claim ref: 25.
    - Treat as a future growth path unless the specific feature is code-backed and tested.
    - Inspect `nexusnet/growth/production_spine.py`, `nexusnet/hive/substrate.py`, and the current tests before claiming implementation.

## Path D - Live Code Walkthrough

Read implementation files in this order.

1. Core brain path
   - `nexusnet/core/brain.py`
   - `nexusnet/core/execution_policy.py`
   - `nexusnet/core/native_execution.py`
   - `nexusnet/core/evidence_feeds.py`
   - `nexusnet/core/attach_base_model.py`

2. Host platform path
   - `nexus/api/app.py`
   - `nexus/services.py`
   - `nexus/storage.py`
   - `nexus/operator/kernel.py`
   - `nexus/runtimes/registry.py`

3. Memory and knowledge path
   - `nexusnet/memory/planes.py`
   - `nexusnet/memory/engram_index.py`
   - `nexusnet/memory/quality_ledger.py`
   - `nexusnet/knowledge/compiler.py`
   - `nexusnet/retrieval/planner.py`

4. Growth and promotion path
   - `nexusnet/growth/engine.py`
   - `nexusnet/growth/production_spine.py`
   - `nexusnet/dreaming/engine.py`
   - `nexusnet/core/self_review.py`
   - `nexusnet/core/self_improvement/`

5. Hive neural substrate path
   - `nexusnet/hive/substrate.py`
   - `nexusnet/moe/cortex/service.py`
   - `nexusnet/moe/router_alignment/service.py`
   - `nexusnet/moe/fusion/service.py`

6. Runtime and provider economy path
   - `nexusnet/runtime/inference_economy_router.py`
   - `nexusnet/runtime/model_route_policy.py`
   - `nexusnet/runtime/provider_registry.py`
   - `nexusnet/runtime/quantization/catalog.py`
   - `nexusnet/runtime/cache_ledger.py`

7. Governance, trust, security, and protocols
   - `nexusnet/policy/kernel.py`
   - `nexusnet/security/`
   - `nexusnet/protocols/`
   - `nexusnet/tools/extensions/catalog.py`

8. Operator UI surfaces
   - `ui/control-panel/app.js`
   - `ui/control-panel/index.html`
   - `ui/visualizer/app.js`
   - `nexusnet/ui_surface/surface.py`
   - `nexusnet/visuals/layout.py`

## Path E - Tests As Evidence

After reading implementation, use tests to determine what is actually supported.

Read these test files first:

- `tests/test_nexusnet_brain.py`
- `tests/test_nexusnet_core_pivot.py`
- `tests/test_nexusnet_core_execution_fusion.py`
- `tests/test_nexusnet_production_spine.py`
- `tests/test_hive_neural_substrate.py`
- `tests/test_hive_model_growth_engine.py`
- `tests/test_knowledge_artifact_compiler.py`
- `tests/test_self_improvement_layer.py`
- `tests/test_policy_kernel.py`
- `tests/test_teacher_registry.py`
- `tests/test_teacher_provenance.py`
- `tests/test_nexusnet_visualizer.py`

Interpret tests conservatively:

- A tested shadow/gated path is not the same as unbounded production autonomy.
- A scorecard surface is not the same as a live certified subsystem.
- A mocked proof or deterministic sandbox proof is evidence for architecture shape, not proof of external deployment readiness.

## Path F - Git And Repository Hygiene Walkthrough

Read the Git audit before staging or reorganizing anything:

1. `docs/NEXUSNET_GIT_REPO_AUDIT_REORGANIZATION_PLAN_2026-05-12.md`
2. `.gitignore`
3. `.gitattributes`
4. `git status --short`
5. `git diff --stat`
6. `git ls-files -o --exclude-standard`

Then classify files by destination:

- Product code: `nexusnet/`, `nexus/`, `ui/`, `config/`, `tests/`
- Canon and patent docs: selected `docs/`, `patent/`
- Research specs: `docs/assimilation/`, `docs/research/`, selected research docs
- Runtime evidence: `runtime/live-proofs/`, `runtime/pytest_collect_*.txt`
- Local-only scratch: caches, temp test roots, private capture helpers

Do not move the complete canon book or patent packet until the public/private boundary is decided.

## Path G - Current Highest-Leverage Build Context

For future implementation work, the most important live gap from the May 6 gap report is not another isolated model or another broad research pass. It is a unified developmental contract that binds existing modules:

- `DevelopmentalCortexKernel`
- `NexusBodySchema`
- `ReferenceFrameStore`
- `WorldModel`
- `CausalInterventionLab`
- `GrowthArchive`
- `PromotionTribunal`

That gap matters for patent work because it separates:

- implemented or code-backed governance/growth primitives
- candidate developmental cortex architecture
- future native model evolution

## First-Sitting Reading Plan

If a reviewer has one session, use this exact sequence:

1. `README.md`
2. `docs/NEXUSNET_CANON_MATRIX.md`
3. `patent/nexusnet_micro_entity_packet_2026-05-01/03_INVENTION_DISCLOSURE_RECORD.md`
4. `patent/nexusnet_micro_entity_packet_2026-05-01/04_NONPROVISIONAL_SPECIFICATION_DRAFT.md`
5. `patent/nexusnet_micro_entity_packet_2026-05-01/05_CLAIMS_DRAFT.md`
6. `patent/nexusnet_micro_entity_packet_2026-05-01/11_SOURCE_CANON_TO_CLAIM_SUPPORT_CHART.md`
7. `docs/core_brain_execution.md`
8. `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
9. `docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md`
10. `docs/NEXUSNET_GIT_REPO_AUDIT_REORGANIZATION_PLAN_2026-05-12.md`

Stop there and write down:

- which claim elements are implemented
- which claim elements are disclosed but not fully built
- which documents are internal-only versus shareable
- which Git changes should be staged together

## Audit Caveats

- The GitNexus index for `NexusNet` was recorded on 2026-05-06, before some untracked May 7+ work. Use GitNexus for orientation, then verify against disk.
- The working tree is dirty. Any source references in this walkthrough describe the live workspace, not a clean release tag.
- The exhaustive canon book contains historical raw export material and old sandbox-style references. Treat it as internal source material unless a fresh shareability audit says otherwise.
- The patent packet is stronger than the raw canon for sharing, but the claims still need practitioner review.
