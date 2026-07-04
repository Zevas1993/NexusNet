# Prompt Governance Optimization Spec

Status: P2 online assimilation target. Research-only until existing NexusNet prompts, skills, and model routes are inventoried.

## Source Evidence

- Langfuse prompt management docs: https://langfuse.com/docs/prompt-management/get-started
- DSPy repository: https://github.com/stanfordnlp/dspy
- Promptfoo docs: https://www.promptfoo.dev/docs/intro/
- ChainForge repository: https://github.com/ianarawjo/ChainForge
- Source status: official docs and public repositories.

## Finding

Prompt management and optimization tooling shows three useful patterns: prompts need versioned release labels, prompt changes need evals before promotion, and optimization should produce reviewable candidate prompts rather than silently changing production behavior.

## NexusNet Assimilation Target

Create governed prompt versioning for NexusNet skills, routers, memory policies, tool prompts, safety prompts, and eval prompts. Prompt experiments should be traceable and reversible.

## Proposed NexusNet Components

- `PromptPassport`: name, owner, lane, version, model route, variables, data class, and release label.
- `PromptExperimentRun`: candidate prompt, baseline prompt, eval cases, metrics, trace links, and reviewer decision.
- `PromptPromotionGate`: requires passing evals, policy review, and rollback path before production label changes.
- `PromptDiffViewer`: highlights instruction, variable, tool-schema, and safety-boundary changes.
- `PromptRollbackRecord`: previous production version, reason for rollback, and affected runs.

## Promotion Gates

- No silent prompt updates for production lanes.
- Tie every prompt version to eval results and trace examples.
- Keep optimization shadow-only until reviewed.
- Treat safety, policy, and authority prompts as high-risk release artifacts.

## Risks

- Automated prompt optimization can overfit to eval cases.
- Prompt registries can become stale unless runtime fetch and local packaging are coordinated.
- Hosted prompt-management systems may conflict with local-only product requirements.
