# AITune Assimilation

## Canon Status
- NexusNet runtime/QES spine: `LOCKED CANON`
- AITune assimilation lane: `EXPLORATORY / PROTOTYPE`

## Purpose
AITune is integrated as an optional subordinate QES/runtime autotuning lane for PyTorch-native modules and pipelines. It does not replace the canonical NexusNet runtime stack, and it never overrides dedicated serving backends when those are already the correct fit.

## Where AITune Fits
Repo audit results:

- Good insertion points:
  - `core/engines/transformers_engine.py`
  - `nexusnet/vision/edge_vlm`
  - `nexusnet/distillation`
  - `nexusnet/foundry`
- Avoided lanes:
  - `llama.cpp` / GGUF
  - `vLLM`, `SGLang`, `TensorRT-LLM`, and similar dedicated serving stacks
  - `onnx-genai` portable runtime lanes
  - default Windows / Python 3.13 developer flows where AITune is unsupported

## Integration Shape
- `BrainRuntimeRegistry` now owns an optional `AITuneQESProvider`.
- QES treats AITune as one optimization provider, not as the primary runtime backend selector.
- Runtime summaries expose:
  - AITune environment compatibility
  - bounded applicability for the selected model
  - target-registry IDs and repo fit/avoid audit state
  - feature/config gating
- Backend benchmarks expose:
  - normal runtime benchmark matrix records
  - a separate `aitune` result payload with compatibility, applicability, artifacts, rollback reference, and any tuned records if a supported environment actually completes tuning
- Wrapper and ops inspection surfaces expose:
  - compatibility and applicability state
  - target registry metadata
  - repo audit fit/avoid guidance

## Environment Gating
AITune is marked unavailable unless all of the following are true:

- feature flag `features.runtime.aitune` is enabled, or `NEXUS_ENABLE_AITUNE=1`
- `runtime/config/aitune.yaml` enables the provider
- Python is within the supported `< 3.13` range
- platform is in the allowlist, currently Linux-focused
- PyTorch is available
- an NVIDIA GPU path is detectable when required
- the `aitune` package is importable

If any of those fail, NexusNet continues through existing runtime paths without breaking startup or inference.

## Bounded Applicability
AITune only considers PyTorch-native lanes by default.

- Allowed by default:
  - `transformers` runtime
  - explicit target-registry entries for:
    - `transformers-text`
    - `edge-vision-lane`
    - `teacher-foundry-helpers`
  - future repo-local PyTorch helper modules matched by configured target hints
- Explicitly blocked:
  - `llama.cpp`
  - `vllm`
  - `onnx-genai`
  - `ollama`
  - `lmstudio`
  - `openai-compatible`
  - `mock`
  - blocked quantization profiles such as `gguf`

## Artifacts And Rollback
AITune writes additive metadata artifacts under `runtime/artifacts/runtime/aitune/`:

- compatibility reports
- benchmark reports
- tuned-artifact metadata when a live invoke path completes

Each result records:

- source model and runtime
- selected AITune backend where applicable
- environment compatibility
- host-specific vs portable expectation
- rollback reference back to the canonical runtime lane

## Promotion Discipline
AITune-tuned artifacts do not become active automatically.

- AITune benchmark records only become runtime-profile promotion candidates through the existing promotion path.
- Candidate creation remains shadow-first.
- EvalsAO, governance, and rollback requirements remain in force.
- If AITune is unavailable or benchmark-gated, NexusNet simply records a skipped AITune result and continues.

## Current Default Behavior
In the current Windows / Python 3.13 developer environment, AITune should normally appear as disabled or incompatible. This is expected and intentional. The assimilation lane is present, measurable, and safely skipped until a supported environment is provided.
