# OpenClaw Assimilation

## Canon Status
- NexusNet brain-first wrapper/runtime stack: `LOCKED CANON`
- OpenClaw-style runtime patterns: `STRONG ACCEPTED DIRECTION`
- Source reverified 2026-05-31: `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`

## Source Health Update - 2026-05-31

The earlier OpenClaw direction remains a pattern-level architecture reference, but two pinned source URLs no longer resolve:

- `https://docs.openclaw.ai/en/docs/skills/overview` returned 404.
- `https://docs.openclaw.ai/en/docs/approvals/overview` returned 404.

Do not strengthen OpenClaw claims or import OpenClaw behavior until current primary docs or repository sources are re-pinned. Hermes Agent was separately source-confirmed at `https://github.com/NousResearch/hermes-agent` as a skill/memory-loop reference, so Hermes-style learning should be tracked as a SkillOps pattern rather than merged into the stale OpenClaw source claim.

## What NexusNet Steals
- Local gateway pattern
- Skill packages with precedence
- Per-agent and per-workspace allowlists
- Exec approvals and ask fallback
- Deny-by-default on ambiguous execution binding

## What NexusNet Refuses
- A second control plane above NexusNet
- Replacing the wrapper/brain path with a generic gateway shell

## Integration Shape
- `nexusnet/runtime/gateway/` holds the local control-plane pattern.
- `nexusnet/tools/skills/`, `approvals/`, and `policy/` hold packaged behavior and execution policy.
- Wrapper/ops surfaces expose the state read-only.

## Sources
- https://docs.openclaw.ai/en/docs/skills/overview
- https://docs.openclaw.ai/en/docs/approvals/overview
- https://openclawalpha.org/en/playbooks/development/p/autoclaw-local-openclaw-solution-2038632251551023250
- Hermes pattern comparator: https://github.com/NousResearch/hermes-agent
