# AITune Validation Matrix

## Canon
- AITune remains optional, bounded, and environment-gated.
- Unsupported Windows / Python 3.13 flows continue gracefully without startup or inference failure.

## Validation Dimensions
- Python compatibility
- platform compatibility
- NVIDIA availability
- import/install state
- target-registry applicability
- host-specific vs portable expectation
- rollback reference availability

## Current Scenarios
- `windows-py313-default`: expected skip
- `linux-nvidia-supported`: validation-ready
- `linux-cpu-no-nvidia`: expected skip

## Inspection Surfaces
- `/ops/brain/backends`
- `/ops/brain/aitune/validation`
- wrapper/runtime summaries
