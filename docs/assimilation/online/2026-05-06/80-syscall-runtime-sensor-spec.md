# Syscall Runtime Sensor Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet sandbox and platform support.

## Source Evidence

- Tetragon site: https://tetragon.io/
- Tetragon GitHub repository: https://github.com/cilium/tetragon
- Falco docs: https://falco.org/docs/
- Inspektor Gadget docs: https://inspektor-gadget.io/docs/
- Source status: official runtime-security project docs and repositories.

## Finding

eBPF-based runtime security tools can observe process execution, file access, network activity, and system-call behavior near the kernel boundary. For NexusNet, this is a way to compare what an agent declared it would do with what actually happened.

## NexusNet Assimilation Target

Add a runtime-effect sensor lane for shell, browser, code, and tool execution. The sensor should produce a compact observed-effects digest that policy gates and incident reports can compare against declared effects.

## Proposed NexusNet Components

- `RuntimeEffectSensor`: platform adapter for process, file, network, and syscall observations.
- `SyscallEventDigest`: compressed per-run evidence of observed effects.
- `DeclaredObservedDiff`: compares declared tool effects to observed runtime behavior.
- `PolicyViolationAlert`: blocks or escalates undeclared sensitive effects.
- `ForensicRunBundle`: sanitized evidence package for debugging unsafe runs.

## Promotion Gates

- Bind process trees and containers to NexusNet run ids.
- Keep raw telemetry local and redacted by default.
- Start in observe-only mode before blocking production runs.
- Test with tools that attempt undeclared network, file, and process effects.
- Provide OS-specific capability notes, especially for Windows support gaps.

## Risks

- eBPF is primarily a Linux primitive; Windows/macOS need different sensors.
- Low-level telemetry can be noisy and privacy-sensitive.
- Enforcement can break legitimate tools if process attribution is wrong.
