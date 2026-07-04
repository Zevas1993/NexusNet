# SWE Lancer Commercial Coding Spec

Status: P2 online assimilation target. Research-only until data availability, task licenses, Docker requirements, and offline runner constraints are inspected.

## Source Evidence

- SWE-Lancer paper: https://arxiv.org/abs/2502.12115
- SWE-Lancer repository: https://github.com/openai/frontier-evals/tree/main/project/swelancer
- Frontier Evals repository: https://github.com/openai/frontier-evals
- Source status: primary paper page and public evaluation code repository.

## Finding

SWE-Lancer moves coding-agent evaluation toward real freelance work. It includes independent software engineering tasks and managerial proposal-selection tasks, with the public repository exposing an offline-adjusted subset and Docker-based task infrastructure.

## NexusNet Assimilation Target

Use SWE-Lancer as a commercial-readiness reference rather than a simple coding benchmark. NexusNet should be evaluated on whether it can scope work, choose implementation proposals, produce deliverables, pass tests, and package buyer-facing handoff evidence.

## Proposed NexusNet Components

- `CommercialTaskPassport`: buyer request, acceptance criteria, budget proxy, required deliverables, risk class, and support obligations.
- `ProposalDecisionLedger`: candidate approaches, tradeoffs, selected proposal, rejected alternatives, and review notes.
- `DeliverableAcceptanceTest`: tests, screenshots, docs, build artifacts, and install/run proof.
- `BuyerHandoffChecklist`: setup instructions, known limits, support notes, rollback path, and privacy audit.
- `CommercialReadinessScore`: separates task success, maintainability, handoff quality, and support risk.

## Promotion Gates

- Do not infer commercial fitness from code tests alone.
- Require license, provenance, privacy, and support-boundary checks for generated deliverables.
- Keep offline benchmark tasks separate from real customer work.
- Validate manager-style proposal choices with explicit reasoning and post-choice evidence.

## Risks

- Public subsets may not cover the full original commercial task distribution.
- Large Docker images and per-task setup can be expensive to run at scale.
- Freelance benchmark success does not replace legal, support, pricing, or buyer-onboarding readiness.
