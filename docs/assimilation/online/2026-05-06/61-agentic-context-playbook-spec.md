# Agentic Context Playbook Spec

Status: P2 online assimilation target. Research-only and refs-only until memory governance and prompt promotion gates are mapped.

## Source Evidence

- ACE project page: https://ace-agent.github.io/
- ACE paper: https://arxiv.org/abs/2510.04618
- ACE repository: https://github.com/ace-agent/ace
- ACE ICLR 2026 note: https://ace-agent.github.io/blogs/2026-01-30-iclr-acceptance/
- Source status: official project page, primary paper page, and public repository.

## Finding

Agentic Context Engineering treats context as an evolving playbook rather than a static prompt or lossy summary. Generator, reflector, and curator roles accumulate strategies from execution feedback, preserving structured lessons that can improve future runs without model fine-tuning.

## NexusNet Assimilation Target

Add a governed playbook layer between raw memory and production prompts. NexusNet should extract reusable strategies from traces, curate them, test them, and attach them to tasks only when relevant.

## Proposed NexusNet Components

- `PlaybookEntry`: task class, strategy, evidence traces, applicability conditions, counterexamples, and expiration.
- `PlaybookCurator`: deduplicates, merges, retires, and ranks entries by eval evidence.
- `ContextAssemblyPolicy`: decides which playbook entries enter a run and why.
- `PlaybookRegressionSet`: tests whether entries improve task success without increasing unsafe actions.
- `PlaybookLineageView`: links entries to raw episodes, failures, evals, and reviewer decisions.

## Promotion Gates

- Keep raw episodes immutable and separate from curated playbooks.
- Require counterexamples and applicability limits for every promoted entry.
- Do not let playbooks override policy, user instructions, or source-status boundaries.
- Test for context bloat and stale strategy drift.

## Risks

- Playbooks can accumulate bad heuristics if curation is weak.
- Long contexts can degrade behavior or increase cost.
- Self-improving context can become unreviewable without lineage and retirement policy.
