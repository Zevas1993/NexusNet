# Darwin Godel Machine Lineage Spec

Status: high-value self-improvement research target, shadow-only. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_World-s-First-SELF-IMPROVING-CODING-AI-A_Media_1XXxG6PqzOY_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-next-20260506/YTDown_YouTube_World-s-First-SELF-IMPROVING-CODING-AI-A_Media_1XXxG6PqzOY_001_1080p_20260506_095038/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`, `contact_sheets/sheet_014.jpg`

## Target Pattern

The valuable target is not automatic production self-modification. The useful DGM pattern is a traceable archive of agent variants where frozen foundation models propose changes to agent scaffolding, tools, prompts, or workflows, then benchmark gates decide whether each offspring is useful enough to keep exploring.

NexusNet should assimilate this as a shadow-only improvement lane:

- candidate variants are created as artifacts, not live code changes;
- every parent/offspring edge records prompt, patch, tests, eval scores, reviewer notes, and safety findings;
- low-scoring but interesting branches can remain in the archive as future stepping stones;
- promotion requires transfer tests, regression tests, and human/teacher review.

## External Confirmation

- Sakana AI describes DGM as a self-improving coding agent that rewrites its own code and evaluates proposed changes on SWE-bench and Polyglot: https://sakana.ai/dgm/
- The DGM page reports open-ended archive exploration, transfer across models/tasks, and safety concerns around fake tool-use logs and objective hacking: https://sakana.ai/dgm/
- The DGM paper and code are linked from the primary page: https://arxiv.org/abs/2505.22954 and https://github.com/jennyzzt/dgm

## NexusNet Use

Map this into existing NexusNet self-improvement and native-execution lanes:

- `nexusnet/core/self_improvement/` for candidate capture, triage, evaluator, provenance, and rollback state.
- `nexusnet/core/autonomous_updates.py` for explicit promotion gates and blocked-update state.
- `nexusnet/agents/sandbox_factory.py` for disposable workspaces where offspring can be built and tested.
- `nexusnet/evals/` for benchmark suites, transfer checks, and anti-Goodhart probes.
- `nexusnet/teachers/` for teacher council review of candidate utility and safety.
- `ui/control-panel/` for lineage tree, blocked gates, benchmark deltas, and reviewer decisions.

## Spec Requirements

- Lineage artifact schema: `candidate_id`, parent ids, mutation prompt, touched files, diff summary, eval suite, scores, failure logs, safety flags, transfer results, reviewer decision, and rollback plan.
- Archive search policy: keep both best-scoring candidates and diverse stepping-stone candidates, but mark non-promoted candidates as `refs-only`.
- Evaluation matrix: unit tests, integration tests, coding-task benchmark, regression suite, safety benchmark, and transfer check against at least one alternate model/provider where feasible.
- Anti-cheat evidence: commands must produce real captured stdout/stderr, timestamps, cwd, exit code, and artifact hashes; fake logs cannot satisfy gates.
- Promotion states: `proposed`, `built-in-sandbox`, `eval-failed`, `safety-blocked`, `shadow-passed`, `teacher-approved`, `operator-approved`, `merged`, `rolled-back`.

## Refusals

- Do not let the system rewrite production NexusNet code directly.
- Do not optimize only for benchmark score without safety and regression probes.
- Do not accept model-written test logs or summaries as proof.
- Do not let a high-scoring candidate bypass source/ref trust, KAC, or artifact trust boundaries.
- Do not treat DGM as locked canon until primary paper/code review is completed.

## Acceptance Criteria

- NexusNet can create a candidate lineage entry without modifying live production files.
- A candidate run stores real command receipts and hashable artifacts.
- Control Panel can show parent/child lineage, current score deltas, blocked gates, and next operator action.
- A reward-hacking probe can fail a candidate even when the main benchmark score improves.
- A promoted candidate has replay instructions and rollback metadata.
