# AITune Supported Lane

## Purpose
AITune remains an optional, environment-gated QES autotuning lane. This document defines the supported validation lane without changing default Windows plus Python 3.13 development behavior.

## Supported Lane
- Platform: Linux
- GPU: NVIDIA required
- Python: `< 3.13`
- PyTorch: required for PyTorch-native modules and pipelines

## Status Model
- `skipped`: current host is unsupported or intentionally skip-safe
- `simulated-supported-lane`: the current host cannot run live AITune, but the supported-lane flow was exercised in dry-run mode
- `validation-ready`: current host can execute the supported lane
- `ready-on-supported-host`: current host cannot execute, but the validation runner and matrix are ready for a supported Linux plus NVIDIA environment

## Runner Contract
- Preferred runner:
  - `python -m nexusnet.runtime.qes.aitune_runner --model <model_id>`
- Mock or dry-run runner:
  - `python -m nexusnet.runtime.qes.aitune_runner --model <model_id> --simulate --json`
- Expected artifacts:
  - health report
  - execution plan
  - execution plan markdown
  - validation report
  - runner report
  - benchmark evidence
  - tuned artifact metadata
  - execution-plan artifact path
  - execution-plan markdown path
  - runner artifact path
  - benchmark artifact path
  - tuned-artifact artifact path

## Reproducible Host Plan
- Preflight commands:
  - `python -c "import sys,platform; print(platform.platform()); print(sys.version)"`
  - `python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.device_count())"`
  - `nvidia-smi`
- Artifact collection:
  - `find runtime/artifacts/runtime/aitune -maxdepth 3 -type f`
- The runner now emits both:
  - a machine-readable execution-plan artifact
  - a markdown execution-plan artifact that can be handed directly to a supported Linux plus NVIDIA operator

## Execution Modes
- `skip-safe`: default for unsupported Windows plus Python 3.13 or non-NVIDIA hosts
- `simulate`: dry-run the supported-lane workflow without pretending the host is actually supported
- `live`: run the real AITune adapter path on a supported Linux plus NVIDIA host when config allows live invocation

## Read-Only Inspection
- Wrapper, ops, and visualizer surfaces now expose:
  - supported-lane readiness
  - provider health
  - latest validation status
  - validation artifact IDs
  - latest execution-plan, runner, benchmark, and tuned-artifact IDs
  - execution-plan markdown path
  - skip reasons when the host remains unsupported

## Current Unsupported-Host Proof
The current Windows plus Python 3.13 host was exercised through the supported-lane simulate path:
- command:
  - `python -m nexusnet.runtime.qes.aitune_runner --project-root . --model transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0 --simulate --json`
- observed mode:
  - `simulated-supported-lane`
- observed artifact families:
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-health_*.json`
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-execution-plan_*.json`
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-benchmark_*.json`
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-tuned-artifact_*.json`
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-validation_*.json`
  - `runtime/artifacts/runtime/aitune/transformers-tinyllama-tinyllama-1.1b-chat-v1.0/aitune-runner_*.json`
- observed skip-safe reasons:
  - feature flag disabled
  - provider config disabled
  - package absent
  - Python 3.13 unsupported
  - Windows unsupported

## Boundaries
- Never replaces vLLM, llama.cpp, ONNX Runtime GenAI, or TensorRT-LLM where those are already the better fit.
- Never becomes mandatory for startup.
- Unsupported environments must stay graceful and skip-safe.
