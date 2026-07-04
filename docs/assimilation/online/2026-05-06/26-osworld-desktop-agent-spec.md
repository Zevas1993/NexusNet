# OSWorld Desktop Agent Spec

Status: P1 online assimilation target. Research-only until VM requirements, licenses, and Windows-host safety implications are inspected.

## Source Evidence

- OSWorld paper: https://arxiv.org/abs/2404.07972
- OSWorld repository: https://github.com/xlang-ai/OSWorld
- Windows Agent Arena paper: https://arxiv.org/abs/2409.08264
- Microsoft Research page: https://www.microsoft.com/en-us/research/publication/windows-agent-arena-evaluating-multi-modal-os-agents-at-scale/
- Source status: primary papers, public OSWorld repository, and Microsoft project publication.

## Finding

OSWorld and Windows Agent Arena evaluate multimodal agents inside real operating-system environments rather than toy UI pages. They cover desktop apps, file I/O, planning, screen understanding, and tool usage, with OSWorld-Verified and Windows-specific task suites showing the direction for more stable desktop-agent evaluation.

## NexusNet Assimilation Target

Define a DesktopOps lane that never touches the host desktop directly during certification. NexusNet should prove desktop-control behavior inside disposable VM snapshots with explicit task state, action traces, rollback, and evaluator evidence before any operator-facing desktop automation is exposed.

## Proposed NexusNet Components

- `DesktopTaskPassport`: VM image, initial snapshot, allowed apps, evaluator, time limit, step limit, and data classification.
- `VMStateSnapshot`: hashable pre-state and post-state metadata plus rollback handle.
- `DesktopActionTrace`: screenshot digest, accessibility tree where available, action, coordinates, active window, and blocked-action flag.
- `DesktopEvaluator`: checks file state, app state, and explicit task success conditions.
- `HostSafetyGate`: blocks host filesystem, host credentials, clipboard leakage, and unsandboxed shell bridges.

## Promotion Gates

- Require disposable VM or containerized desktop sessions.
- Disable host clipboard, credential stores, personal folders, and ambient browser profiles.
- Record every GUI and shell action with replayable evidence.
- Require separate safety tests for direct state mutation and evaluator gaming.

## Risks

- Desktop benchmark setup is heavy, especially on Windows hosts.
- GUI benchmarks can be gamed by directly changing expected state if the sandbox allows it.
- Passing OS tasks does not imply the agent is safe around real user files or private sessions.
