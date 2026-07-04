# Tau Bench Customer Reliability Spec

Status: P1 online assimilation target. Research-only until tau3 task updates and licenses are inspected.

## Source Evidence

- Tau-bench paper: https://arxiv.org/abs/2406.12045
- Tau-bench repository: https://github.com/sierra-research/tau-bench
- Tau2/tau3 repository: https://github.com/sierra-research/tau2-bench
- Source status: primary paper page plus public benchmark repositories. The older repo warns that tau3 contains newer fixes and domains.

## Finding

Tau-bench evaluates dynamic conversations between simulated users and tool-using agents under domain-specific API tools and policy guidelines. It scores final database state and uses repeated-trial reliability metrics. The newer tau3 repository adds fixed tasks, banking knowledge, and voice modalities.

## NexusNet Assimilation Target

Add policy-compliant customer/task reliability fixtures for NexusNet. The main idea is not customer support specifically; it is multi-turn state-changing work where the agent must follow policy, ask clarifying questions, use tools, and produce the correct final state across repeated trials.

## Proposed NexusNet Components

- `PolicyTaskDomain`: policy docs, tools, user simulator, database fixture, and target final state.
- `PassKReliability`: repeated-trial success metric for nondeterministic tool agents.
- `FinalStateVerifier`: compares database/workspace state to expected state rather than trusting final text.
- `ClarificationGate`: rewards asking for missing information and blocks guessing on policy-sensitive tasks.

## Promotion Gates

- Prefer tau3 task definitions if local evaluation is attempted.
- Keep simulated user data synthetic.
- Require final-state verification for any state-mutating workflow.
- Track reliability decay across repeated runs, not only pass@1.

## Risks

- Older tau-bench tasks are explicitly marked outdated by the repository.
- User simulators can leak task intent if not audited.
- Domain policies can be overfit unless task splits and gold states remain frozen.
