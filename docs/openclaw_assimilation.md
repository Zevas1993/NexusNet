# OpenClaw Assimilation

## Canon Status
- NexusNet brain-first wrapper/runtime stack: `LOCKED CANON`
- OpenClaw-style runtime patterns: `STRONG ACCEPTED DIRECTION`

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
