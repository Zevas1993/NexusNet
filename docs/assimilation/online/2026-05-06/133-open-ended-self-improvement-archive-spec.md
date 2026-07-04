# Open Ended Self Improvement Archive Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet shadow-only improvement workflows.

## Source Evidence

- Darwin Godel Machine arXiv page: https://arxiv.org/abs/2505.22954
- Darwin Godel Machine paper page: https://huggingface.co/papers/2505.22954
- Google DeepMind AlphaEvolve announcement: https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Godel Machines arXiv page: https://arxiv.org/abs/cs/0309048
- Source status: primary paper pages and official research announcement.

## Finding

The practical self-improvement signal is not an agent silently rewriting itself. It is an archive of variants, empirical evaluation, lineage, open-ended exploration, and promotion gates. The archive matters because breakthroughs can come from branches that were not immediate hill-climb winners.

## NexusNet Assimilation Target

Create a shadow-only self-improvement archive for NexusNet. Candidate changes to prompts, policies, circuits, tools, routers, evals, or code are generated, evaluated, stored with ancestry, and reviewed before promotion.

## Proposed NexusNet Components

- `ImprovementGenome`: candidate change payload, parent lineage, intent, and affected lanes.
- `VariantArchive`: tree of candidate agents, circuits, prompts, policies, and routes.
- `EmpiricalFitnessSuite`: tests performance, safety, cost, privacy, robustness, and regression risk.
- `SteppingStoneSelector`: samples not only best variants but diverse promising ancestors.
- `PromotionTribunal`: human/eval/policy gate that decides whether a variant graduates.

## Promotion Gates

- Keep generated variants out of production until review and tests pass.
- Preserve failed variants and weird stepping stones with evidence.
- Require regression tests and rollback plan for every promoted variant.
- Separate self-improvement search from self-modifying authority.
- Track compute budget and stop conditions.

## Risks

- Open-ended archives can consume unbounded compute and storage.
- Fitness suites can be gamed if too narrow.
- Self-improvement language can obscure the fact that promotion must remain governed.
