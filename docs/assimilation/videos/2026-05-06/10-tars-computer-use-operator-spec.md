# TARS Computer-Use Operator Spec

Status: high-value VisualOps/operator-plane target. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_TARS-Agent-Powerful-AI-Operating-System-_Media_vF8FWmzRd5M_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-next-20260506/YTDown_YouTube_TARS-Agent-Powerful-AI-Operating-System-_Media_vF8FWmzRd5M_001_1080p_20260506_100349/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`, `contact_sheets/sheet_020.jpg`

## Target Pattern

The useful TARS pattern is a split operator stack: CLI/Web UI/Desktop surfaces on top of multimodal computer-use, browser-use, MCP tools, and provider-configurable models.

NexusNet should not copy the demo's authority posture. It should assimilate the operator ergonomics: visible event stream, model/provider selector, browser/system operator separation, MCP server configuration, task replay, and a stop/rollback surface.

## External Confirmation

- ByteDance's UI-TARS desktop repository describes TARS as a multimodal AI agent stack with Agent TARS and UI-TARS Desktop: https://github.com/bytedance/UI-TARS-desktop
- The repo describes Agent TARS as bringing GUI agent and vision capabilities to terminal, computer, browser, and product workflows, with CLI/Web UI usage and MCP integration: https://github.com/bytedance/UI-TARS-desktop
- The repo describes UI-TARS Desktop as a native GUI agent with local/remote computer and browser operators, and the Agent TARS CLI can be launched with `npx @agent-tars/cli@latest`: https://github.com/bytedance/UI-TARS-desktop

## NexusNet Use

Map this into a governed VisualOps/computer-use plane:

- `nexusnet/vision/computer_use.py` for visual grounding, screenshot state, proposed actions, and confidence.
- `nexusnet/browser/` for browser-control adapters with local-only permission scopes.
- `nexusnet/policy/kernel.py` for action allowlists, high-authority prompts, and hard-deny rules.
- `nexusnet/telemetry/` for event stream spans, screenshots metadata, tool calls, and failure receipts.
- `nexusnet/security/` and Artifact Trust Registry for files touched by browser/computer tasks.
- `ui/control-panel/` for provider selection, operator mode, MCP mounts, event stream viewer, pause/stop, and rollback.

## Spec Requirements

- Operator split: `browser_operator`, `desktop_operator`, `terminal_operator`, `file_operator`, and `mcp_tool_operator` must have separate permissions.
- Event stream: every observation, plan, action, tool call, screenshot, DOM state, result, and correction must be inspectable.
- Provider selector: model/provider credentials remain operator-owned, scoped, and health-checked.
- MCP mount registry: each server records source, permissions, tool names, allowed roots, and revocation state.
- Action confidence: GUI clicks and keyboard input require target confidence, screenshot evidence, and a stop window before high-risk actions.
- Local/remote boundary: remote computer operation is a separate capability class with stronger warnings and disabled default state.

## Refusals

- Do not market NexusNet as "automates all computer tasks" without scoped capability evidence.
- Do not allow browser/desktop/terminal operators to share permissions implicitly.
- Do not run high-authority tasks without a visible event stream and stop control.
- Do not mount MCP servers without source, permission, and revocation metadata.
- Do not treat demo success as benchmark proof; OSWorld-style evals are still required.

## Acceptance Criteria

- A computer-use task produces a replayable event stream with observations, actions, screenshots metadata, and final result.
- Control Panel can pause/stop an active operator run and show what permission class is active.
- A browser task cannot escalate into desktop or terminal control without a new permission grant.
- MCP server mounts are visible, scoped, and revocable.
- A failed UI-grounding action records confidence, screenshot metadata, and recovery state instead of silently retrying forever.
