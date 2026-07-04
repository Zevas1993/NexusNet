# NexusNet Self-Improvement Layer

## Purpose

The Self-Improvement Layer turns NexusNet interactions into governed improvement candidates. It follows the operating pattern confirmed from the multimodal self-improvement survey: data collection, data organization, and model or workflow optimization. NexusNet does not learn from every interaction automatically. It captures structured events, triages them, and queues safe candidates behind review and regression gates.

Primary sources:

- arXiv:2510.02665, "Self-Improvement in Multimodal Large Language Models: A Survey"
- arXiv:2411.17760, "Efficient Self-Improvement in Multimodal Large Language Models: A Model-Level Judge-Free Approach"

## Architecture

```text
Experience Capture
  -> ImprovementEvent
  -> TriageDecision
  -> ImprovementQueue
  -> validation / approval / deployment / monitoring / rollback
```

The implementation is intentionally governed and additive:

- `nexusnet/core/self_improvement/event_schema.py`
- `nexusnet/core/self_improvement/experience_capture.py`
- `nexusnet/core/self_improvement/triage.py`
- `nexusnet/core/self_improvement/provenance.py`
- `nexusnet/core/self_improvement/evaluator.py`
- `nexusnet/core/self_improvement/improvement_queue.py`
- `nexusnet/core/self_improvement/memory_update_policy.py`
- `nexusnet/core/self_improvement/prompt_update_policy.py`
- `nexusnet/core/self_improvement/training_candidate_builder.py`
- `nexusnet/core/self_improvement/regression_gate.py`

No direct model fine-tuning or autonomous weight update is included.

## ImprovementEvent Schema

An `ImprovementEvent` stores:

- session id, user goal, modality set, task type, context sources
- agent plan, actions taken, final output summary
- outcome status, user feedback, failure modes
- learning signal for memory, eval, or training-candidate creation
- privacy and retention classification
- evidence references and source document references

Every event defaults to the NexusNet project name and carries source references for the self-improvement survey, judge-free multimodal self-improvement paper, and this design document.

## Event Lifecycle

```text
captured -> triaged -> proposed -> validated -> approved -> deployed -> monitored
                                                   \-> reverted
                         \-> rejected
```

Rejected records remain auditable. This keeps unsafe events visible without letting them become memory, eval data, or training data.

## Memory Update Policy

Store as project memory only when:

- no secrets are present
- private data is not marked for durable retention without review
- the learning signal explicitly allows memory storage
- source evidence or operator confirmation exists

Never store:

- secrets
- passwords
- raw private content without an explicit need and review
- speculative conclusions as confirmed facts

## Evaluation Generation Policy

Create eval cases from:

- failures
- partial or blocked outcomes
- stale-information risk
- missing-context events
- tool errors
- hallucination risk
- user corrections

Eval cases are preferred over direct model updates because they improve measurement before behavior is changed.

## Training Candidate Policy

Training examples remain candidates only. They require:

- human review
- source evidence
- privacy classification
- external or tool-based verification where possible
- regression gates before use

The MVP records training candidates but does not fine-tune a model.

## Safety And Privacy Rules

Secrets cause immediate discard/rejection from the improvement path. Private data requires review and redaction before durable use. Low-confidence or failure-bearing events require review. High-impact updates must pass validation before approval.

## Regression Gates

Before an approved improvement can affect behavior, it should be tested against:

- project continuity
- factuality
- tool-use correctness
- safety and privacy leakage
- coding or artifact validation when applicable
- multimodal grounding when applicable
- latency and cost thresholds when applicable

## Operator Endpoints

- `POST /ops/brain/self-improvement/capture` accepts a raw interaction trace, normalizes it into an `ImprovementEvent`, triages it, queues it, and returns a governed review bundle.
- `POST /ops/brain/self-improvement/events` accepts a pre-normalized structured event, triages it, and queues only safe candidates.
- `GET /ops/brain/self-improvement/queue` lists proposed, validated, approved, deployed, monitored, reverted, and rejected candidates.
- `GET /ops/brain/self-improvement/queue/{queue_id}/review` returns provenance, evaluator findings, memory/prompt/training candidates, and regression gate blockers.
- `GET /ops/brain/canon/self-improvement` exposes the canon scorecard consumed by the Control Panel.

## Open Questions

- Which durable storage backend should replace the MVP JSON queue?
- Which verifier tools should be trusted for multimodal grounding?
- Which Control Panel surfaces should expose the improvement queue first?
- Which event classes should automatically generate held-out eval tasks?
- When, if ever, should adapter fine-tuning be enabled after review?
