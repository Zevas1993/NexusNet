# Synthetic Truth Guard Spec

Status: critical governance candidate. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_Synthetic-Truths-Gemini-has-a-Secret-Cod_Media_3ib3Mr9O8YQ_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/06-synthetic-truths-gemini-secret-code/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

## Target Pattern

The video's high-value target is not a Gemini-specific claim. The target is a general failure mode: an LLM can produce a coherent, authority-shaped explanation that feels like a discovered truth while being unsupported, invented, or over-interpreted.

NexusNet needs a `synthetic-truth-guard` before further research/canon acceleration. This guard should force claims through provenance, contradiction handling, uncertainty, and abstention scoring.

## External Confirmation

- TruthfulQA shows that models can generate false answers that mimic misconceptions and can deceive users; scaling alone is not a reliable truthfulness fix: https://arxiv.org/abs/2109.07958
- OpenAI's hallucination research frames confident false answers as partly driven by training/evaluation incentives that reward guessing over uncertainty: https://openai.com/index/why-language-models-hallucinate/

## NexusNet Use

Build the guard over existing evidence and trust surfaces:

- `nexusnet/knowledge/compiler.py` for knowledge artifact source refs and blocked refs.
- `nexusnet/security/artifact_trust.py` for trust scanning and quarantine behavior.
- `nexusnet/memory/quality_ledger.py` for source/claim quality state.
- `nexusnet/teachers/` for teacher disagreement and review.
- `nexusnet/telemetry/genai_observability.py` for trace metadata without private content.
- `ui/control-panel/` for claim provenance and blocked-promotion visibility.
- `tests/test_knowledge_artifact_compiler.py`, `tests/test_artifact_trust_registry.py`, and `tests/test_memory_quality_ledger.py`.

## Spec Requirements

- Claim object: text, source refs, source status, evidence strength, contradiction refs, uncertainty label, reviewer, and promotion state.
- Source status enum: `primary_verified`, `secondary_verified`, `transcript_only`, `operator_supplied`, `inferred`, `unverified`, `contradicted`, `rejected`.
- Abstention reward: research agents should score higher for saying "not verified" than for fabricating a confident claim.
- Contradiction workflow: when sources conflict, preserve both refs and require resolution before promotion.
- Canon promotion gate: no claim becomes canon unless it has acceptable source status, current-date check when relevant, and KAC/trust registry clearance.

## Refusals

- Do not turn transcript-only claims into canon.
- Do not accept polished language, model self-analysis, or "it sounds plausible" as evidence.
- Do not hide failed searches; failed verification is evidence.
- Do not let teacher consensus override source absence for factual claims.

## Acceptance Criteria

- A research artifact can mark claims as verified, inferred, unverified, or rejected.
- A hallucinated citation or unsupported paper claim is blocked from promotion and surfaced in Control Panel.
- The scoring system rewards uncertainty/abstention over confident unsupported answers.
- Every canon/research refresh report carries a source-status summary.

