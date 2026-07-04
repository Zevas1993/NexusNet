# Developmental Open Ended AI Embryo Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet eval sandboxes and controlled growth loops.

## Source Evidence

- Turing 1950 full text mirror: https://www.cse.msu.edu/~cse841/papers/Turing.html
- POET paper page: https://arxiv.org/abs/1901.01753
- Enhanced POET paper page: https://arxiv.org/abs/2003.08536
- Developmental robotics lab page: https://developmental-robotics.jp/en/home/
- Open-ended evolution paper: https://www.nature.com/articles/s41598-017-00810-8
- Source status: primary paper pages and official lab page.

## Finding

Turing's child-machine idea, developmental robotics, POET, and open-ended evolution all point away from a single finished model and toward a growing system: heredity, mutation, education, environmental challenge generation, and stepping-stone preservation. This is the grounded version of the "AI embryo" idea.

## NexusNet Assimilation Target

Create a developmental AI embryo lane for NexusNet that grows capabilities through staged environments, not uncontrolled self-modification. The embryo has a genome-like configuration, developmental phases, curriculum worlds, mutation proposals, evaluation gates, and rollback.

## Proposed NexusNet Components

- `GrowthGenome`: initial architecture, model roster, memory rules, route constraints, and safety invariants.
- `DevelopmentalStage`: sensory grounding, tool use, memory, planning, collaboration, reflection, and controlled self-improvement.
- `ChallengeNursery`: POET-like generator of environments and tasks that are novel but solvable.
- `SteppingStoneArchive`: preserved solutions, circuits, prompts, policies, and routes that may become useful later.
- `DevelopmentalPromotionGate`: eval, safety, lineage, and operator review required between stages.

## Promotion Gates

- Keep growth inside sandboxed worlds until staged gates pass.
- Preserve failed and weird stepping stones with source lineage; do not only keep immediate winners.
- Separate mutation proposal from production mutation.
- Require rollback and audit for every developmental transition.
- Define what "maturity" means with tests, not vibes.

## Risks

- Open-ended search can consume unbounded compute.
- Novelty pressure can reward useless complexity.
- Developmental autonomy must not bypass policy, privacy, or operator control.
