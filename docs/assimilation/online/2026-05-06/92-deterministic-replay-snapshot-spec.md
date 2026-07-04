# Deterministic Replay Snapshot Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet sandbox, test, and incident replay infrastructure.

## Source Evidence

- rr project site: https://rr-project.org/
- rr repository: https://github.com/rr-debugger/rr
- CRIU main page: https://criu.org/Main_Page
- CRIU checkpoint/restore docs: https://criu.org/Checkpoint/Restore
- Docker checkpoint docs: https://docs.docker.com/reference/cli/docker/checkpoint/
- Source status: official project docs and repositories.

## Finding

Record/replay debugging and checkpoint/restore tools capture enough execution state to reproduce failures that ordinary logs miss. For agent systems, this can turn flaky tool failures, native crashes, and sandbox state bugs into replayable incidents.

## NexusNet Assimilation Target

Add a replay/snapshot evidence tier for high-value local runs. When a run fails in a sandbox, NexusNet should be able to save enough state to replay the failure in a controlled diagnostic environment without exposing unrelated private data.

## Proposed NexusNet Components

- `ReplayCapturePolicy`: decides which lanes can capture rr traces, container checkpoints, screenshots, logs, and filesystem diffs.
- `ExecutionSnapshot`: container/process state, environment digest, input digest, and privacy classification.
- `ReplayBundle`: sanitized artifact that can reproduce or inspect a failed run.
- `ReplayVerifier`: checks that the replayed failure matches the original trace.
- `SnapshotRetentionPolicy`: expiry and redaction rules for heavy/private replay artifacts.

## Promotion Gates

- Capture only inside declared sandbox boundaries.
- Redact or exclude private files outside the run scope.
- Record tool versions, kernel/runtime constraints, and replay limitations.
- Verify at least one replay path before calling an incident reproducible.
- Expire heavy replay bundles unless explicitly retained.

## Risks

- Replay artifacts can be large and privacy-sensitive.
- Linux-specific tooling does not cover every Windows/macOS scenario.
- Restored processes can have side effects unless replay is isolated.
