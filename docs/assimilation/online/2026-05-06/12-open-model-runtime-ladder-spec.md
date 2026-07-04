# Open Model Runtime Ladder Spec

Status: P1 online assimilation target. Research-only until local runtime testing.

## Source Evidence

- Qwen3-Coder-Next paper: https://arxiv.org/abs/2603.00729
- Gemma 4 official release: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- Gemma 4 MTP release: https://blog.google/innovation-and-ai/technology/developers-tools/multi-token-prediction-gemma-4/
- Gemma 4 edge developer guide: https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/
- LFM2.5-350M release: https://www.liquid.ai/blog/lfm2-5-350m-no-size-left-behind
- MiniCPM5-1B-GGUF model card: https://huggingface.co/openbmb/MiniCPM5-1B-GGUF
- Keye-VL-2.0-30B-A3B model card: https://huggingface.co/Kwai-Keye/Keye-VL-2.0-30B-A3B
- Source status: primary model/paper/release pages.
- Reverified: 2026-05-31 via `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`.

## Finding

The open-first model landscape is moving toward efficient active-parameter MoE coding models, edge-ready multimodal models, tiny tool-use/data-extraction models, speculative decoding, and broad inference-engine support. The 2026-05-31 reverify adds MiniCPM5-1B-GGUF as a compact local/edge worker candidate and Keye-VL-2.0-30B-A3B as a conditional multimodal video-temporal teacher candidate. This reinforces NexusNet's need for model passports, runtime certification, quantization checks, and task-specific routing rather than one default model.

## NexusNet Assimilation Target

Refresh the open model/runtime ladder with distinct roles: tiny extraction/tool-use models, edge multimodal models, local coding experts, large offline planners, and premium fallback models. Each model should carry license, active parameters, context, supported modalities, tool-calling support, quantization formats, and known failure modes.

## Proposed NexusNet Components

- `OpenModelCandidatePassport`: license, source, weights, active params, context, modalities, runtime support, and local artifact status.
- `RuntimeFitScore`: estimates CPU/GPU/NPU/VRAM fit and expected task class.
- `SpeculativeDecodingCapability`: records target/drafter compatibility and quality-verification contract.
- `TaskSpecificityRouter`: maps extraction, tool call, coding, planning, multimodal, and document tasks to model tiers.

## Promotion Gates

- Verify license and weight availability before adding a model to recommended routes.
- Run local smoke tests before marking any model as usable on this machine.
- Separate open weights from free compute; both matter for product planning.
- Keep small local workers, multimodal teachers, and primary reasoning routes as separate roles; do not silently swap a teacher or edge worker into the brain path.
- Avoid general factual QA claims for models intended for extraction/tool calls.

## Risks

- Model leaderboards and availability drift quickly.
- Vendor release claims need local validation.
- Edge support can depend on specific hardware, quantization, and runtime versions.
