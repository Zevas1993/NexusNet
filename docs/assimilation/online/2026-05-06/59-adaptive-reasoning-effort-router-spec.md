# Adaptive Reasoning Effort Router Spec

Status: P1 online assimilation target. Research-only until NexusNet supports per-step reasoning effort metadata across model routes.

## Source Evidence

- Ares paper: https://arxiv.org/abs/2603.07915
- AdaptEvolve paper: https://arxiv.org/abs/2602.11931
- DICE paper: https://arxiv.org/abs/2507.23554
- Source status: recent primary paper pages.

## Finding

The hidden cost lever is not only which model to use; it is how much reasoning effort to spend at each step. Ares proposes a lightweight router that predicts the lowest sufficient reasoning effort for each agent step and reports large reasoning-token reductions with minimal task-success loss.

## NexusNet Assimilation Target

Add per-step reasoning effort routing to the NexusNet brain. Cheap deterministic steps should stay low effort; ambiguous planning, authority escalation, code repair, security review, and contradiction handling should escalate.

## Proposed NexusNet Components

- `StepDifficultySignal`: tool state, uncertainty, novelty, risk class, verifier history, and failure count.
- `ReasoningEffortPolicy`: low, medium, high, or route-specific equivalent with escalation triggers.
- `EffortRouterTrace`: predicted effort, actual effort, tokens, latency, result quality, and override reason.
- `MinimumSufficientEffortDataset`: replayed NexusNet traces labeled by lowest effort that preserved success.
- `EffortRegressionGate`: compares fixed-high, fixed-low, and adaptive policies across agent tasks.

## Promotion Gates

- Never downshift high-authority actions solely for cost.
- Train or calibrate on NexusNet traces, not generic claims.
- Record effort choice in every run trace.
- Use fallback escalation after uncertainty, verifier failure, or policy ambiguity.

## Risks

- A cheap router can under-classify difficult steps.
- Reasoning-effort APIs differ across providers and local runtimes.
- Reducing tokens can silently reduce review quality if success metrics are too shallow.
