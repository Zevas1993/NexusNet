# Hardware-Aware Core Execution

## Goal
HardwareScanner and QES/runtime planning now feed the actual brain path instead of living only in side infrastructure.

## Inputs
- RAM and VRAM availability
- GPU summary when available
- thermal posture placeholder
- safe-mode inference
- long-context host cap
- runtime availability from the registry
- QES policy config

## Core Outputs
- `device_profile`
- `token_budget_profile`
- runtime candidates
- quantization decision
- selected runtime
- safe-mode fallback signal
- long-context profile
- execution-policy runtime bias used by the brain before model attachment

## Long Context
- The implementation line preserves the 1,000,000-token ambition.
- The host profile reports a bounded cap for the current machine.
- Safe hosts degrade to bounded-long-context behavior instead of pretending million-token execution is already available.

## Local-First Behavior
- Safe mode preserves local-first fallback.
- Safe mode does not disable the policy engine; it bounds native behavior to teacher-fallback-safe planning.
- Windows / Python 3.13-safe behavior is maintained.
- No cloud-only control plane is introduced.

## Files
- `nexusnet/runtime/hardware_scanner.py`
- `nexusnet/runtime/adaptive_system_profiler.py`
- `nexusnet/runtime/registry.py`
