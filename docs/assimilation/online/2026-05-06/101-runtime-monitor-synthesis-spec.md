# Runtime Monitor Synthesis Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet run monitors and policy-to-monitor generation.

## Source Evidence

- NASA Ogma repository: https://github.com/nasa/ogma
- Copilot Language repository: https://github.com/Copilot-Language/copilot
- NASA cFS repository: https://github.com/nasa/cFS
- NASA F Prime repository: https://github.com/nasa/fprime
- Source status: official NASA and Copilot project repositories.

## Finding

Ogma generates runtime monitors for flight and robotics systems and can target cFS and F Prime integration patterns. Copilot is a stream-based runtime-verification framework that generates hard real-time C. The NexusNet transfer is property-to-monitor generation: high-risk policies should become live monitors, not only prose rules.

## NexusNet Assimilation Target

Generate lightweight runtime monitors from NexusNet policies and invariants. These monitors should watch traces as runs happen and trip clear actions when a property is violated.

## Proposed NexusNet Components

- `MonitorPropertySpec`: temporal or stream property over commands, telemetry, tool calls, memory writes, and approvals.
- `GeneratedRunMonitor`: executable watcher generated from approved property specs.
- `MonitorInputBinding`: maps event-stream fields to monitor variables.
- `ViolationHandler`: pause run, revoke grant, request review, roll back patch, or emit incident.
- `MonitorCoverageReport`: shows which policies have live monitors and which are docs-only.

## Promotion Gates

- Keep generated monitors small and inspectable.
- Bind monitor inputs to typed event schemas, not log-string parsing.
- Fail closed for high-authority invariant violations.
- Test monitors with synthetic event streams before production use.
- Review any LLM-assisted property translation before monitor generation.

## Risks

- Monitoring the wrong property creates false confidence.
- Runtime monitors need low overhead and clear failure behavior.
- Too many noisy monitors can create alert fatigue.
