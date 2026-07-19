# nanochat Constrained-Hardware Reference Spec

Status: primary-verified reference assimilation target. Checked on 2026-07-14.

Source:

- Video review: `https://youtu.be/0jcJigwk_Xc`
- Primary implementation: `https://github.com/karpathy/nanochat`
- Local evidence: `video-watch-output/0jcJigwk_Xc/0jcJigwk_Xc_20260714_164307/`

## Target Pattern

nanochat is a small, readable end-to-end LLM training and evaluation harness. Its constrained-hardware value is not a new NexusNet runtime. The patterns to assimilate are explicit hardware-aware compute dtype selection, reducing the device-local batch to remain within memory, maintaining comparable experiments through accumulation or other bounded work scheduling, and recording quality, throughput, and memory evidence together.

## NexusNet Use

Use this target as a reference for the existing `hardware_profile`, `inference_evolution`, and `dream_lab` surfaces. A candidate experiment must describe the detected hardware, precision, memory budget, workload envelope, measured throughput, and quality/equivalence evidence. The system may explore these candidates during downtime, but promotion remains approval-gated and does not modify model weights or select an unverified runtime route.

## Required Controls

- Device-aware precision is selected only when the detected hardware supports it and the selected runtime reports the effective dtype.
- Every experiment declares a memory-budget envelope and records refusal/degraded status instead of silently exceeding it.
- Reproducible experiment contracts contain workload, runtime, model fingerprint, hardware profile, and measured evidence.
- Quality/equivalence and throughput evidence are recorded together; throughput alone cannot promote a candidate.
- Promotion is shadow-certification first and requires explicit approval before any quality-altering or native-runtime action.

## Refusals

- Do not add nanochat as a NexusNet runtime dependency.
- Do not import nanochat model weights or represent its training results as a general inference certification.
- Do not infer consumer-hardware suitability from a cloud-GPU result without hardware-local evidence.
- Do not promote a lower-memory configuration when it degrades verified output quality or violates a model/runtime compatibility constraint.

## Acceptance Criteria

- The video assimilation scorecard exposes the target and source reference.
- The target identifies hardware profiling, inference evolution, and the dream lab as its only NexusNet surfaces.
- The target remains `shadow_certification` with approval-gated promotion.
