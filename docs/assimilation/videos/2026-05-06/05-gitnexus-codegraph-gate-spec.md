# GitNexus Codegraph Gate Spec

Status: high-priority assimilation already partially present. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_OpenCode-GitNexus-Give-OpenCode-Real-Cod_Media_bhsd9MXfccg_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/05-opencode-gitnexus/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`, `contact_sheets/sheet_013.jpg`

## Target Pattern

The video's practical target is a required codegraph context gate before code-affecting work:

- index the repo into a persistent graph;
- expose graph context through MCP;
- query execution flows and relationships before planning edits;
- run impact analysis before modifying symbols;
- detect changed symbols and affected flows before commit;
- expose stale-index state as a blocker.

NexusNet already has GitNexus instructions and an active GitNexus index. The assimilation work is to productize that into NexusNet's own agent/harness discipline.

## External Confirmation

- GitNexus upstream describes local indexing, graph relationships, MCP support, and `npx gitnexus analyze`: https://github.com/abhigyanpatwari/GitNexus
- The GitNexus public site summarizes the live-index/MCP positioning and points users back to the upstream repo for authoritative commands: https://gitnexus.homes/

## NexusNet Use

Build a `codegraph-required-context-gate` candidate over:

- Project `AGENTS.md` GitNexus requirements.
- GitNexus repo `NexusNet`, currently indexed with code symbols, relationships, and execution flows.
- `nexusnet/agents/pipelines/service.py` for agentic run manifests.
- `nexusnet/operations/assimilation_targets.py` for assimilation target tracking.
- `ui/control-panel/` for codegraph freshness, latest impact report, and detect-changes status.
- `tests/test_claude_code_assimilation_targets.py` and future gate tests for required graph evidence.

## Spec Requirements

- Code-affecting run manifest fields: index id, indexed commit, graph query used, impact target, impact risk, affected processes, stale-index state, and detect-changes summary.
- Policy hook: if a run plans to modify a symbol without impact evidence, block or escalate before edits.
- Stale-index behavior: warn when index commit differs from worktree head; require re-analysis for high-risk changes.
- Control Panel scorecard: indexed repo, indexed commit, node/edge/process counts, latest graph query, latest impact risk, and latest detect-changes result.
- KAC receipt: codegraph evidence is context-only until tests or implementation artifacts consume it.

## Refusals

- Do not replace direct code reading with graph output when exact source context is required.
- Do not allow a low-risk graph report to bypass tests.
- Do not trust stale graph results for symbol edits.
- Do not let graph facts become product claims without current source confirmation.

## Acceptance Criteria

- Any code-editing agentic pipeline records graph context and impact evidence.
- Missing graph evidence blocks high-risk symbol changes.
- `gitnexus_detect_changes` or equivalent detect-changes evidence is present before commit.
- Control Panel shows stale-index state and the last affected execution flows.

