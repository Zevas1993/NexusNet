# Computer-Use Safety Reliability Spec

Status: P0 online assimilation target. Research-only until converted into VisualOps/computer-use eval fixtures.

## Source Evidence

- OS-BLIND paper: https://arxiv.org/abs/2604.10577
- AgentHazard paper: https://arxiv.org/abs/2604.02947
- On the Reliability of Computer Use Agents: https://arxiv.org/abs/2604.17849
- Source status: primary paper pages.

## Finding

Recent computer-use research points to three separate hazards: benign user requests can still produce harmful outcomes in the environment, harmful behavior can emerge from sequences of individually plausible steps, and a computer-use agent that succeeds once may fail on repeated execution of the same task.

## NexusNet Assimilation Target

Make computer-use certification a repeated-run, harm-aware, context-aware gate. NexusNet should not treat a single successful browser/desktop task as proof of reliability, and it should re-check safety after decomposition, handoff, and environmental changes.

## Proposed NexusNet Components

- `ComputerUseHazardSuite`: local fixture categories for environment-embedded threat, accumulated harm, prompt injection, and irreversible action.
- `RepeatedRunReliability`: runs the same computer-use task multiple times and records variance.
- `BenignIntentOutcomeGate`: evaluates likely outcome harm even when the user request is benign.
- `VisualOps Stop/Undo Contract`: every high-risk operator lane must expose stop, rollback, and action replay.

## Promotion Gates

- No live desktop/browser authority above read-only without explicit consent and visible trace.
- Require repeated-run success before advertising reliability.
- Require subtask safety re-checks after decomposition and before each irreversible step.
- Keep harmful benchmark payloads isolated as test fixtures, not operator suggestions.

## Risks

- Safety benchmarks can contain sensitive misuse patterns; keep docs high-level and fixtures controlled.
- Repeated-run testing adds cost and time.
- Multi-agent decomposition can hide harmful intent from sub-agents if capability scope is not carried forward.
