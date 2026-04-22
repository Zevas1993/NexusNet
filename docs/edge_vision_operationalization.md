# Edge Vision Operationalization

## Canon
- The edge lane stays subordinate to the broader multimodal teacher system.
- `LFM2.5-VL-450M` remains an explicit candidate provider and low-power/safe-mode teacher reference.

## Operational Additions
- Config-backed benchmark cases for safe-mode, multilingual prompting, grounding, and function calling
- Grounding payload validation
- Function-calling validation
- Latency-profile evaluation
- Benchmark artifacts under `runtime/artifacts/vision/edge-bench/`

## Measured Readiness
- latency-profile fit
- grounding/schema correctness
- bounding-box validity
- multilingual prompt coverage
- function/tool calling readiness
- safe-mode suitability

## Inspection Surfaces
- `/ops/brain/vision/edge-lane`
- `/ops/brain/vision/edge-benchmark`
- `/ops/brain/wrapper-surface`
