# Verifier Guided Search Controller Spec

Status: P2 online assimilation target. Research-only until used only in shadow evals and high-value planning tasks.

## Source Evidence

- Reflexion paper: https://arxiv.org/abs/2303.11366
- Tree of Thoughts paper: https://arxiv.org/abs/2305.10601
- Tree of Thoughts repository: https://github.com/princeton-nlp/tree-of-thought-llm
- LATS paper: https://arxiv.org/abs/2310.04406
- LATS repository: https://github.com/lapisrocks/LanguageAgentTreeSearch
- Source status: primary paper pages and public repositories.

## Finding

Verifier-guided search replaces one-shot plan execution with exploration, self-evaluation, reflection, and backtracking. The value for NexusNet is not using more tokens everywhere; it is reserving search for hard planning, code repair, workflow design, and research synthesis where early choices determine success.

## NexusNet Assimilation Target

Create a bounded search controller that explores alternative plans in shadow mode, scores them with verifiers, and promotes only one plan to execution after policy checks.

## Proposed NexusNet Components

- `PlanSearchNode`: partial plan, evidence, estimated cost, risk, verifier score, and parent node.
- `VerifierPortfolio`: deterministic tests, policy checks, model judge, retrieval evidence, and human review.
- `SearchBudgetPolicy`: max branches, depth, tokens, wall-clock time, and authority limit.
- `ReflectionMemoryCandidate`: failure lesson that remains refs-only until curated.
- `ExecutionCommitGate`: only approved final plans may mutate state.

## Promotion Gates

- Use search before side effects, not after irreversible mutation.
- Require deterministic verifiers where available.
- Cap search cost and avoid infinite reflection loops.
- Keep rejected plans and verifier failures as evidence.

## Risks

- Search can multiply cost quickly.
- Model-based self-evaluation can reinforce wrong assumptions.
- Planning improvement does not guarantee safe execution without policy gates.
