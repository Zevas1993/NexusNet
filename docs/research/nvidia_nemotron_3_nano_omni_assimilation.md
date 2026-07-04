# NVIDIA Nemotron 3 Nano Omni Assimilation

Date: 2026-05-03

Status: optional teacher/perception adapter
Source reverified: 2026-05-31, see `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`

## Decision

NexusNet assimilates NVIDIA Nemotron 3 Nano Omni as an optional multimodal teacher and perception sub-agent reference. It is not a replacement for the NexusNet brain, Mixtral + Devstral + NexusNet fusion path, Mini-NexusNet hierarchy, or Hive Neural Substrate.

## Source Evidence

- NVIDIA technical blog, 2026-04-28: https://developer.nvidia.com/blog/nvidia-nemotron-3-nano-omni-powers-multimodal-agent-reasoning-in-a-single-efficient-open-model/
- Hugging Face model card: https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16

Repo-confirmed facts from the sources:

- Unified video, audio, image, and text inputs with text output.
- 31B total parameter Mamba2-Transformer hybrid MoE backbone with about 3B active parameters per token.
- Maximum context length up to 256k tokens.
- Vision uses C-RADIOv4-H; audio uses Parakeet.
- The model card lists BF16, FP8, and NVFP4 variants.
- Use is governed by the NVIDIA Open Model Agreement.

2026-05-31 reverify note: the NVIDIA technical blog and Hugging Face model card remain reachable and still support the optional teacher/perception posture. The source check confirms the multimodal sub-agent framing, but the NVIDIA Open Model Agreement, hardware/runtime profile, privacy review, and benchmark evidence remain blocking gates before any production teacher use.

## NexusNet Role

NexusNet should use Nemotron Omni as:

- Multimodal perception teacher.
- Document intelligence teacher.
- Video/audio reasoning teacher.
- GUI reasoning teacher.
- Dream-seed and foundry-training candidate generator.

NexusNet should not use Nemotron Omni as:

- Primary brain replacement.
- Ungated production teacher.
- Silent model swap.
- Active route mutator.

## Implementation Boundary

The v0 implementation is contract-only:

- `nexusnet/teachers/adapters/nemotron_omni_adapter.py` defines a guarded adapter contract.
- `nexusnet/teachers/teacher_registry_v2026_live.yaml` registers an auxiliary `multimodal-professor` path.
- Evidence packets are accepted into core only when license status is approved, hardware profile is reviewed, and an operator approval ref exists.
- Raw inputs are never stored in the evidence packet.

## Promotion Gates

Before production use, NexusNet must complete:

- NVIDIA Open Model Agreement license review.
- Hardware/runtime profile for BF16, FP8, or NVFP4.
- Privacy review for local and remote inference.
- Sandbox execution proof.
- Teacher evidence validation.
- Benchmark evidence across document, OCR/chart, video/audio, GUI, and ASR tasks.
- Human/governance approval.
