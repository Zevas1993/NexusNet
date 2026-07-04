# Flight Software Command Telemetry Bus Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet Control Panel, run bus, and health channels.

## Source Evidence

- NASA cFS repository: https://github.com/nasa/cFS
- NASA cFS reference docs list: https://github.com/nasa/cFS#references-documentation
- NASA F Prime docs: https://nasa.github.io/fprime/
- NASA F Prime repository: https://github.com/nasa/fprime
- Source status: official NASA repositories and docs.

## Finding

NASA's cFS and F Prime show mature patterns for command, telemetry, reusable applications/components, health channels, and mission-specific verification responsibility. This is a better mental model for NexusNet than chat-only agents: operators need command paths, telemetry paths, health checks, stored commands, limit checks, and safe-mode behavior.

## NexusNet Assimilation Target

Create a NexusNet command/telemetry bus for agent operations. Every high-authority lane should expose commands, telemetry, health, limits, event messages, and safe-mode transitions as first-class surfaces.

## Proposed NexusNet Components

- `NexusCommandPacket`: operator command, authority grant, target component, nonce, and approval trace.
- `NexusTelemetryPacket`: state, metric, health, event, or incident record emitted by a component.
- `HealthAndSafetyApp`: monitors stalled runs, limit violations, memory pressure, sandbox failures, and unsafe tool drift.
- `StoredCommandQueue`: reviewable scheduled commands with expiry and cancellation.
- `LimitChecker`: threshold rules that trip warnings, pauses, or safe-mode transitions.

## Promotion Gates

- Separate command ingestion from telemetry emission.
- Require command authentication, nonce/replay protection, and operator-visible effect summary.
- Every high-authority component must publish health telemetry.
- Limit-checking must be testable with simulated bad telemetry.
- Treat flight software as a discipline source, not as a claim of flight readiness.

## Risks

- Command/telemetry architecture can be overbuilt for simple local workflows.
- Operators can ignore telemetry unless the UI turns it into clear action.
- Scheduled commands need strong expiry and cancellation controls.
