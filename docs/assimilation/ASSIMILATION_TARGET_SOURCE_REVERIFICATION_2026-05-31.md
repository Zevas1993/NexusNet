# Assimilation Target Source Reverification - 2026-05-31

Status: source-reverification evidence packet
Scope: all NexusNet assimilation-target files inventoried from `docs/`
Primary artifacts:

- `docs/chatgpt_ingestion/assimilation_target_file_inventory_2026-05-31.txt`
- `docs/chatgpt_ingestion/assimilation_target_urls_2026-05-31.json`
- `docs/chatgpt_ingestion/assimilation_target_url_status_2026-05-31.json`
- `docs/NEXUSNET_CHATGPT_PROJECT_ASSIMILATION_TARGETS_2026-05-31.md`

## Boundary

This pass verifies current source availability and source-claim alignment. It does not promote any candidate into production, import third-party code, validate licenses for commercial redistribution, or prove local runtime performance. Promotion still requires the NexusNet ledger, source/license/security review, GitNexus impact analysis where code symbols are affected, sandbox evidence, eval evidence, rollback, and operator/governance approval.

## All-File Coverage

The pass inventoried 191 assimilation-related files and extracted 964 unique file-to-URL references across 872 unique URLs.

| Metric | Count | Meaning |
| --- | ---: | --- |
| Assimilation-related files inventoried | 191 | Files under `docs/` whose path or contents match assimilation/target source patterns. |
| Unique file-to-URL references | 964 | A URL may appear in more than one file. |
| Unique URLs checked | 872 | Current HTTP liveness/status pass. |
| Normal success | 777 | Returned HTTP 2xx/3xx in the automated pass. |
| Reachable but manual/gated | 34 | Returned 401, 403, or 429; may need browser, auth, publisher anti-bot allowance, or manual review. |
| Failed | 61 | Includes dead links, malformed copied links, localhost/dev endpoints, private ChatGPT URLs, and stale external docs. |

Do not interpret the 61 failures as 61 rejected targets. The failure set mixes stale source links, private/local endpoints, malformed extracted URLs, and some real 404s. Each target still needs file-level review before changing its candidate status.

## Source Health Findings

- `docs/openclaw_assimilation.md` has two stale OpenClaw docs URLs returning 404. The OpenClaw pattern remains usable only as a prior architecture direction until current primary docs are pinned.
- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` contains many local, private, malformed, or workstation/runtime URLs. These are canon/evidence references, not all external web targets.
- The ChatGPT 17-target synthesis has current primary sources for the new model/paper/repo targets, except canon-only clarifications that intentionally have no external source.
- The automated URL pass confirms broad source availability for the 2026-05-06 online packet, but the packet remains research-only. Source liveness is not implementation proof.
- The video assimilation packet remains documentation-only unless the local watcher evidence root is re-opened and checked. Online URL liveness cannot revalidate local video/transcript evidence by itself.

## ChatGPT 17 Target Confirmation

| ID | Target | Source status | Confirmed NexusNet posture |
| --- | --- | --- | --- |
| CGPT17-001 | Birth doctrine and creator observability | Canon/chat clarification, not an external source target. | Keep as `locked_clarification`; do not need web source, but needs ledger/canon anchoring. |
| CGPT17-002 | `FareedKhan-dev/train-llm-from-scratch` | GitHub source reachable; repo presents PyTorch scratch transformer training and MIT license. | Confirm as Scratch Apprentice Foundry pattern only. Do not copy training data or scripts without license/security/runtime review. |
| CGPT17-003 | MUSE-Autoskill / arXiv 2605.27366 | Hugging Face and arXiv paper pages reachable; claim matches skill lifecycle framing. | Confirm as SkillOps sidecar candidate: skill creation, memory, management, evaluation, and refinement. |
| CGPT17-004 | `openbmb/MiniCPM5-1B-GGUF` | Hugging Face model card reachable; Apache-2.0; 1.08B params; GGUF; 131,072 context. | Confirm as edge/local worker candidate, not core brain. |
| CGPT17-005 | HF paper 2605.27365 / LocateAnything | Hugging Face paper page reachable; model/card links point to vision-language grounding with Parallel Box Decoding and released code. | Upgrade from vague spatial lane to explicit visual grounding/localization research plugin candidate. |
| CGPT17-006 | CodeRabbit/Claude orchestration | Anthropic webinar page reachable; claim matches structured planning before coding-agent execution. | Confirm as planning preflight/governance pattern, not product dependency. |
| CGPT17-007 | `Kwai-Keye/Keye-VL-2.0-30B-A3B` | Hugging Face model card reachable; Apache-2.0; 31B params; long-video/agent claims; high resource requirements. | Confirm as conditional multimodal video-temporal teacher candidate. Keep research-only until hardware, privacy, and benchmark gates pass. |
| CGPT17-008 | EAGLE 3.1 | vLLM blog reachable; direct vLLM integration and throughput claims present. | Confirm as runtime acceleration candidate. It belongs under speculative decoding, not cognition. |
| CGPT17-009 | LiteParse v2.0 | LlamaIndex blog reachable; Rust rewrite, Node/Python/Rust/WASM package story, local/browser parsing claims present. | Confirm as ingestion/parser adapter candidate for KAC/document pipelines. |
| CGPT17-010 | AXPO / arXiv 2605.28774 | Hugging Face and arXiv paper pages reachable; paper fixes thinking prefix and resamples tool call/continuation. | Confirm as action/tool-step recovery candidate for failed agent trajectories. |
| CGPT17-011 | OSCAR / arXiv 2605.17757 | Project page and arXiv reachable; code/paper/RotationZoo links present; INT2 KV-cache claims align with chat summary. | Confirm as long-context KV-cache memory-economy candidate. Needs workload-specific correctness and privacy gates. |
| CGPT17-012 | OpenCLAW vs Hermes Agent | Hermes primary GitHub source reachable; OpenClaw docs links in local doc are stale. | Split posture: Hermes skill/memory loop is confirmed as pattern input; OpenClaw source pins need refresh before stronger claims. |
| CGPT17-013 | OpenMonoAgent.ai | Website and GitHub reachable; local-first coding agent claims present; GitHub badge indicates GNU AGPL-3.0. | Confirm as architecture/pattern candidate only. Direct code import is blocked unless AGPL compatibility is explicitly accepted. |
| CGPT17-014 | Bloom/Petri behavioral eval | `safety-research/bloom` GitHub and Anthropic Bloom article reachable; Anthropic describes Petri as complementary. | Confirm as behavioral-evaluation candidate; keep Petri/Bloom lineage separate and source-pinned. |
| CGPT17-015 | Compiled Knowledge Artifact Layer / KAC | VentureBeat article reachable; article describes Pinecone Nexus context compiler and early-access status. | Confirm KAC direction; keep vendor claims as references only and preserve local-first/vendor-independent KAC. |
| CGPT17-016 | NVIDIA Nemotron 3 Nano Omni | NVIDIA technical blog and Hugging Face model card reachable; NVIDIA Open Model Agreement applies. | Confirm as optional multimodal teacher/perception candidate, not a replacement brain. |
| CGPT17-017 | Manifest-style model router | `mnfst/manifest` GitHub reachable; MIT license; smart routing, cost tracking, fallback, local providers confirmed. | Confirm as inference-economy router pattern; existing NexusNet implementation posture remains valid. |
| CGPT17-018 | MLLM self-improvement survey / arXiv 2510.02665 | Hugging Face and arXiv reachable; abstract frames data collection, data organization, and model optimization. | Confirm as self-improvement process doctrine, not an implementation dependency. |

## Cross-File Target Updates

The following existing assimilation files now carry the updated source posture from this pass:

| File | Update |
| --- | --- |
| `docs/NEXUSNET_CHATGPT_PROJECT_ASSIMILATION_TARGETS_2026-05-31.md` | Add source-backed confirmation statuses and keep all implementation gates. |
| `docs/manifest_assimilation.md` | Manifest source is current and stronger than the earlier transcript-only status; still subordinate to NexusBrain policy. |
| `docs/research/nvidia_nemotron_3_nano_omni_assimilation.md` | Source remains current; confirm NVIDIA Open Model Agreement and optional teacher boundary. |
| `docs/compiled_knowledge_artifact_layer.md` | KAC direction is confirmed as architecture reference; Pinecone/VentureBeat claims remain vendor reference, not dependency. |
| `docs/openclaw_assimilation.md` | Downgrade source health because two pinned OpenClaw docs URLs are stale; add Hermes source as a separate pattern reference. |
| `docs/assimilation/online/2026-05-06/41-kv-cache-runtime-efficiency-spec.md` | Add OSCAR as a newly verified KV-cache candidate under research-only posture. |
| `docs/assimilation/online/2026-05-06/68-speculative-decoding-runtime-stack-spec.md` | Add EAGLE 3.1/vLLM update under research-only runtime acceleration posture. |
| `docs/assimilation/online/2026-05-06/07-parsebench-document-certification-spec.md` | Add LiteParse v2.0 as a parser adapter candidate feeding document certification and KAC. |
| `docs/assimilation/online/2026-05-06/12-open-model-runtime-ladder-spec.md` | Add MiniCPM5 and Keye-VL as newly verified model candidates with distinct runtime/teacher roles. |
| `docs/assimilation/online/2026-05-06/README.md` | Add all-file source-reverification summary. |
| `docs/assimilation/videos/2026-05-06/README.md` | Clarify that video packet needs local watcher evidence verification, not only URL liveness. |

## Confirmation Rules Going Forward

- `confirmed source` means the external source exists and matches the target identity.
- `confirmed target posture` means the NexusNet role is still coherent after source review.
- `accepted NexusNet state` still requires ledger/addendum entry plus the normal proof gates.
- Any source returning 401, 403, or 429 should be manually checked in a browser before being marked dead.
- Any source returning 404 or malformed extraction should be repaired in the source file before future automation uses it.
- AGPL, custom model agreements, and dataset-training rights must be handled as blocking legal/provenance gates, not documentation footnotes.
