# ClawArena Belief Revision Spec

Status: P1 online assimilation target. Research-only until benchmark code and data are inspected.

## Source Evidence

- ClawArena paper: https://arxiv.org/abs/2604.04202
- Source status: primary paper page with linked code.

## Finding

ClawArena evaluates persistent agents in evolving information environments with noisy, partial, and contradictory traces. It focuses on multi-source conflict reasoning, dynamic belief revision, and implicit personalization.

## NexusNet Assimilation Target

Use ClawArena as a pattern for memory and KAC contradiction handling. NexusNet should preserve conflicting evidence, revise beliefs when new evidence invalidates old conclusions, and distinguish current-fact updates from preference corrections.

## Proposed NexusNet Components

- `BeliefRevisionCase`: source records, staged updates, hidden ground truth, and expected current belief.
- `ContradictionLedger`: stores unresolved conflicts without collapsing them into one synthetic answer.
- `PreferenceCorrectionRecord`: marks user corrections as preference evidence only when appropriate.
- `CurrentFactResolver`: selects current truth from dated evidence with source-status metadata.

## Promotion Gates

- Do not mutate old source artifacts; add new revision records.
- Require provenance for every changed belief.
- Keep implicit personalization opt-in and inspectable.

## Risks

- Belief revision can be mistaken for memory rewriting.
- Personalization evidence can become privacy-sensitive.
- Hidden ground-truth benchmarks may not transfer directly to open-world facts.
