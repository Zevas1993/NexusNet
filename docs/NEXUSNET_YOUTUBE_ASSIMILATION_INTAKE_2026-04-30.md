# NexusNet YouTube Assimilation Intake - 2026-04-30

Status: candidate assimilation intake. This document does not change locked canon by itself.

Primary canon anchor:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- `docs/SELF_IMPROVEMENT_LAYER.md`
- `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`

Purpose:

This intake reviews the YouTube transcript packet supplied by the operator and maps the useful patterns into NexusNet candidate lanes. The goal is to identify what should improve NexusNet without prematurely promoting vendor claims, promotional claims, or uncontrolled self-training into canon.

Core rule:

NexusNet can assimilate these ideas only through governed candidate lanes: provenance, privacy, license checks, evals, rollback, and Control Panel visibility.

---

## Source Packet

| ID | User-supplied video | Main pattern | NexusNet disposition |
| --- | --- | --- | --- |
| YT-01 | https://www.youtube.com/watch?v=jB3yKR6bOjQ | Local browser AI agent, offline tab/history/page reasoning, edge privacy | Assimilate as Browser AO / Local Browser Memory Agent candidate. |
| YT-02 | https://www.youtube.com/watch?v=9YYUzA5ZnDo | Agentic pipelines with blocks, events, manifests, gates, profiles, artifacts | Assimilate as Agentic Pipeline Runtime candidate. |
| YT-03 | https://www.youtube.com/watch?v=X2SVUeQwdI8 | Policy-as-code as deterministic guardrail under nondeterministic AI development | Assimilate as Policy Kernel candidate. |
| YT-04 | https://www.youtube.com/watch?v=mREHBZQbhBo | Bespoke repo-specific pipelines instead of generic AI factories | Assimilate as Pipeline Recipe / Worktree Governance candidate. |
| YT-05 | https://www.youtube.com/watch?v=YJCe8hvZrxs | Agent platform landscape, brain/hands split, memory lock-in risk | Assimilate as Harness Provider Registry / Brain-Hands Decoupling candidate. |
| YT-06 | https://www.youtube.com/watch?v=5Z2HBJTUNik | Hybrid cloud/local AI, local inference for private data and edge workloads | Assimilate as Edge Workload Router candidate. |
| YT-07 | https://www.youtube.com/watch?v=v7qMjy_RxOs | Local LoRA/QLoRA fine-tuning, dataset engineering, eval, GGUF deployment | Assimilate as governed Adapter Forge / Training Candidate pipeline. |

---

## Evidence Summary

### YT-01 - Browser AO / local page intelligence

Transcript claims:

- A local browser extension can search open tabs, history, and the current page using an edge model.
- Browser-local AI improves privacy and latency because browsing context does not need to leave the device.
- Edge-optimized open models make browser and device-side agents more practical.

External confirmation:

- Google announced Gemma 4 as an open-model family with edge-oriented variants and agentic/reasoning emphasis: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- The referenced community browser assistant exists as a public repository: https://github.com/nico-martin/gemma4-browser-extension
- Transformers.js is the relevant JavaScript/browser runtime family for local model execution: https://huggingface.co/docs/transformers.js

Candidate assimilation:

- Add a Browser AO that can read local browser context through explicit user permission.
- Keep the Browser AO local-first, private by default, and auditable.
- Do not let browser history ingestion auto-promote to memory. Browser-derived facts should become ImprovementEvents first.

Promotion gates:

- Permission envelope for tabs/history/current page.
- PII and secrets filter.
- Per-source provenance.
- Browser event trace in Control Panel.
- Offline mode proof using a small local model.

---

### YT-02 and YT-04 - Agentic Pipeline Runtime

Transcript claims:

- Durable agentic development needs pipelines, not one long unstructured chat.
- Useful pipeline building blocks include manifests, fresh subprocesses, isolated worktrees, events, gates, profiles, adapters, and artifacts on disk.
- Repo-specific pipelines outperform generic "factory" recipes because each codebase has its own constraints.

External confirmation:

- OpenAI Agents SDK now exposes a stronger agent harness with sandbox/workspace patterns: https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- Anthropic's managed agents post formalizes a brain/hands separation for hosted agent execution: https://www.anthropic.com/engineering/managed-agents
- LangChain Deep Agents Deploy positions deployment around agent orchestration, memory, sandboxes, and protocols: https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/ and https://docs.langchain.com/oss/python/deepagents/deploy

Candidate assimilation:

- Add an Agentic Pipeline Runtime that produces a structured run ledger instead of opaque agent sessions.
- Each pipeline run should have a manifest, planned steps, roles, artifacts, gate outcomes, events, costs, and operator-visible status.
- Pipeline recipes should be repo/canon-specific, not a universal template.

Promotion gates:

- Pipeline run schema.
- Event ledger API.
- Deterministic gate contract.
- Branch/worktree ownership metadata.
- Control Panel page for active and historical pipelines.

---

### YT-03 - Policy-As-Code Governance Kernel

Transcript claims:

- AI-generated code drifts even when instructions and rules exist.
- Deterministic checks should form a hard floor under nondeterministic agent behavior.
- Policy rules can govern architecture, imports, UI boundaries, docs requirements, tests, exceptions, and observability.

External confirmation:

- Policy-as-code for AI-generated software is an active research direction, including PCAS-style enforcement of software policies: https://arxiv.org/abs/2602.16708
- The broader industry direction around agentic pipelines also emphasizes gates, traces, sandboxes, and reviewable harnesses.

Candidate assimilation:

- Add a NexusNet Policy Kernel as a first-class governance system, not just lint.
- Policies should be machine-readable, versioned, waiver-aware, and Control Panel visible.
- Policies should apply to code, tools, data, memory promotion, training candidates, and autonomous updates.

Promotion gates:

- Policy rule schema.
- Policy scan report.
- Waiver ledger with owner, reason, expiry, and audit trail.
- Hard-fail vs warning tiering.
- Regression tests showing at least one blocked anti-pattern.

---

### YT-05 - Harness Provider Registry / brain-hands split

Transcript claims:

- Agent platforms fall across a build-to-buy spectrum: custom code, SDK/framework, managed infrastructure, visual low-code, and embedded SaaS agents.
- Managed agent infrastructure can create lock-in through memory, harnesses, and runtime assumptions.
- "Brain" orchestration and "hands" execution should be separable.

External confirmation:

- Anthropic documents managed agent infrastructure and brain/hands separation: https://www.anthropic.com/engineering/managed-agents
- LangChain argues for an open alternative around deep agents, memory, sandboxes, and protocols: https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/
- OpenAI's Agents SDK announcement positions the SDK as a harness option with sandbox/workspace support while leaving deployment choices to builders: https://openai.com/index/the-next-evolution-of-the-agents-sdk/

Candidate assimilation:

- Add a Harness Provider Registry that scores each provider by model control, memory portability, sandbox model, local/offline support, protocol support, privacy, cost, and lock-in.
- Keep NexusBrain as authority. External harnesses should be adapters, not the core brain.
- Persist memory in NexusNet-owned stores unless the operator deliberately opts into a managed provider.

Promotion gates:

- Provider scorecard schema.
- Lock-in risk labels.
- Memory export/import test.
- Credential vault separation.
- Control Panel provider trust envelope.

---

### YT-06 - Edge Workload Router

Transcript claims:

- Local AI does not need to beat cloud AI for every task to be valuable.
- Strong local use cases include private transcription, document processing, vision, proprietary code assistance, and air-gapped or regulated workloads.
- Hybrid cloud/local routing is the practical path: use frontier cloud models for complex reasoning and local models for private, high-volume, latency-sensitive, or offline work.

External confirmation:

- Edge AI remains a large and growing market category: https://www.grandviewresearch.com/industry-analysis/edge-ai-market-report
- Google Cloud air-gapped appliance work demonstrates a concrete tactical-edge deployment lane: https://www.gdit.com/about-gdit/press-releases/gdit-successfully-demonstrates-google-cloud-air-gapped-appliance-at-the-tactical-edge/
- Whisper and faster-whisper style local ASR remain practical local workload anchors: https://github.com/openai/whisper and https://github.com/SYSTRAN/faster-whisper

Candidate assimilation:

- Add an Edge Workload Router that decides whether a task belongs on local CPU, local GPU, browser WebGPU/WebNN, Android/NPU, WSL GPU, or cloud/API.
- Treat privacy, data gravity, latency, hardware fit, cost, and model quality as explicit routing factors.
- Feed routing outcomes into the Control Panel and Self-Improvement Layer.

Promotion gates:

- Workload classification schema.
- Hardware capability snapshot.
- Cost/privacy/latency scoring.
- Local-vs-cloud explainability.
- Route regression tests.

---

## YT-07 - Fine-Tuning / Adapter Forge Intake

This video adds a missing practical lane: NexusNet should not only capture training candidates, it should have a governed path from experience data to adapter artifacts.

### Claims Worth Assimilating

1. Fine-tuning is different from prompting and RAG.

Fine-tuning changes behavior in model weights or adapters. RAG injects retrieved knowledge at inference time. Prompting changes only the current instruction context. NexusNet should use this distinction as a routing gate:

```text
Try prompt/policy change first
        ->
Try memory/RAG retrieval if the problem is missing or changing knowledge
        ->
Try agentic workflow if the problem is planning/tool use
        ->
Create a fine-tuning candidate if the problem is stable behavior, style, format, domain routine, or tool-use habit
```

2. LoRA/QLoRA should be the default first training mechanism.

External confirmation:

- LoRA freezes pretrained weights and trains low-rank adapter matrices, reducing trainable parameters and memory needs: https://arxiv.org/abs/2106.09685
- QLoRA backpropagates through a frozen 4-bit quantized model into LoRA adapters and showed 65B fine-tuning on a single 48GB GPU in the paper setting: https://arxiv.org/abs/2305.14314
- Hugging Face PEFT documents adapter-based fine-tuning, including LoRA support in Transformers: https://huggingface.co/docs/transformers/peft

NexusNet implication:

- Add adapter-first training, not full-weight training, as the first promoted path.
- Keep base model weights, adapter artifacts, and deployment quantizations separately registered.
- Do not merge adapters into deployable artifacts until eval and rollback metadata are preserved.

3. Dataset engineering is the hard part.

Transcript claims:

- Raw transcripts are not enough.
- Data should be cleaned, converted into task-aligned prompt/response or chat examples, split into training/validation/test sets, and evaluated.
- Synthetic question generation can transform raw text into supervised examples.

External confirmation:

- Self-Instruct demonstrates a pipeline that generates instructions, inputs, and outputs, filters them, and fine-tunes on the result: https://arxiv.org/abs/2212.10560
- LIMA shows that carefully curated data can matter more than raw quantity for alignment behavior: https://arxiv.org/abs/2305.11206
- Hugging Face TRL documents dataset formats for language-modeling, prompt-completion, preference, conversational, and vision datasets: https://huggingface.co/docs/trl/main/en/dataset_formats

NexusNet implication:

- Add a Dataset Forge candidate subsystem:
  - source capture
  - transcript/document cleanup
  - segmentation
  - prompt/response synthesis
  - deduplication
  - privacy filtering
  - license filtering
  - train/validation/test splitting
  - eval case generation
  - dataset manifest creation

4. Evaluation must come before promotion.

Transcript claims:

- A fine-tuned model can appear better stylistically while regressing on reliability.
- Evaluation can identify whether failures came from data formatting, training configuration, or model limits.

NexusNet implication:

- Fine-tune candidates must pass a regression gate before becoming active.
- Evals should compare base model vs adapter vs merged/quantized export.
- NexusNet should measure task quality, style adherence, refusal/safety behavior, factual grounding, tool-calling reliability, latency, memory use, and cost.

5. GGUF export is a deployment path, not the training source of truth.

External confirmation:

- llama.cpp has a `convert_lora_to_gguf.py` path: https://github.com/ggml-org/llama.cpp/blob/master/convert_lora_to_gguf.py
- Unsloth documents saving/deployment paths for LoRA adapters and GGUF/llama.cpp/LM Studio/Ollama workflows: https://unsloth.ai/docs/get-started/fine-tuning-llms-guide
- MLX-LM can fine-tune LoRA/QLoRA on Apple Silicon and can fuse/export supported models to GGUF with limitations: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md

NexusNet implication:

- NexusNet should track at least three artifact classes:
  - base model source: safetensors, MLX, GGUF, ONNX, etc.
  - adapter source: PEFT/LoRA adapter, MLX adapter, other adapter format
  - deployment artifact: merged safetensors, GGUF, AWQ/GPTQ/FP8/NVFP4, MLX, vLLM-compatible package

6. Hardware reality matters.

Transcript claims:

- NVIDIA/CUDA is the easiest path for training.
- AMD/ROCm is viable but more compatibility-sensitive.
- Apple Silicon is good for local inference but can be slower or format-limited for training.

External confirmation:

- AMD ROCm provides an AI/HPC GPU stack and PyTorch support across supported hardware: https://www.amd.com/en/products/software/rocm.html
- ROCm PyTorch training documentation explicitly covers fine-tuning/pretraining with optimized ROCm containers on AMD Instinct GPUs: https://rocm.docs.amd.com/en/develop/how-to/rocm-for-ai/training/benchmark-docker/previous-versions/pytorch-training-v25.11.html
- MLX-LM supports Apple Silicon generation, quantization, LoRA, full fine-tuning, and some GGUF export paths: https://github.com/ml-explore/mlx-lm

NexusNet correction:

- Do not encode "avoid Apple Silicon" as canon. The better rule is: NVIDIA/CUDA is the first training target; AMD/ROCm and Apple MLX are supported candidate lanes with explicit compatibility probes and narrower guarantees.

7. Qwen3.5 is real, but "latest" is unstable.

External confirmation:

- Qwen3.5-27B is available on Hugging Face and lists support for Transformers, vLLM, SGLang, KTransformers, and other serving paths: https://huggingface.co/Qwen/Qwen3.5-27B
- The Qwen GitHub news stream shows Qwen3.5 releases in February/March 2026 and Qwen3.6 releases in April 2026: https://github.com/QwenLM/Qwen3.5

NexusNet implication:

- Do not hardcode Qwen3.5 as "latest." Treat it as a candidate family with time-stamped model-card evidence.
- The model registry should pin model family, revision, license, source URL, supported runtimes, and known quantizations.

---

## New Candidate Lane: Adapter Forge

### Purpose

Adapter Forge is the governed NexusNet lane that turns approved learning material into trainable, testable, versioned LoRA/QLoRA adapters without allowing uncontrolled self-training.

### Relationship To Existing Self-Improvement Layer

The current Self-Improvement Layer already records training candidates but does not fine-tune. Adapter Forge should extend that spine:

```text
ImprovementEvent
    -> Triage
    -> TrainingCandidateBuilder
    -> Dataset Forge
    -> FineTune Planner
    -> Adapter Training Job
    -> Eval + Regression Gate
    -> Adapter Registry
    -> Shadow Deployment
    -> Promotion / Rollback
```

### Candidate Components

| Component | Responsibility |
| --- | --- |
| `DatasetForge` | Converts approved traces, transcripts, docs, and examples into trainable datasets with provenance. |
| `FineTuneDecisionGate` | Decides prompt vs RAG vs agent loop vs adapter training. |
| `TrainingRunManifest` | Records base model, data manifest, method, hyperparameters, hardware, cost, seed, and software versions. |
| `AdapterRegistry` | Tracks adapter artifacts, base model compatibility, license, provenance, evals, deployment status, rollback path. |
| `EvalHarness` | Compares base vs adapter vs deployment artifact. |
| `PromotionGate` | Blocks activation unless eval, privacy, license, and regression checks pass. |
| `ControlPanelAdapterForge` | Shows active adapters, candidates, training jobs, eval deltas, and rollback controls. |

### Recommended Schema Sketch

```json
{
  "adapter_id": "adapter_2026_04_30_code_ao_style_v1",
  "status": "candidate|training|evaluating|shadow|active|rejected|rolled_back",
  "base_model": {
    "model_id": "Qwen/Qwen3.5-27B",
    "revision": "pinned_commit_or_snapshot",
    "license": "declared_license",
    "source_url": "https://huggingface.co/Qwen/Qwen3.5-27B"
  },
  "method": {
    "type": "lora|qlora|full|dpo|grpo",
    "framework": "peft|trl|axolotl|unsloth|mlx-lm",
    "precision": "bf16|fp16|nf4|int4",
    "target_modules": ["q_proj", "v_proj"]
  },
  "dataset": {
    "dataset_manifest_id": "dataset_manifest_uuid",
    "source_count": 0,
    "example_count": 0,
    "token_count": 0,
    "contains_private_data": false,
    "license_status": "approved|blocked|needs_review"
  },
  "eval": {
    "base_score": 0.0,
    "adapter_score": 0.0,
    "regression_failures": [],
    "style_gain": 0.0,
    "grounding_delta": 0.0,
    "tool_call_delta": 0.0
  },
  "deployment": {
    "adapter_artifact": "path_or_uri",
    "merged_artifact": "path_or_uri",
    "gguf_artifact": "path_or_uri",
    "runtime_targets": ["vllm", "llama.cpp", "lm_studio", "ollama", "mlx"],
    "rollback_adapter_id": "previous_active_adapter_id"
  }
}
```

### What Adapter Forge Should Train First

Highest-value first targets:

1. AO writing/response style adapters for consistent role behavior.
2. Tool-calling format adapters for reliable JSON, function calls, and MCP/A2A protocol behavior.
3. Domain expert adapters where the domain knowledge is stable and licensing is clean.
4. Control Panel summarization and telemetry interpretation adapters.
5. Browser AO tab/history/page summarization style adapters.

Defer:

- Fine-tuning on raw private user logs.
- Fine-tuning on copyrighted/private material without clear rights.
- Fine-tuning medical/legal/financial authority without external review gates.
- Fully autonomous model-weight updates.
- Any adapter that weakens safety or governance behavior.

---

## Canon Impact Matrix

| NexusNet surface | Impact from this intake | Candidate update |
| --- | --- | --- |
| NexusBrain authority | External harnesses, browser agents, and training jobs must remain subordinate to NexusBrain | Add provider and adapter trust envelopes. |
| AO Hive | Each AO can have its own mini-adapter or training curriculum | Add per-AO adapter slots with eval gates. |
| Expert Hive | Domain experts can be improved by stable, licensed, task-specific adapters | Add expert adapter registry fields. |
| Self-Improvement Layer | Training candidates need a real downstream lane | Add Adapter Forge after TrainingCandidateBuilder. |
| Memory/RAG | RAG remains the first choice for dynamic facts | Add prompt/RAG/agent/fine-tune decision gate. |
| Governance | Policy-as-code should gate code, data, memory, and training | Add Policy Kernel as prerequisite for autonomous training. |
| Observability | Pipelines and training must emit events, manifests, and eval reports | Add pipeline/training event ledgers. |
| Runtime/Hardware | Training and deployment choices depend on CUDA, ROCm, MLX, GGUF, vLLM, etc. | Add hardware-aware training/deployment scorecards. |
| Control Panel | Operator needs cockpit visibility into all of this | Add Adapter Forge, Policy Kernel, Pipeline Runtime, Browser AO, and Edge Router panels. |

---

## Recommended Build Order

This is the order that preserves safety and usefulness.

1. Policy Kernel MVP

Build deterministic governance first so later agentic and training lanes have a hard floor.

Deliverables:

- Policy rule schema.
- Policy scan report.
- Waiver ledger.
- Control Panel policy scorecard.

2. Agentic Pipeline Ledger

Build the event/manifest/gate ledger so long-running NexusNet work is visible and replayable.

Deliverables:

- Pipeline run schema.
- Step/gate/event artifacts.
- API endpoints for active/history runs.
- Control Panel pipeline trace view.

3. Adapter Registry

Before training anything, register artifacts and promotion states.

Deliverables:

- Adapter metadata schema.
- Dataset manifest schema.
- Promotion/rollback status.
- API endpoint for adapter candidates.

4. Dataset Forge MVP

Implement data preparation without training first.

Deliverables:

- Source capture manifest.
- Cleanup/split pipeline.
- Prompt/response or chat example builder.
- Privacy/license filters.
- Eval case generation.

5. FineTune Decision Gate

Prevent premature fine-tuning.

Deliverables:

- Decision matrix for prompt vs RAG vs agent loop vs LoRA.
- Training-candidate review output.
- Regression blockers.

6. Adapter Forge Training CLI

Only after the above exists, add local LoRA/QLoRA dry-run training.

Deliverables:

- Dry-run estimator.
- Hardware compatibility check.
- PEFT/TRL or Axolotl/Unsloth plan export.
- No automatic weight update.

7. Control Panel Integration

Expose the whole lane to the human cockpit.

Deliverables:

- Adapter candidates.
- Training manifests.
- Eval deltas.
- Active/shadow/rollback state.
- Privacy and license status.

---

## Non-Assimilation / Watchlist

Do not promote these as confirmed canon:

- Any single video benchmark or hardware timing claim without reproducible local tests.
- "Qwen3.5 is latest" language, because Qwen3.6 releases are already visible by April 2026.
- "Apple Silicon cannot fine-tune" as a blanket rule. MLX-LM proves a viable lane, even if CUDA remains the first target.
- "Fine-tuning bakes in knowledge" as a replacement for RAG. Stable behavior and style are better fine-tune targets; changing knowledge stays retrieval-first.
- Training on raw transcripts, user sessions, or browser history without explicit rights, privacy classification, and review.
- Merged GGUF artifacts as the only source of truth. Keep original adapter and dataset manifests.

---

## Immediate NexusNet Decisions

Recommended decisions to promote to candidate registry:

1. Add `Adapter Forge` as a candidate subsystem under Self-Improvement and Model Registry.
2. Add a `FineTuneDecisionGate` before any training candidate becomes a job.
3. Treat LoRA/QLoRA as the first-class training path; defer full fine-tuning.
4. Keep RAG first for dynamic facts and fine-tuning first only for stable behavior, format, style, and task routines.
5. Require per-adapter provenance, data license, privacy classification, eval deltas, and rollback.
6. Add Control Panel visibility before enabling any actual training job.
7. Treat Qwen3.5/Qwen3.6, Gemma 4, LFM, Phi, Granite, Kimi, MiniMax, and other open models as registry candidates, not hardcoded truths.

---

## Source Index

User-supplied videos:

- https://www.youtube.com/watch?v=jB3yKR6bOjQ
- https://www.youtube.com/watch?v=9YYUzA5ZnDo
- https://www.youtube.com/watch?v=X2SVUeQwdI8
- https://www.youtube.com/watch?v=mREHBZQbhBo
- https://www.youtube.com/watch?v=YJCe8hvZrxs
- https://www.youtube.com/watch?v=5Z2HBJTUNik
- https://www.youtube.com/watch?v=v7qMjy_RxOs

External confirmation:

- Google Gemma 4: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- Gemma browser extension: https://github.com/nico-martin/gemma4-browser-extension
- Transformers.js: https://huggingface.co/docs/transformers.js
- Anthropic managed agents: https://www.anthropic.com/engineering/managed-agents
- LangChain Deep Agents Deploy: https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/
- LangChain Deep Agents Deploy docs: https://docs.langchain.com/oss/python/deepagents/deploy
- OpenAI Agents SDK announcement: https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- Policy-as-code for AI-generated software: https://arxiv.org/abs/2602.16708
- Edge AI market report: https://www.grandviewresearch.com/industry-analysis/edge-ai-market-report
- Google Cloud air-gapped appliance demonstration: https://www.gdit.com/about-gdit/press-releases/gdit-successfully-demonstrates-google-cloud-air-gapped-appliance-at-the-tactical-edge/
- Whisper: https://github.com/openai/whisper
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- LoRA paper: https://arxiv.org/abs/2106.09685
- QLoRA paper: https://arxiv.org/abs/2305.14314
- Hugging Face PEFT: https://huggingface.co/docs/transformers/peft
- Hugging Face TRL SFTTrainer: https://huggingface.co/docs/trl/v0.17.0/sft_trainer
- Hugging Face TRL dataset formats: https://huggingface.co/docs/trl/main/en/dataset_formats
- Axolotl method guide: https://docs.axolotl.ai/docs/choosing_method.html
- Unsloth fine-tuning guide: https://unsloth.ai/docs/get-started/fine-tuning-llms-guide
- llama.cpp LoRA to GGUF converter: https://github.com/ggml-org/llama.cpp/blob/master/convert_lora_to_gguf.py
- MLX-LM: https://github.com/ml-explore/mlx-lm
- MLX-LM LoRA guide: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md
- AMD ROCm: https://www.amd.com/en/products/software/rocm.html
- ROCm PyTorch training docs: https://rocm.docs.amd.com/en/develop/how-to/rocm-for-ai/training/benchmark-docker/previous-versions/pytorch-training-v25.11.html
- Qwen3.5-27B model card: https://huggingface.co/Qwen/Qwen3.5-27B
- Qwen release repository: https://github.com/QwenLM/Qwen3.5
- Self-Instruct: https://arxiv.org/abs/2212.10560
- LIMA: https://arxiv.org/abs/2305.11206
