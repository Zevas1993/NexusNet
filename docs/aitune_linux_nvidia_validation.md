# AITune Linux NVIDIA Validation

## Goal
Provide a clean execution path for future live AITune validation on supported Linux plus NVIDIA hosts while preserving current unsupported environments.

## Host Expectations
- Ubuntu 22.04 or newer recommended
- NVIDIA driver and CUDA-visible devices
- Python 3.12 or earlier
- PyTorch with CUDA support
- `aitune` importable in the validation environment

## Container / Devcontainer Guidance
- Base on Linux, not Windows.
- Expose NVIDIA devices and CUDA libraries to the container runtime.
- Keep Windows plus Python 3.13 host development flows outside the AITune lane.

## CI Guidance
- Run live AITune validation only on Linux plus NVIDIA runners.
- Keep unsupported CI jobs in skip-safe or mock validation mode.

## Validation Outputs
- capability status
- skip reason if unsupported
- supported-lane readiness
- health report
- execution plan
- execution plan markdown
- execution-plan artifact
- tuned artifact metadata
- tuned-artifact metadata artifact
- host-specific vs portable flags
- rollback references
- benchmark evidence
- benchmark artifact
- runner report
- preflight command set
- artifact-collection command set

## Recommended Commands
- Dry-run from any host:
  - `python -m nexusnet.runtime.qes.aitune_runner --model transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0 --simulate --json`
- Live validation from a supported Linux plus NVIDIA host:
  - `python -m nexusnet.runtime.qes.aitune_runner --model transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0 --json`

## Expected Artifact Families
- `health`
- `execution-plan`
- `execution-plan-markdown`
- `validation`
- `runner`
- `benchmark`
- `tuned-artifact`

## Execution Plan Artifact Expectations
The supported-lane runner now emits a reproducible execution-plan artifact even on unsupported hosts. That plan should be treated as the handoff object for the future Linux plus NVIDIA lane and should include:
- model ID
- target lane
- simulate/live intent
- required host characteristics
- explicit preflight commands
- explicit artifact-collection commands
- execution modes
- docs and operator guidance
- provider health at time of planning
