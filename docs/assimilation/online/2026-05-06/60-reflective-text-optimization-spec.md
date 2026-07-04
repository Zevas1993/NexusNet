# Reflective Text Optimization Spec

Status: P2 online assimilation target. Research-only and shadow-only until prompt, skill, and policy governance are in place.

## Source Evidence

- GEPA paper: https://arxiv.org/abs/2507.19457
- GEPA repository: https://github.com/CerebrasResearch/gepa
- DSPy GEPA docs: https://github.com/stanfordnlp/dspy/blob/main/docs/docs/api/optimizers/GEPA/overview.md
- TextGrad paper: https://arxiv.org/abs/2406.07496
- TextGrad repository: https://github.com/zou-group/textgrad
- Source status: primary paper pages, public repositories, and framework docs.

## Finding

GEPA and TextGrad point to a powerful path for improving compound AI systems without weight training: use task traces, textual feedback, and reflection to evolve prompts, code snippets, policies, and component instructions. The leverage is high, but unsafe if it can silently edit production behavior.

## NexusNet Assimilation Target

Create a shadow-only reflective optimization lane. NexusNet can propose improved prompts, policies, playbooks, and tool descriptions from failed traces, but promotion must require evals, diff review, provenance, and rollback.

## Proposed NexusNet Components

- `OptimizationCandidate`: target artifact, baseline, proposed change, trace evidence, metric delta, and risk class.
- `TextualGradientTrace`: feedback, diagnosis, proposed edit, accepted edit, rejected edit, and rationale.
- `ParetoCandidateSet`: competing changes optimized for quality, safety, cost, latency, and simplicity.
- `ShadowOptimizerRunner`: runs on saved eval cases without mutating production artifacts.
- `OptimizationPromotionGate`: requires eval pass, review, provenance, and rollback record.

## Promotion Gates

- Keep reflective optimization advisory until human or governance approval.
- Never let an optimizer rewrite safety, authority, or privacy rules without review.
- Require before/after eval traces and prompt diffs.
- Preserve failed optimization attempts as negative evidence.

## Risks

- Optimizers can overfit eval cases and degrade real behavior.
- Textual feedback can be biased, circular, or model-dependent.
- Self-improvement pressure can blur the boundary between suggestion and autonomous mutation.
