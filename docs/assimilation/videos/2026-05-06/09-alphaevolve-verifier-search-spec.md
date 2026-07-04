# AlphaEvolve Verifier Search Spec

Status: high-value evaluator-first research target. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_New-maths-discoveries-All-announced-at-o_Media_sGCmu7YKgPA_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-next-20260506/YTDown_YouTube_New-maths-discoveries-All-announced-at-o_Media_sGCmu7YKgPA_001_1080p_20260506_095921/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`, `contact_sheets/sheet_015.jpg`

## Target Pattern

The useful pattern is verifier-first search: use models to propose code/algorithm candidates, but let an automated evaluator run and score them before they are kept, mutated, or promoted.

The video's main NexusNet lesson is that discovery work becomes tractable when the problem has a cheap, objective, repeatable score. NexusNet should use this for research and optimization lanes where the score is real and auditable, not as a general license for self-mutation.

## External Confirmation

- Google DeepMind describes AlphaEvolve as a Gemini-powered evolutionary coding agent that combines LLM-generated programs with automated evaluators and a program database: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- DeepMind reports practical deployments for data center scheduling, hardware design, AI training/inference, and mathematical algorithm discovery, including 4x4 complex matrix multiplication with 48 scalar multiplications and a new 11D kissing-number lower bound: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

## NexusNet Use

Map this into NexusNet as a general research optimizer:

- `nexusnet/evals/` for objective score functions, reproducible benchmark harnesses, and scorer receipts.
- `nexusnet/core/self_improvement/` for candidate databases, mutation lineage, and promotion state.
- `nexusnet/teachers/` for proposal generation and human-readable critique.
- `nexusnet/rag/` and `nexusnet/knowledge/` for retrieval scorer experiments and source-quality optimization.
- `nexusnet/runtime/` and model/router surfaces for local runtime planning, prompt templates, quantization choices, and latency/quality tradeoffs.
- `ui/control-panel/` for score curves, candidate tables, evaluator health, and blocked promotions.

## Assimilation Targets

- Evaluator contract: each experiment starts with a scorer that has inputs, expected outputs, constraints, timeout, reproducibility settings, and known failure cases.
- Candidate database: store candidate code/config/prompt, score, eval logs, parent lineage, mutation reason, and reviewer notes.
- Parallel experiment runner: launch many low-authority candidates in sandboxes, then keep only traceable outputs.
- Human proof handoff: mathematical or architectural outputs become leads for review, proof, and implementation, not instant canon.
- Multi-objective scoring: include quality, latency, memory, safety, source faithfulness, and regression risk instead of a single reward.

## Refusals

- Do not run verifier search where the scoring function is vague, private, or easy to exploit.
- Do not promote a candidate solely because it improves one metric.
- Do not let generated code write outside the sandbox or install dependencies without approval.
- Do not turn video-reported discoveries into NexusNet canon without primary-source status.
- Do not optimize governance away because it slows the search.

## Acceptance Criteria

- A NexusNet experiment can define a scorer and reject candidates that lack reproducible receipts.
- Candidate tables show lineage, score, runtime cost, safety flags, and reviewer decision.
- A multi-objective score can block a candidate that improves speed but degrades source faithfulness or safety.
- Research outputs remain `refs-only` until a code-backed consumer and promotion gate exist.
- Control Panel exposes "best candidate", "most diverse candidate", and "blocked by" states separately.
