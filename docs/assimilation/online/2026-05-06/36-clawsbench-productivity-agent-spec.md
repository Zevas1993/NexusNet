# ClawsBench Productivity Agent Spec

Status: P1 online assimilation target. Research-only until task release status, license, and mock-service containers are inspected.

## Source Evidence

- ClawsBench project page: https://clawsbench.benchflow.ai/
- ClawsBench paper link: https://clawsbench.benchflow.ai/
- ClawsBench repository link: https://clawsbench.benchflow.ai/
- Source status: official project page with paper, GitHub, dataset, results, and release roadmap.

## Finding

ClawsBench evaluates productivity agents in high-fidelity mock Gmail, Calendar, Docs, Drive, and Slack services. Its strongest signal is the joint measurement of task success and unsafe-action rate across realistic multi-service workflows with deterministic state management.

## NexusNet Assimilation Target

Use ClawsBench patterns for a NexusNet productivity-safety lane. NexusNet should measure whether skills, prompts, and tool manifests improve completion without increasing unsafe actions such as unauthorized sharing, prompt-injection compliance, hallucinated actions, escalation probing, or over-refusal.

## Proposed NexusNet Components

- `ProductivityWorkspaceSandbox`: mock mail, calendar, docs, drive, and chat APIs with snapshot/restore.
- `UnsafeActionRateScorer`: counts policy violations independently from task success.
- `SkillScaffoldAblation`: tests with and without domain skill prompts and meta safety prompts.
- `MultiServiceWorkflowTrace`: records cross-service dependencies and authorization checks.
- `InjectionTrapDataset`: synthetic comments, emails, headers, and docs designed to test prompt-injection resistance.

## Promotion Gates

- Track task success and unsafe-action rate separately.
- Test single-service and multi-service workflows independently.
- Require authorization checks before share, forward, edit, delete, or external send actions.
- Keep all productivity tests on mock services until live connector controls are proven.

## Risks

- Mock APIs may not capture every edge case in real Google, Microsoft, or Slack services.
- Strong domain skills can increase both success and unsafe behavior.
- Over-refusal can look safe while still failing legitimate operator workflows.
