# Learned Model Cascade Router Spec

Status: P2 online assimilation target. Research-only until compared with AgentFloor, existing model-route logic, and open-first constraints.

## Source Evidence

- RouteLLM paper: https://arxiv.org/abs/2406.18665
- RouteLLM repository reference: https://github.com/anyscale/llm-router
- FrugalGPT paper: https://arxiv.org/abs/2305.05176
- LLMRouter repository: https://github.com/ulab-uiuc/LLMRouter
- Not Diamond routing docs: https://docs.notdiamond.ai/docs/quickstart-routing
- Source status: primary papers, public routing repositories, and official docs.

## Finding

Learned routing and cascades can cut cost while preserving quality when the router is trained or calibrated on the target task distribution. For NexusNet, the hidden value is using local/open models as the default tier and escalating only when task evidence justifies it.

## NexusNet Assimilation Target

Build a learned model cascade router after the deterministic open-first routing baseline exists. The router should learn from NexusNet eval outcomes, not generic leaderboards alone.

## Proposed NexusNet Components

- `RouteCandidateSet`: local model, open hosted model, frontier fallback, tool-specialist, and verifier route.
- `RouteOutcomeDataset`: prompt class, selected model, cost, latency, success, verifier result, and fallback reason.
- `CascadePolicy`: cheap-first, verifier-escalate, confidence-escalate, or direct-premium by risk class.
- `RouterCalibrationReport`: expected quality/cost curve and failure bands.
- `OpenFirstGuard`: blocks premium escalation unless policy and evidence allow it.

## Promotion Gates

- Train or calibrate on NexusNet-specific tasks.
- Do not route private data to hosted models without explicit permission.
- Track route failures and rollback when calibration drifts.
- Compare learned routing against simple deterministic baselines.

## Risks

- Router scores can become stale as models and prices change.
- Small routers can misclassify rare high-risk tasks.
- Cost optimization can undermine quality if success metrics are too shallow.
