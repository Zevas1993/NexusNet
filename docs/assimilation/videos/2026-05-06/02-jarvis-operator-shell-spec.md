# Jarvis Mark XXXIX Operator Shell Spec

Status: repo-backed clean-room assimilation target. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_New-Flexible-AI-Model-Jarvis-Mark-XXXIX_Media_ej1f5OE3SNQ_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/02-jarvis-mark-xxxix-flexible-model/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

Primary source:

- Repository: https://github.com/FatihMakes/Mark-XXXIX
- README setup video: https://youtu.be/ej1f5OE3SNQ?si=lCxDhJix9ungq1Ry
- Reviewed branch `main` at commit `d3e85047061000f148d5bd675c471cdea899f5de` from 2026-05-02.
- Local syntax check of the reviewed clone passed with `python -m compileall -q .`.
- No test files were found in the reviewed repository.
- License status: personal/non-commercial only under Creative Commons BY-NC 4.0. Do not copy code, prompts, or assets into NexusNet.

## Source Confidence

The earlier uncertainty note is superseded. Mark XXXIX has a public source repository that matches the video identity and setup link. The source confidence is high for the existence of the project and its operator-shell architecture.

The assimilation boundary is still narrow: use the repository as a product/architecture reference only. NexusNet should not import implementation code because of license limits and because several repo paths grant broad authority over the user's computer.

## Repo Review Findings

- `main.py` uses a Gemini Live session with a large function-calling surface for app launch, web search, weather, messaging, reminders, YouTube, screen processing, settings control, browser control, file control, code helper, development agent, game update, flight finding, file processing, and memory saving.
- `ui.py` provides the strongest product pattern: a configurable desktop control shell with API-key setup, dashboard state, file drop, live transcript/log style surfaces, and a flexible assistant panel.
- `memory/memory_manager.py` keeps lightweight JSON memory categories such as identity, preferences, projects, relationships, wishes, and notes, but memory can be promoted without a NexusNet-grade provenance/edit/delete workflow.
- `actions/file_controller.py` is more cautious than other tools: it constrains roots to the user home, uses recycle-bin deletion, and blocks protected top-level folders.
- `actions/browser_control.py`, `actions/computer_control.py`, and `actions/computer_settings.py` expose high-authority desktop/browser controls. Some dangerous actions have confirmation, but most actions do not use a uniform permission envelope.
- `agent/executor.py` can fall back to generated Python execution from the user's home directory. This is a useful warning sign, not an assimilation target.
- `actions/dev_agent.py` shows a compelling multi-file project-builder pattern, but dependency installation, app launch, and self-fix loops require a sandboxed NexusNet equivalent before any adoption.

## Target Pattern

Assimilate the operator-shell product pattern:

- companion-style control surface with visible system state;
- voice/chat command flow subordinate to the NexusNet brain path;
- explicit API/provider setup and health state;
- file drop and upload affordances that route through artifact trust;
- memory/preferences panel with operator controls;
- browser, desktop, vision, scheduler, and file actions presented as governed tools;
- action log that makes assistant behavior inspectable instead of hidden.

## NexusNet Use

Map the clean-room pattern into governed NexusNet surfaces:

- `nexusnet/browser/context_memory.py` for operator-provided local context only.
- `nexusnet/vision/computer_use.py` for vision/computer-use action planning.
- `nexusnet/agents/scheduled/` for reminders and scheduled assistant workflows.
- `nexusnet/policy/kernel.py` for action allowlists and hard-deny rules.
- `nexusnet/security/` and Artifact Trust Registry for imported files or generated action artifacts.
- `ui/control-panel/` for operator-visible permissions, active memory, action history, and provider/API health.
- `tests/test_browser_context_memory.py` and `tests/test_multimodal_computer_use.py` as current guardrail anchors.

## Spec Requirements

- Permission envelope per action class: read-only local context, file import, camera, desktop setting, app control, network lookup, scheduled action, browser session, and generated artifact.
- Action receipt for every OS-adjacent command: request, model rationale, permission state, executor, result, captured evidence, and rollback if available.
- Preference memory schema with provenance, edit/delete controls, consent state, source trace, and "do not remember" support.
- File-drop intake that routes through artifact trust scanning before use.
- Browser profile policy: default to disposable or NexusNet-owned profiles; never attach to real user browser profiles without explicit, session-scoped permission.
- Vision prompt receipt that stores image metadata and analysis result without silently promoting private visual data into memory.
- Generated-code policy: project generation can create reviewable artifacts, but execution, dependency installation, and desktop launch require sandbox + operator approval.

## Refusals

- Do not import Mark XXXIX code, prompts, assets, or UI copy into NexusNet.
- Do not make OS actions autonomous by default.
- Do not let persona memory become authority over policy, privacy, or evidence.
- Do not attach browser automation to real user profiles by default.
- Do not use generated Python execution as an unknown-tool fallback.
- Do not create a second control plane above NexusNet.

## Acceptance Criteria

- Operator shell can show memory/preferences, scheduled reminders, local file intake, browser/computer-use permissions, provider health, and recent action receipts in one surface.
- A blocked desktop action creates a visible denial receipt rather than failing silently.
- A permitted action creates an audit record and rollback metadata when rollback exists.
- Tests prove browser/private context is unavailable without explicit local-only operator permission.
- Tests prove memory promotion requires provenance and operator-visible edit/delete controls.
