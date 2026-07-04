# ADR: Optional Nemotron Omni Teacher Adapter

Date: 2026-05-03

Status: accepted for shadow teacher evidence

## Context

NVIDIA Nemotron 3 Nano Omni is a multimodal model positioned for unified video, audio, image, and text reasoning in agentic systems. NexusNet already has a brain-first direction with routed experts, Mini-NexusNets, teacher/dream/foundry evidence, hardware-aware runtime selection, and governed promotion.

## Decision

Add Nemotron Omni as an optional auxiliary teacher under the `multimodal-professor` subject. It can produce structured teacher evidence packets for NexusNet, but it cannot replace the core brain or mutate active production.

## Consequences

- Multimodal teacher evidence can enter the Hive substrate as governed shadow evidence.
- The locked 19 live expert pairs remain unchanged.
- Production use remains blocked until license, hardware, privacy, sandbox, benchmark, and operator approval gates pass.
- The adapter is contract-only and does not launch inference in v0.

## Non-Goals

- No primary brain replacement.
- No automatic teacher promotion.
- No automatic model download.
- No remote inference without explicit provider and privacy approval.

