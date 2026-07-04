# Frontier Small Model Training Spec

Status: candidate assimilation target. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_Everything-I-Learned-Training-Frontier-S_Media_fLUtUkqYHnQ_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/01-frontier-training-lessons/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

## Target Pattern

The video is a high-value target for NexusNet because it treats small/edge models as a distinct design problem, not as crippled frontier models. The useful pattern is a disciplined edge-model lifecycle:

- train or select small models for bounded tasks;
- separate data extraction, structured output, tool use, knowledge recall, and code generation;
- benchmark against the target device and runtime;
- post-train with task-specific SFT, preference alignment, and reinforcement learning where justified;
- certify by lane, not by global model reputation.

## External Confirmation

- LiquidAI's LFM2.5-350M model card describes an on-device 350M model with 28T-token training budget, 32K context, local deployment formats, and a recommendation toward structured outputs/tool use instead of knowledge-intensive programming: https://huggingface.co/LiquidAI/LFM2.5-350M
- LiquidAI's LFM2.5 blog positions the family around on-device deployment, open-weight use, and hardware support across local runtimes: https://www.liquid.ai/blog/introducing-lfm2-5-the-next-generation-of-on-device-ai

## NexusNet Use

Build this as `edge-small-model-certification`, not as a new default model. The lane should improve:

- `nexus/models/__init__.py` for model registry metadata and per-task suitability.
- `nexusnet/core/model_ingestion.py` for attaching local/edge models with explicit constraints.
- `nexusnet/runtime/model_tier_assignment.py` for tier assignment by task and device fit.
- `nexusnet/runtime/quantization/catalog.py` for GGUF/ONNX/OpenVINO/MLX style deployment variants.
- `nexusnet/growth/` and `tests/test_hive_model_growth_engine.py` for governed growth/training candidates.
- Existing docs in `docs/liquid_efficiency_assimilation.md` as the prior Liquid lane.

## Spec Requirements

- Model passport fields: parameter count, active parameter count when applicable, context, quantization, runtime formats, memory budget, latency envelope, task strengths, task refusals.
- Certification scenarios: extraction, tool call formatting, short RAG answer, local preference recall, no-answer/uncertainty, and adverse prompt stability.
- Device matrix: desktop CPU, local GPU if present, mobile/edge target where available, memory ceiling, prefill/decode speed, cold-start time.
- Training record: source data class, license status, privacy class, SFT plan, preference plan, RL plan, held-out eval set, and rollback artifact.
- Teacher role: use strong teachers for evaluation and distillation, but keep the child model's deployment claim bounded to its certified tasks.

## Refusals

- Do not promote a small model because a benchmark headline looks strong.
- Do not use small edge models for high-stakes factual recall unless retrieval and claim verification are active.
- Do not bypass the existing fine-tune decision gate or artifact trust registry.

## Acceptance Criteria

- A candidate edge model can be ingested with a passport and assigned to task-specific tiers.
- Certification produces a signed or trust-scanned artifact with benchmark deltas and blocked-use labels.
- Control Panel exposes the lane state, latest certification artifact, latency/memory proof, and disallowed tasks.
- Regression tests prove that knowledge-intensive prompts route to retrieval/teacher support rather than small-model guessing.

