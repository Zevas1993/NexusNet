# Neural Cellular Self Organizing Growth Spec

Status: P1 final-pass assimilation target. Research-only and computational only.

## Source Evidence

- Growing Neural Cellular Automata article: https://distill.pub/2020/growing-ca/
- Google Research publication page: https://research.google/pubs/growing-neural-cellular-automata/
- Adversarial Reprogramming of Neural Cellular Automata: https://distill.pub/selforg/2021/adversarial/
- HyperNCA paper page: https://arxiv.org/abs/2204.11674
- Source status: primary Distill/Google pages and paper page.

## Finding

Neural cellular automata demonstrate a concrete computational version of growth, persistence, and regeneration from local update rules. This is a direct bridge from embryo metaphor to buildable software: a system can grow a target form from a seed if local cells carry state, communicate locally, and are trained for persistence and repair.

## NexusNet Assimilation Target

Create a software morphogenesis lane for NexusNet. Instead of only hand-assembling architecture, define small local update rules that grow, maintain, repair, and prune parts of NexusNet's memory maps, eval surfaces, route graphs, and capability atlas.

## Proposed NexusNet Components

- `GrowthCell`: local unit with hidden state, type, maturity, evidence links, and neighbor signals.
- `LocalUpdateRule`: rule that changes a cell based on neighbors, gradients, and target morphology.
- `RegenerationTrainingScenario`: simulated damage or missing structure that the system must repair.
- `MorphogeneticTrace`: records how structure grew from seed to target.
- `UncontrolledGrowthBrake`: stops expansion when constraints, evidence, or resource budgets are violated.

## Promotion Gates

- Use synthetic or derived metadata worlds first, not production code mutation.
- Require target morphology and damage tests before growth runs.
- Keep every grown structure reversible or rebuildable from evidence.
- Compare grown structures against hand-built baselines.
- Maintain strict stop conditions and operator review.

## Risks

- Growth rules can create complexity faster than humans can inspect it.
- Regeneration may preserve bad patterns if the target morphology is wrong.
- The embryo metaphor can encourage overclaiming unless tied to tests.
