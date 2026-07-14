# Colibrì Assimilation Notice

NexusNet's native MoE residency work was informed by the Apache-2.0 licensed Colibrì project:

- Repository: <https://github.com/JustVugg/colibri>
- Reviewed revision: `748787c3afa8ab336bb51bf616f212a04f209bba`
- License: Apache License 2.0

The NexusNet implementation owns its runtime interfaces and execution architecture. The following upstream areas are recorded as eligible for narrowly attributed algorithm adaptation:

- `c/tier.h`: frequency/recency heat scoring, decay, and hysteretic tier replacement.
- `c/resource_plan.py`: dense-versus-expert resource accounting concepts.

The following areas were used as conceptual evidence and were independently expressed against NexusNet contracts:

- `c/st.h`: bounded asynchronous storage and prefetch behavior.
- `c/glm.c`: expert load/compute overlap and router-guided prefetch.
- `docs/grammar-draft.md`: target-verified constrained drafts.
- `docs/experiments/glm52-6x5090-2026-07-12.md`: evidence that speculation can regress fully resident execution.

Excluded from the production dependency and integration graph:

- `c/openai_server.py`
- the `coli` CLI
- the Colibrì runtime, server, queue, or subprocess

No Colibrì performance result is represented as NexusNet runtime evidence. NexusNet promotion requires its own profile-specific correctness, quality, latency, throughput, memory, trace, and hardware evidence.
