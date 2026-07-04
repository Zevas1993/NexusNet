# Terminal Bench Sandbox Spec

Status: P1 online assimilation target. Research-only until harness license, task format, and local Docker requirements are inspected.

## Source Evidence

- Terminal-Bench paper: https://arxiv.org/abs/2601.11868
- Terminal-Bench repository: https://github.com/harbor-framework/terminal-bench
- Source status: primary paper page and public benchmark repository.

## Finding

Terminal-Bench 2.0 evaluates agents on hard, realistic terminal tasks with unique environments, human-written oracle solutions, and comprehensive tests. The repository positions the benchmark as a sandboxed execution harness for real command-line work, not just code-generation output.

## NexusNet Assimilation Target

Create a NexusNet terminal-certification lane before trusting native expert execution. Any shell/code lane should prove it can operate in a sandbox, satisfy task tests, preserve logs, and explain failures before it gains authority in a real workspace.

## Proposed NexusNet Components

- `TerminalTaskPassport`: instruction, sandbox image, allowed tools, test script, oracle status, timeout, and risk level.
- `ShellExecutionTrace`: command, working directory, stdout/stderr digest, exit code, file diff summary, and policy gate result.
- `TerminalHarnessAdapter`: maps NexusNet native execution into a Terminal-Bench-like sandbox contract.
- `Control Panel`: shows task result, failing tests, blocked commands, and replay path.

## Promotion Gates

- Run only in isolated containers or disposable worktrees.
- Block host-path access, secrets, and network by default.
- Require tests plus diff review, not only agent-reported success.
- Keep benchmark tasks separate from production user workspaces.

## Risks

- Terminal tasks can still produce destructive commands if sandboxing is incomplete.
- Docker/runtime setup may be heavy on Windows and should be measured before adoption.
- Passing terminal benchmarks does not imply product-ready code review quality.
