# Property Based Agent Testing Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet's test stack and language mix.

## Source Evidence

- Hypothesis stateful testing docs: https://hypothesis.readthedocs.io/en/latest/stateful.html
- fast-check docs: https://fast-check.dev/docs/introduction/what-is-property-based-testing/
- fast-check homepage: https://fast-check.dev/
- Agentic property-based testing paper: https://arxiv.org/abs/2510.09907
- Source status: official docs and primary paper page.

## Finding

Property-based testing tests invariants across generated cases and shrinks failures to small counterexamples. For agent systems, the key is stateful properties: no duplicate mutation, approvals precede side effects, redaction precedes export, revocation blocks access, and policy decisions remain stable under irrelevant prompt changes.

## NexusNet Assimilation Target

Add property-based and state-machine testing for NexusNet agent authority boundaries, memory policies, prompt assembly, route selection, and structured-output parsing.

## Proposed NexusNet Components

- `AgentInvariant`: executable property over agent state, action traces, policies, and artifacts.
- `TraceGenerator`: creates synthetic sequences of tool calls, approvals, revocations, retries, resumes, and failures.
- `CounterexampleArtifact`: minimized failing sequence plus reproducible test case.
- `PolicyFuzzSuite`: mutates user prompts, tool manifests, connector metadata, and memory records.
- `InvariantCoveragePanel`: shows which high-risk invariants have generated-test coverage.

## Promotion Gates

- Turn every fixed authority bug into an invariant.
- Run generated tests with deterministic seeds in CI or local release gates.
- Keep dangerous generated actions inside synthetic sandboxes.
- Preserve minimized counterexamples as regression fixtures.

## Risks

- Bad generators miss the important state space.
- Generated tests can be flaky if external tools or clocks are not controlled.
- Property-based tests need clear invariants; vague safety goals are not enough.
