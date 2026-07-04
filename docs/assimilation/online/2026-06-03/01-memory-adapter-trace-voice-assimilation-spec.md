# Memory, Adapter, Trace, And Voice Assimilation Spec

Status: candidate assimilation packet
Date added: 2026-06-03
Canon entries: `PB-2026-06-03-095` through `PB-2026-06-03-098`
Primary canon addendum: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
Primary ledger: `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`

## Source Evidence

Primary source refs:

- `https://arxiv.org/abs/2605.15156`
- `https://www.marktechpost.com/2026/05/26/memo-a-modular-framework-for-training-a-dedicated-memory-model-on-new-knowledge-without-modifying-llm-parameters/`
- `https://arxiv.org/abs/2606.02437`
- `https://huggingface.co/papers/2606.02437`
- `https://youtu.be/NGfvTlU2T5E?si=4bz8lpPk7Ex3k7_L`
- `https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/`
- `https://arxiv.org/abs/2605.30993`
- `https://huggingface.co/papers/2605.30993`
- `https://swanaigc.github.io/#/swanvoice`

Related local video-watcher evidence:

- `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-2026-06-03\YTDown_YouTube_YES-Harness-Self-optimization-w-9B-LLM-L_Media_aaViBfjnh78_001_1080p_20260603_054026\WATCH_REPORT.md`
- `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-2026-06-03\YTDown_YouTube_Unlock-Autonomous-AI-Agents-with-auth-md_Media_Dqp_b8GHLXU_001_1080p_20260603_054750\WATCH_REPORT.md`

Existing NexusNet anchors:

- `docs/compiled_knowledge_artifact_layer.md`
- `docs/SELF_IMPROVEMENT_LAYER.md`
- `nexusnet/knowledge/compiler.py`
- `nexusnet/memory/engram_index.py`
- `nexusnet/retrieval/planner.py`
- `nexusnet/agents/harnesses/ledger.py`
- `nexusnet/agents/harnesses/registry.py`
- `nexusnet/agents/pipelines/service.py`
- `nexusnet/tools/action_harness.py`
- `nexusnet/tools/permissions/service.py`
- `nexusnet/security/artifact_trust.py`
- `tests/test_engram_memory_index.py`
- `tests/test_knowledge_artifact_compiler.py`
- `tests/test_retrieval_planner.py`
- `tests/test_harness_improvement_ledger.py`
- `tests/test_agentic_pipeline_runtime.py`
- `tests/test_tool_action_harness.py`

## Assimilation Verdicts

Assimilate four separate targets with different promotion postures:

1. **Dedicated Memory Model Knowledge Lane**: candidate.
2. **Persistent Adapter State Fabric**: candidate, high priority.
3. **Trace-Optimized Secure Self-Evolving Agent Runtime**: candidate, high priority, overlaps `PB-2026-06-03-094`.
4. **Dialogue Voice Scene Alignment Lane**: research_only until consent, model/data availability, and content-accuracy gates are cleared.

None of these targets authorizes direct protected-state mutation, direct model-weight updates, direct credential storage, or bypass of existing sandbox/eval/governance gates.

## PB-2026-06-03-095 - Dedicated Memory Model Knowledge Lane

Accepted pattern:

MeMo separates a frozen executive LLM from a trainable dedicated memory model. NexusNet should assimilate the pattern as a **Knowledge Memory Model Lane** that can internalize selected project, domain, or operator-approved corpora into a small memory model, while keeping the primary reasoning model frozen.

NexusNet should not replace the existing Knowledge Artifact Compiler, retrieval planner, engram index, or provenance layer. The memory model is an additional recall substrate for stable, rights-cleared knowledge where repeated RAG is too noisy or expensive, especially when answers require cross-document synthesis.

Implementation path:

1. Add a `MemoryModelLane` design contract under the knowledge or memory subsystem before any training code.
2. Reuse `KnowledgeRequestContract`, source digests, freshness checks, and permission filters to select eligible corpora.
3. Generate reflection QA records from source chunks with fact extraction, consolidation, verification, entity surfacing, and cross-document synthesis steps.
4. Train only on rights-cleared, non-private, operator-approved corpora; compute loss over answer tokens or an equivalent supervised target.
5. Query the memory model through a bounded multi-turn protocol: grounding, entity identification, then support-seeking synthesis.
6. Store source-to-training lineage, corpus digests, memory-model revision, eval set, and rollback metadata in a project-root ledger.
7. Compare memory-model answers against KAC/RAG baselines before promotion.

Required tests:

- Memory corpus eligibility rejects private, stale, unclear-rights, or unredacted sources.
- Reflection QA generation preserves source refs and rejects unresolved pronouns or unsupported claims.
- Memory-model lane can answer through a bounded protocol without source-document retrieval at inference.
- KAC remains the fallback and source-of-citation authority.
- Model-merge or incremental update candidates stay shadow-only until eval and rollback gates pass.

Security and policy gates:

- No private files, secrets, raw prompts, raw outputs, private URLs, or unredacted local paths in training corpora.
- No training on source material without rights for the intended internal model-improvement use.
- Memory-model output cannot be treated as citation evidence unless linked back to source refs and KAC provenance.
- Any model merging or incremental memory update remains shadow-first.

## PB-2026-06-03-096 - Persistent Adapter State Fabric

Accepted pattern:

The PEFT scaling paper reframes adapters as persistent local state on top of a strong shared foundation model. NexusNet should assimilate this as a **Persistent Adapter State Fabric** for AO, expert, Mini-NexusNet, operator, task-family, and tool-habit personalization.

This target aligns directly with NexusNet's fractal Mini-NexusNet hierarchy and teacher/foundry lanes. Adapters become small governed state modules, not uncontrolled per-user fine-tunes.

Implementation path:

1. Add an adapter passport schema before runtime attachment.
2. Track adapter identity, base-model compatibility, revision, source lineage, owner, task family, eval suite, route constraints, residency, and rollback ref.
3. Add an adapter registry that can enumerate candidate adapters without loading weights by default.
4. Route adapters through shadow evaluation before any production use.
5. Bind adapter selection to existing provider registry, teacher registry, runtime decision ledger, and Control Panel replay.
6. Add a storage policy for adapter residency and eviction that does not expose raw weights in logs or federated packets.
7. Compare adapter-backed behavior against base-model and KAC/RAG baselines before promotion.

Required tests:

- Adapter passport rejects incompatible base models and missing provenance.
- Adapter load is blocked without eval proof and rollback metadata.
- Per-AO and per-expert adapter routing stays shadow-only until approval.
- Adapter registry does not store or leak raw adapter weights in ordinary ledger output.
- Rollback restores the previous adapter selection.

Security and policy gates:

- Every adapter requires source rights, privacy classification, eval deltas, rollback coverage, and owner or lane identity.
- Adapter state cannot override action policy, credential scopes, data boundaries, or governance gates.
- Adapter-derived behavior cannot federate as raw weights or private behavior traces.

## PB-2026-06-03-097 - Trace-Optimized Secure Self-Evolving Agent Runtime

Accepted pattern:

The Hermes/NemoClaw material is useful as a secure self-evolving runtime pattern: a model, a harness with skills/memory/sessions/bridges, and a policy-enforced runtime with credential brokering, network allowlists, snapshots, trace export, and learned skills that persist across rebuilds.

This target should extend `PB-2026-06-03-094`, not duplicate it. The additional lesson is that trace-to-skill and trace-to-memory self-improvement must run inside a policy-coded sandbox where credentials are brokered outside the agent and network access is enforced by runtime policy, not by prompt text.

Implementation path:

1. Extend the future `HarnessContractLedger` with runtime-policy evidence, snapshot evidence, trace refs, and learned-state refs.
2. Add a read-only trace collector that records tool calls, skill calls, arguments, decisions, policy errors, and final output refs in a redacted agent trajectory format.
3. Add a trace analyzer that proposes skill, memory, prompt, or policy candidates, but cannot write protected state directly.
4. Add a shadow optimizer lane that can produce proposed `SKILL.md`, memory note, or prompt overlay diffs with provenance and rollback refs.
5. Require sandbox policy proofs for credential brokering, network allowlist enforcement, and ETL/read-only mirror boundaries before any live deployment.
6. Add snapshot/restore verification for learned skills, memories, sessions, and schedules while excluding `.env`, token, secret, and credential files.
7. Surface trace counts, policy blocks, learned-state candidates, and restore checks in the Control Panel.

Required tests:

- Agent cannot see raw Slack, Outlook, GitHub, or provider tokens through the sandbox contract.
- Network policy blocks destinations outside an allowlist and records a replayable policy error.
- Trace-to-skill proposals produce review-required candidates, not active prompt or skill mutations.
- Snapshot excludes credential-like files and restores learned non-secret state.
- Control Panel shows redacted trace, policy, and learned-state evidence.

Security and policy gates:

- Policy is code and artifact-backed; prompts cannot be the only security boundary.
- Agent self-improvement is review-gated and shadow-first.
- Public and private data mixing requires ETL mirrors, read-only boundaries, source labels, and exfiltration controls.
- Trace artifacts must redact private content, secrets, tokens, private local paths, and personal identifiers.

## PB-2026-06-03-098 - Dialogue Voice Scene Alignment Lane

Accepted pattern:

SwanVoice is useful for NexusNet's audio and multimodal roadmap, but lower priority than the memory, adapter, and secure runtime targets. The strongest assimilation target is not unrestricted voice cloning. It is a **Dialogue Voice Scene Alignment Lane** for long-form multi-speaker narration, simulation playback, operator reports, and audio/video assimilation metadata.

The technical subtarget worth preserving is pause-aware word alignment, speaker-turn conditioning, dialogue-scene continuity, and audio-scene evaluation. These can support better video-watcher transcripts, multi-agent conversation replay, and narrated Control Panel artifacts.

Implementation path:

1. Add an audio-scene schema before any synthesis: speaker ids, consent refs, turn ids, pause markers, alignment refs, emotion/style labels, and provenance.
2. Add a forced-alignment evaluation lane for transcripts and video/audio assimilation artifacts.
3. Keep generated speech as optional presentation output, not source evidence.
4. Require speaker consent and voice-rights metadata before any cloned or identity-like voice use.
5. Evaluate content accuracy separately from expressiveness, hierarchy, and speaker similarity.
6. Preserve generated audio provenance, watermark/disclosure refs, and rollback/deletion refs.

Required tests:

- Audio-scene records require consent refs for identity-like voice generation.
- Generated voice output cannot satisfy evidence or citation gates.
- Forced alignment preserves timestamps, speaker turns, and source refs.
- Content-accuracy failures block promotion even if expressiveness scores improve.

Security and policy gates:

- No unauthorized voice cloning.
- No training on copyrighted or private audio without explicit rights.
- Synthetic speech must be disclosed, provenance-marked, and excluded from factual evidence.
- Emotion/style conditioning cannot be used to impersonate or manipulate a real person.

## Promotion Boundary

Immediate canon effect is documentation and candidate tracking only. Implementation should proceed in this order:

1. Extend the harness contract and secure runtime evidence path from `PB-2026-06-03-094` and `PB-2026-06-03-097`.
2. Add adapter passport and adapter registry tests for `PB-2026-06-03-096`.
3. Design the memory-model lane for `PB-2026-06-03-095` behind KAC and source-rights gates.
4. Keep `PB-2026-06-03-098` as research_only until audio consent, model availability, and content-accuracy gates are proven.

