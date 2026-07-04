# Landlock Seccomp Micro Sandbox Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet platform-specific sandbox launchers.

## Source Evidence

- Linux Landlock userspace API docs: https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- Linux Landlock security docs: https://www.kernel.org/doc/html/latest/security/landlock.html
- Linux seccomp filter docs: https://cdn.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- Source status: official Linux kernel documentation.

## Finding

Landlock allows unprivileged filesystem access control, while seccomp filters restrict system calls. Together they form a lightweight local process sandbox pattern that can sit below agent tools without requiring a full container for every command.

## NexusNet Assimilation Target

Create a micro-sandbox launcher for local tools and coding agents. The launcher should grant project-scoped filesystem access, deny unrelated paths, restrict risky syscalls where practical, and feed observed denials into the run trace.

## Proposed NexusNet Components

- `MicroSandboxProfile`: allowed read/write roots, denied roots, syscall profile, network policy, and platform support.
- `SandboxLaunchPlan`: command, environment, working directory, credentials, and expected effects.
- `AccessDenialTrace`: blocked path, syscall, process, and reason.
- `ProfileCompatibilityProbe`: checks kernel/API support before enforcing a profile.
- `MicroSandboxRegressionSuite`: attempts sensitive path reads, writes, process escapes, and syscall misuse.

## Promotion Gates

- Default to read/write only inside the declared workspace or disposable temp roots.
- Check Landlock ABI and seccomp support at runtime.
- Fail closed for high-authority tools when sandboxing is required but unavailable.
- Keep platform-specific notes for Linux, Windows, and macOS rather than pretending one sandbox fits all.
- Record denied access events without leaking sensitive path contents.

## Risks

- Landlock and seccomp are Linux-specific; other platforms require different primitives.
- Seccomp policies can break tools due to hidden syscalls.
- Filesystem sandboxes do not replace network, credential, or UI authority controls.
