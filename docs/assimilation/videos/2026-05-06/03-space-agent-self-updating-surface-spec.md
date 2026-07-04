# Space Agent Self-Updating Surface Spec

Status: high-value candidate, shadow-only until promotion gates pass. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_This-AI-Agent-can-actually-self-evolve-j_Media_F3ZzNgf-R7Y_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/03-self-evolving-ai-agent/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

## Target Pattern

The video's strong idea is not "let the agent modify itself live." The useful pattern is a browser-native agent surface where the agent can propose, render, test, and persist new UI/function modules as reviewable artifacts.

The NexusNet version should be a self-updating surface sandbox:

- generate a candidate UI/workflow module;
- run it in an isolated browser/runtime space;
- record screenshots, DOM diffs, action traces, and policy findings;
- run evals against the candidate;
- submit it to teacher/human review;
- only then promote to an allowed surface.

## External Confirmation

- Space Agent presents itself as a free, open-source browser-based agent and points to self-host/native options: https://space-agent.ai/
- The upstream repository is `agent0ai/space-agent`: https://github.com/agent0ai/space-agent
- The adjacent Agent0 self-evolution paper frames self-evolving agents through tool-integrated reasoning and generated curricula, which supports using the concept as a governed research target rather than an unreviewed runtime privilege: https://arxiv.org/abs/2511.16043

## NexusNet Use

Map this to existing governed self-improvement surfaces:

- `nexusnet/core/self_improvement/` for event capture, triage, evaluator, regression gate, and provenance.
- `nexusnet/agents/sandbox_factory.py` for disposable agent/sandbox manifests.
- `nexusnet/agents/pipelines/service.py` for structured agentic runs.
- `nexusnet/core/autonomous_updates.py` for update governance and rollback requirements.
- `nexus/api/app.py` self-improvement endpoints for capture, queue, and review.
- `tests/test_self_improvement_layer.py`, `tests/test_sandbox_agent_factory.py`, and `tests/test_agentic_pipeline_runtime.py`.

## Spec Requirements

- Candidate artifact schema: target surface, generated files, browser route, permission profile, screenshots, DOM diff, test output, policy scan, rollback plan.
- Hard sandbox default: generated modules cannot write to production UI or backend routes.
- Review queue: teacher council review, policy kernel review, EvalsAO result, operator approval, and expiry.
- Promotion levels: `draft`, `sandbox-demo`, `shadow-enabled`, `operator-approved`, `live-guarded`, `rolled-back`.
- Runtime receipt: every generated module must be traceable to prompt, input evidence, model/provider, and reviewer decision.

## Refusals

- Do not grant the agent unrestricted frontend/backend mutation.
- Do not persist generated modules without provenance and rollback.
- Do not let a successful demo bypass regression gates.
- Do not treat browser DOM edits as durable product changes unless they are compiled into reviewed artifacts.

## Acceptance Criteria

- A self-updating surface candidate can be generated and run entirely in sandbox mode.
- The candidate stores screenshots, diffs, policy findings, and eval output.
- A blocked candidate remains visible in Control Panel with the blocking reason.
- A promoted candidate must have a rollback artifact and a passing regression gate.

