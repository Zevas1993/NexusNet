# Hippocampal Replay Consolidation Engine Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet memory, offline review, and self-improvement gates.

## Source Evidence

- Nature Reviews systems consolidation review: https://www.nature.com/articles/s41583-018-0031-2
- Nature Reviews hippocampal sharp-wave ripple review: https://www.nature.com/articles/s41583-018-0077-1
- Nature Communications brain-inspired replay for continual learning: https://www.nature.com/articles/s41467-020-17866-2
- Nature Neuroscience prioritized replay paper: https://www.nature.com/articles/s41593-018-0232-z
- Source status: peer-reviewed review and research paper pages.

## Finding

Biological memory is not just infinite context. The hippocampus, cortex, engrams, replay, and sleep-like offline processing suggest a deeper pattern: fast episodic capture, prioritized replay, consolidation into slower semantic structures, and forgetting/strengthening based on utility.

## NexusNet Assimilation Target

Create an offline consolidation engine for NexusNet. During "wake" mode NexusNet captures traces and candidate memories. During "sleep" mode it replays important events, extracts durable abstractions, weakens noise, strengthens useful patterns, and generates reviewable improvement proposals.

## Proposed NexusNet Components

- `EpisodicTraceStore`: fast capture of run events, sources, decisions, tool outputs, and operator feedback.
- `ReplayPriorityScore`: surprise, reward, error, contradiction, reuse value, risk, and operator mark.
- `ConsolidationSession`: offline replay batch with generated memory candidates and eval checks.
- `SemanticEngram`: durable memory abstraction with source links, confidence, and decay schedule.
- `DreamReviewQueue`: proposed route, prompt, policy, or memory updates that require review before promotion.

## Promotion Gates

- Keep raw episodic traces linked to consolidated abstractions.
- Never mutate production behavior during sleep without review.
- Test consolidation against stale, private, contradictory, and low-value traces.
- Preserve forgetting and decay paths.
- Record replay decisions and skipped candidates.

## Risks

- Offline consolidation can hallucinate patterns if not grounded in raw evidence.
- Excessive replay can overfit to recent failures.
- Private traces require retention, redaction, and deletion policy.
