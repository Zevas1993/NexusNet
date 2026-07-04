# Black Box Interpretability Plane Spec

Status: medium-high research candidate. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_Inside-The-Black-Box-Now-Read-the-Mind-o_Media_G1NBI3AW5Q_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/07-black-box-read-the-mind/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

## Target Pattern

The useful target is an interpretability-inspired safety plane, not a claim that NexusNet can read the mind of any model.

The video centers on the idea that some language-model features are not single straight-line directions in activation space. They may be multi-dimensional structures that sparse autoencoders approximate through local charts. For NexusNet, the right near-term transfer is a concept telemetry proxy and a later open-model SAE experiment lane.

## External Confirmation

- "Not All Language Model Features Are One-Dimensionally Linear" argues that some language-model representations are inherently multi-dimensional and uses sparse autoencoders to find such features in GPT-2 and Mistral 7B: https://arxiv.org/abs/2405.14860
- "Understanding sparse autoencoder scaling in the presence of feature manifolds" analyzes how feature manifolds affect SAE scaling and feature recovery: https://arxiv.org/abs/2509.02565

## NexusNet Use

Use two tiers.

Tier 1: Concept telemetry proxy, ship as governance/research metadata:

- `nexusnet/telemetry/genai_observability.py` for trace spans and attributes.
- `nexusnet/memory/engram_index.py` for concept clustering over observed traces.
- `nexusnet/evals/registry.py` for safety/eval suites.
- `research/interpretability/guardrail_analysis/service.py` for guardrail-analysis research surfaces.
- `nexusnet/hive/` for internal concept-plane vocabulary, without claiming neuron-level access.

Tier 2: Open-model SAE experiment, research-only:

- Only use local/open models where activations can be captured lawfully and reproducibly.
- Store activation capture metadata, SAE config, reconstruction metrics, candidate features, and reviewer notes as research artifacts.
- Never infer closed-model internals from output-only traces.

## Spec Requirements

- Concept telemetry proxy: label observed runs with candidate concepts, source prompts, outputs, teacher disagreements, safety flags, and confidence.
- Manifold caution label: any concept cluster from output traces must be marked `behavioral_proxy`, not `activation_feature`.
- SAE experiment record: model, layer, tokens, activation capture method, SAE architecture, sparsity, reconstruction loss, feature examples, interventions if any.
- Safety use cases: deception-risk prompts, uncertainty concepts, source-confidence behavior, policy-evasion attempts, and recurrent hallucination patterns.
- Control Panel surface: proxy concept map, confidence, linked traces, and whether any real activation experiment exists.

## Refusals

- Do not claim interpretability of closed models from screenshots or transcripts.
- Do not treat output clusters as internal activations.
- Do not use interpretability experiments to weaken safety constraints or remove refusals.
- Do not promote SAE findings without reproducible activation capture and eval review.

## Acceptance Criteria

- NexusNet can record concept telemetry proxies without private-content leakage.
- Control Panel clearly distinguishes behavioral proxy labels from real activation-derived features.
- An open-model SAE experiment can be registered as research-only with artifact trust/provenance.
- Safety review can query recurring concept clusters tied to hallucination, uncertainty, or policy-risk events.

