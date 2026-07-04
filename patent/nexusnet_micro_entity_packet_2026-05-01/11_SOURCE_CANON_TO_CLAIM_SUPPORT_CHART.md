# Source Canon To Claim Support Chart

Use this chart to check whether each proposed claim element is supported by
the NexusNet source record before filing. This is not a patentability
opinion. It is a written-description and drafting-support aid.

## Source Records

- S1: `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- S2: `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`
- S3: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- S4: `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- S5: `nexusnet/core/brain.py`
- S6: `nexusnet/canon/realization.py`

## Claim Element Support

| Claim element | Draft claim refs | Primary support | Notes to verify |
| --- | --- | --- | --- |
| Brain-mediated neural core service | 1, 14, 15, 23 | S1, S2, S5, S6 | Confirm every user-facing path is intended to route through NexusBrain or equivalent. |
| Hive node registry | 1, 2, 23 | S2, S3, S4, S6 | Confirm final registry fields and expert/AO node taxonomy. |
| Neural bus carrying typed activations | 1, 3, 15, 23 | S2, S4 | Confirm v0 data contract names. |
| Sparse cortex router / MoE-style selection | 1, 6, 15, 23 | S1, S2, S4, S6 | Confirm selected scoring dimensions. |
| Multi-plane memory / engram layer | 1, 5, 15, 23 | S1, S2, S4 | Confirm memory plane taxonomy and provenance/status labels. |
| Recurrent deliberation loop and exit gates | 1, 4, 15, 23 | S3, S4 | Confirm loop metadata and exit gate fields. |
| Immune/governance kernel | 1, 10, 13, 15, 23 | S2, S3, S4 | Confirm no-bypass policy and write gates. |
| Checkpoint/rewind ledger | 1, 11, 15, 23 | S3, S4 | Confirm pre-write snapshot and rollback metadata. |
| Skill-system orchestrator | 8, 19 | S3, S4 | Confirm focused skills plus orchestrator, not mega-skill pattern. |
| Sandbox agent factory | 9 | S3, S4 | Confirm planner/implementer/reviewer/merger lane evidence. |
| Candidate assimilation and sidebar | 10, 16, 24 | S2, S3, S4 | Confirm sandbox/eval/promotion/rejection ledger states. |
| Federated learning plane | 12, 20, 25 | S1, S2, S3, S4 | Confirm privacy boundary and redacted delta types. |
| VisualOps cockpit | 7, 18 | S1, S2, S4 | Confirm live surfaces and missing telemetry behavior. |
| Native MoE evolution path | 25 | S1, S2, S3, S4 | Confirm this is future growth path, not current implementation claim. |

## Filing Review Notes

- Remove or narrow any claim element that cannot be enabled in the
  specification.
- Avoid claiming only a result, such as "self-improves," without concrete
  data structures, routing steps, gates, and ledgers.
- Separate implemented features from planned embodiments when discussing
  commercial readiness.
