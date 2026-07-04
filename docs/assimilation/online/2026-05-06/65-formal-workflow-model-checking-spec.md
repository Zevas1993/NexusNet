# Formal Workflow Model Checking Spec

Status: P2 online assimilation target. Research-only until a small NexusNet authority workflow is selected for pilot modeling.

## Source Evidence

- Apalache docs: https://apalache-mc.org/docs/apalache/index.html
- Apalache project page: https://apalache-mc.org/
- Alloy Analyzer FAQ: https://alloytools.org/faq/what_kind_of_analysis_does_the_alloy_analyzer_do.html
- Learn TLA+ PlusCal guide: https://learntla.com/core/pluscal.html
- TLA+ verification overview paper: https://arxiv.org/abs/2211.07216
- Source status: official docs and primary paper pages.

## Finding

Formal methods can catch authority and workflow bugs before code exists. TLA+, PlusCal, Apalache, and Alloy are especially relevant for state machines, delegation, retries, cancellation, approval gates, revocation, and side-effect ordering.

## NexusNet Assimilation Target

Model-check the smallest high-authority NexusNet workflows before implementation: delegated tool grants, approval before mutation, no duplicate side effects on resume, revocation, and rollback after failure.

## Proposed NexusNet Components

- `WorkflowInvariantSpec`: states, actions, allowed transitions, forbidden states, and liveness expectations.
- `ModelCheckTrace`: counterexample, violated invariant, minimal action sequence, and mapped implementation test.
- `AuthorityStateModel`: grant, approve, execute, revoke, retry, compensate, and audit states.
- `SpecToTestBridge`: turns counterexamples into property-based or integration test cases.
- `FormalModelRegistry`: stores model versions next to implementation and policy versions.

## Promotion Gates

- Start with one narrow authority workflow, not the entire brain.
- Every formal invariant needs a matching runtime test or trace assertion.
- Counterexamples must be reviewed before implementation proceeds.
- Keep models readable enough for maintainers to audit.

## Risks

- Formal models can prove the wrong abstraction if requirements are incomplete.
- State-space growth can make models hard to check.
- Modeling cost is only justified for high-risk workflow primitives.
