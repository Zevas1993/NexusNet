# Causal Representation Intervention Cortex Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet eval sandboxes, memory promotion, and route learning.

## Source Evidence

- Toward causal representation learning record: https://research-explorer.ista.ac.at/record/14117
- Toward causal representation learning arXiv page: https://arxiv.org/abs/2102.11107
- CausalWorld repository: https://github.com/rr-learning/CausalWorld
- CausalWorld arXiv page: https://arxiv.org/abs/2010.04296
- Source status: primary paper records and official benchmark repository.

## Finding

Modern models often learn associations; causal representation learning asks the harder question: what high-level variables and mechanisms generate observations, and how do they behave under interventions? This is the difference between a system that memorizes patterns and one that can adapt when the world changes.

## NexusNet Assimilation Target

Add a causal intervention cortex to NexusNet. It should identify candidate causal variables in run traces, design safe interventions, test them in sandboxed worlds, and use those results to update routing, memory confidence, and policy assumptions.

## Proposed NexusNet Components

- `CausalVariableCandidate`: proposed high-level factor with source evidence and measurement method.
- `InterventionPlan`: safe test that changes one factor while holding others stable.
- `MechanismGraph`: causal relation among tools, models, prompts, policies, memory, and outcomes.
- `CounterfactualTrace`: predicted and observed difference under an intervention.
- `CausalConfidenceLedger`: tracks which mechanisms are confirmed, refuted, or unknown.

## Promotion Gates

- Prefer sandboxed or replayed interventions before live interventions.
- Require explicit consent for any intervention touching user data or production work.
- Separate association evidence from causal evidence.
- Record failed causal hypotheses; they are useful negative evidence.
- Do not promote causal claims without repeatable tests or strong external evidence.

## Risks

- Causal discovery from messy agent traces is hard and can overfit.
- Bad interventions can harm real work if not sandboxed.
- Counterfactual language can sound stronger than the evidence supports.
