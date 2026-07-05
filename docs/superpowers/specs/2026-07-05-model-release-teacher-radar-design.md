# NexusNet Model Release Teacher Radar Design

Date: 2026-07-05
Status: Approved design direction; awaiting implementation plan

## Purpose

NexusNet needs a continuous model-release intake loop so newly released models can become governed teacher candidates for Orchestrators, Assistant Orchestrators, Experts, temporary experts, and the model NexusNet eventually births. The loop must support automatic downtime research and benchmarking, while preserving NexusNet's core rule that improvements are reviewed through the proper promotion pipeline before they affect active teachers, training, distillation, routing, or production behavior.

The chosen approach is Downtime Auto-Benchmark, Gated Promotion.

## Current Anchors

The design attaches to existing repo structures instead of creating a parallel teacher system:

- `TeacherCandidateUniverse` remains the canonical candidate registry.
- `Cluster9TeacherReconciliationRegistry` remains the O/AO/Expert teacher-pairing consumer.
- Release Harness and control-panel surfaces remain the operator-visible place for sanitized status and evidence.
- NexusBrain remains the authority that can recommend or approve promotion, replacement, merge, split, retirement, or rejection.

## Goals

- Discover newly released model candidates from configured model-release sources.
- Convert release metadata into normalized teacher-candidate records.
- Classify possible teacher roles and target NexusNet domains.
- Queue and run safe benchmarks during downtime.
- Attach sanitized evidence refs to the candidate record.
- Keep candidates watchlist, quarantined, benchmarked, shadow, or canary until all gates pass.
- Prevent autonomous promotion into active teachers without NexusBrain/governance approval.
- Give the birthed model the same radar/eval/gated-promotion loop so it can keep improving under inherited governance.

## Non-Goals

- No automatic active teacher promotion.
- No automatic training, distillation, model download, or weight mutation from a new candidate.
- No bypass of license, provenance, privacy, hardware, cost, eval, rollback, or safety gates.
- No separate teacher registry outside `TeacherCandidateUniverse`.
- No raw prompt, private session data, secret, credential, or unredacted benchmark input storage in candidate evidence.

## Architecture

### ModelReleaseRadar

`ModelReleaseRadar` discovers potential teacher sources and emits normalized release observations. It should support source adapters for Hugging Face, GitHub, provider release feeds, curated local watchlists, and future marketplace or research-paper feeds. Each adapter produces sanitized metadata only: model id, provider, release URL, release date if known, modality, size hints, license text/ref, model-card refs, tags, tasks, and provenance hashes where available.

### TeacherCandidateIntake

`TeacherCandidateIntake` converts release observations into `TeacherCandidate` records or updates existing candidates. New candidates start as `watchlist` when evidence is incomplete and `quarantined` when license, provenance, safety, or privacy risk is known or unresolved. Duplicate releases update source refs and metadata rather than creating conflicting candidate ids.

### Role And Domain Classifier

The classifier maps a candidate to teacher roles and domain scopes. It can propose generator, critic, verifier, retriever, simulator, compact apprentice, or judge roles. It must also map domains to Cluster 9 coverage areas such as orchestration, coding, formal methods, medical, quantum, finance, crypto, recursive dreaming, graph, memory, world models, multimodal perception, edge/mobile, security, and future expert domains.

### DowntimeBenchmarkScheduler

The scheduler runs benchmark jobs only when downtime gates allow it. Downtime means there is low user activity, safe thermal/load posture, available budget, no high-priority live problem, and no release gate requiring resources. The scheduler should start with inexpensive metadata and smoke checks before heavier domain evals.

### TeacherEvidenceLedger

The ledger records sanitized evidence refs, benchmark summaries, blockers, and recommendations. Evidence is append-only and traceable. A candidate can gain benchmark refs, source refs, blocker refs, and comparison refs, but active promotion still requires the governance pipeline.

## Candidate Lifecycle

The lifecycle is:

1. `watchlist`: discovered and normalized, but not benchmark-ready.
2. `quarantined`: held because source, license, safety, privacy, or provenance needs review.
3. `benchmarked`: downtime evals ran and produced sanitized evidence.
4. `shadow`: eligible for non-production teacher comparisons and distillation-readiness review.
5. `canary`: limited governed trial against a narrow non-production workload.
6. `active`: approved through NexusBrain/governance pipeline.
7. `retired`: superseded or unsafe, preserved for lineage and rollback.
8. `blocked`: explicitly disallowed until a blocker changes.

Automatic jobs may move candidates into watchlist, quarantined, or benchmarked states when policy allows. Shadow, canary, active, retired, merge, split, replace, and reject decisions require the proper review pipeline.

## Gates

Every candidate must carry gate status:

- Source gate: model card, release page, repository, paper, checksum, and provenance refs exist.
- License gate: training, distillation, evaluation, local inference, and redistribution rights are known.
- Privacy gate: eval and inference path can avoid private/raw user data.
- Safety gate: candidate does not introduce obvious malware, unsafe remote code, impersonation, medical/financial/legal misuse, or policy-blocking risk.
- Hardware gate: expected runtime class is known, including local, edge, GPU, cloud, and mobile feasibility.
- Cost gate: expected eval and inference cost is bounded.
- Benchmark gate: domain evals and teacher comparisons produce enough evidence.
- Rollback gate: any later shadow/canary use can be reverted.
- NexusBrain gate: mother-brain authority reviews evidence before active promotion.

## Downtime Eval Stages

Downtime benchmarking runs in stages:

1. Metadata validation: model-card availability, source refs, license refs, provider identity, and release freshness.
2. Safety/provenance scan: suspicious files, remote-code flags, unverified authorship, and blocked terms.
3. Hardware/cost estimate: size, modality, quantization path, memory footprint, and expected evaluation budget.
4. Smoke eval: tiny bounded tasks for declared capabilities.
5. Domain eval: role-specific tasks for coding, formal proof, medical safety, finance, quantum, memory, graph, dream review, or other mapped domains.
6. Teacher comparison: compare against current teacher panel for the mapped O/AO/Expert domain.
7. Distillation-readiness review: check whether training or distillation use is rights-approved and technically useful.
8. Recommendation packet: summarize keep, quarantine, benchmarked, shadow-candidate, canary-candidate, replacement-candidate, merge-candidate, retire-candidate, or blocked.

## Promotion Rule

NexusNet may auto-run discovery and benchmarks. NexusNet may not auto-promote a candidate into an active teacher role. Promotion requires:

- approved license/provenance/privacy/hardware/cost gates,
- benchmark refs,
- teacher comparison evidence,
- rollback plan,
- Cluster 9 pairing impact review,
- NexusBrain approval,
- human/governance review where required by risk tier.

High-risk domains such as medical, finance, crypto, law, security, and high-autonomy tool use require stricter review and cannot be promoted solely by automated evidence.

## Control Surfaces

Release Harness and control-panel surfaces should expose:

- discovery feed status,
- downtime scheduler state,
- candidate counts by status,
- recently discovered candidate ids,
- candidate role/domain proposals,
- benchmark queue depth,
- latest evidence refs,
- blockers by gate,
- promotion-ready count,
- governance-required count,
- birthed-model inheritance readiness.

All surfaces must stay sanitized: counts, ids, refs, hashes, statuses, and summaries only.

## Birthed Model Inheritance

The model NexusNet births should inherit the same teacher radar pattern:

- it can discover new candidates,
- it can benchmark during downtime,
- it can update its own candidate universe,
- it can propose self-improvement,
- it cannot bypass NexusBrain lineage, governance, or gate evidence for active mutation.

If the birthed model operates independently, it must carry a local mother-brain authority equivalent and a federation path back to NexusNet when available.

## Failure Handling

- Source fetch failure keeps or returns the candidate to watchlist with a fetch blocker.
- License ambiguity quarantines the candidate.
- Unsafe file or remote-code risk quarantines the candidate.
- Benchmark failure records degraded evidence and does not delete the candidate.
- Repeated regression creates a retire or block recommendation, not an automatic deletion.
- Budget, thermal, or user-activity pressure pauses downtime evals and records a scheduler skip reason.

## Testing Strategy

Implementation should add focused tests for:

- newly discovered release observations become watchlist or quarantined teacher candidates,
- duplicate discoveries update refs without duplicate candidate ids,
- downtime scheduler refuses work under load, thermal, budget, or active-user gates,
- benchmark evidence can move a candidate to benchmarked but not active,
- promotion blockers remain until all gates and benchmark refs pass,
- Cluster 9 reconciliation sees new candidate passports without treating them as active teachers,
- release Harness/control-panel status surfaces candidate counts and sanitized evidence refs,
- high-risk domain candidates require stricter gates,
- birthed-model inheritance exposes the same gated radar contract.

## Implementation Slices

1. Add data contracts for release observations, benchmark evidence, and downtime scheduler decisions.
2. Add a `ModelReleaseRadar` service with local/static source adapters first.
3. Add intake logic that writes to `TeacherCandidateUniverse` without auto-promotion.
4. Add downtime benchmark scheduler gates and dry-run benchmark packets.
5. Surface sanitized radar state through release runtime, status-card, visualizer, and control panel.
6. Add governance recommendation packets for NexusBrain review.
7. Add optional live source adapters after the local/static path is tested.
