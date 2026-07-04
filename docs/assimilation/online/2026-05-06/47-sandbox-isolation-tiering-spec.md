# Sandbox Isolation Tiering Spec

Status: P1 online assimilation target. Research-only until local Windows, Docker, VM, and NexusNet runtime constraints are tested.

## Source Evidence

- gVisor docs: https://gvisor.dev/docs/
- Firecracker project docs: https://firecracker-microvm.github.io/
- Kata Containers docs: https://katacontainers.io/
- E2B sandbox docs: https://e2b.dev/docs
- Source status: official documentation and public project pages.

## Finding

Agent sandboxes are not one thing. gVisor, Firecracker, Kata Containers, and E2B show different tradeoffs across syscall interception, microVM isolation, container compatibility, startup speed, language/runtime ergonomics, and operational complexity.

## NexusNet Assimilation Target

Create a sandbox tier matrix for shell, code, browser, desktop, MCP, and experiment lanes. NexusNet should select isolation based on action risk, not convenience.

## Proposed NexusNet Components

- `SandboxProfile`: none, read-only workspace, disposable worktree, container, hardened container, microVM, full VM, or remote sandbox.
- `IsolationRequirement`: filesystem, network, process, kernel, GPU, clipboard, credential, and persistence boundaries.
- `SandboxBroker`: chooses a sandbox profile from the action policy decision.
- `EscapeCanary`: synthetic secrets, files, and network traps used to prove containment.
- `SandboxEvidenceReport`: launch config, mounted paths, network policy, allowed tools, and teardown result.

## Promotion Gates

- High-risk code and shell tasks require disposable isolation.
- Browser and desktop tasks must not reuse personal profiles during certification.
- Sandboxes need teardown, network, mount, and secret-leak tests.
- Record sandbox profile in every benchmark and production trace.

## Risks

- Strong isolation can be expensive or awkward on Windows.
- A sandbox that mounts the wrong host path can still leak or destroy data.
- Remote sandboxes create privacy, cost, and availability dependencies.
