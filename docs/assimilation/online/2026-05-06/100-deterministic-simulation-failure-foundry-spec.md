# Deterministic Simulation Failure Foundry Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet sandbox, orchestration, and multi-agent testing.

## Source Evidence

- FoundationDB simulation and testing docs: https://apple.github.io/foundationdb/testing.html
- FoundationDB testing source page: https://github.com/apple/foundationdb/blob/main/documentation/sphinx/source/testing.rst
- Jepsen analyses index: https://jepsen.io/analyses
- LLVM libFuzzer docs: https://llvm.org/docs/LibFuzzer.html
- AFL++ repository: https://github.com/AFLplusplus/AFLplusplus
- Source status: official docs/repositories and public analysis index.

## Finding

FoundationDB's deterministic simulation is one of the best hidden testing ideas in production software: model a whole distributed system, inject brutal failures, and make failures exactly reproducible. Jepsen and coverage-guided fuzzers add complementary adversarial testing discipline. NexusNet needs this style for agent orchestration, not just unit tests.

## NexusNet Assimilation Target

Build a deterministic failure foundry for NexusNet runs. Simulated models, tools, filesystems, networks, memory stores, and policy gates should be driven by seeded schedules so rare failures can be replayed and minimized.

## Proposed NexusNet Components

- `SimulationSeed`: controls timing, model responses, tool failures, network delays, and scheduler interleavings.
- `SimulatedToolWorld`: deterministic fake filesystem, browser, connector, model, and memory APIs.
- `FailureScenarioGenerator`: produces partitions, timeouts, stale reads, malformed outputs, denial spikes, and partial writes.
- `ReplayableFailureTrace`: seed, event log, state digests, and minimized reproduction.
- `AgentInvariantChecker`: asserts no unauthorized effects, no lost approvals, no hidden state corruption, and no unsafe retries.

## Promotion Gates

- Every simulation failure must replay from seed.
- Keep real credentials and private files out of the simulated world.
- Add invariants before adding random failure volume.
- Promote minimized failures into permanent regression cases.
- Use coverage/fuzzing metrics as search guidance, not as proof of safety.

## Risks

- Simulation models can miss real-world behavior.
- Determinism requires control over time, randomness, concurrency, and external APIs.
- Large simulations can become slow without tiered test budgets.
