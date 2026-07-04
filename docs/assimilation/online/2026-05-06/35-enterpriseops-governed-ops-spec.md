# EnterpriseOps Governed Operations Spec

Status: P1 online assimilation target. Research-only until benchmark assets, licenses, and container requirements are inspected locally.

## Source Evidence

- EnterpriseOps-Gym project page: https://enterpriseops-gym.github.io/
- EnterpriseOps-Gym paper: https://arxiv.org/abs/2603.13594
- Source status: official project page with paper, GitHub, dataset, and benchmark details.

## Finding

EnterpriseOps-Gym evaluates agents on stateful enterprise operations with hundreds of tools, many database tables, persistent state changes, policy rules, cross-domain workflows, and infeasible-task refusal. It is valuable because it treats enterprise agency as governed operations, not just generic tool use.

## NexusNet Assimilation Target

Build an EnterpriseOps shadow lane for NexusNet Control Panel. Any business-workflow agent should prove that it can navigate high-density tools, follow internal policy, refuse infeasible or unauthorized tasks, and produce SQL-like state-verification evidence before mutating real systems.

## Proposed NexusNet Components

- `EnterpriseTaskPassport`: domain, policy rules, data scopes, allowed tools, verifier, and infeasible-task flag.
- `BusinessPolicyGate`: evaluates approval workflow, privacy, access level, and separation-of-duty requirements before tool calls.
- `EnterpriseStateVerifier`: checks task completion by state, not self-report.
- `CrossDomainTrace`: links calendar, email, drive, HR, ITSM, chat, and CRM-like action chains.
- `InfeasibleTaskClassifier`: captures why the correct action is refusal or escalation.

## Promotion Gates

- Require hidden deterministic verifiers for state-changing workflows.
- Treat failure to refuse infeasible tasks as a release blocker.
- Require policy evidence before business-data mutation.
- Keep enterprise simulations sandboxed and seeded with synthetic data only.

## Risks

- Enterprise-style task suites can become heavy to install and maintain.
- Agents may optimize for verifier quirks instead of business correctness.
- Domain policies must be modeled precisely or the benchmark will teach the wrong behavior.
