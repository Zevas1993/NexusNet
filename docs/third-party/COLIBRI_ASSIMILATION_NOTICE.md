# Colibrì Assimilation Notice

NexusNet's native MoE residency work was informed by the Apache-2.0 licensed Colibrì project:

- Repository: <https://github.com/JustVugg/colibri>
- Reviewed revision: `748787c3afa8ab336bb51bf616f212a04f209bba`
- License: Apache License 2.0; the complete retained license is at
  [`licenses/Apache-2.0-Colibri.txt`](licenses/Apache-2.0-Colibri.txt).

Assimilation classification: **independent behavioral assimilation**. NexusNet
implements the useful behavior through NexusNet-owned Python contracts and did
not copy or embed the Colibrì runtime, provider, server, CLI, queue, or process.

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

## Reproducible source boundary

| Role | Path | SHA-256 |
|---|---|---|
| Reviewed upstream | `c/tier.h` | `93c2a90ebb233f30a9cf1a5adb6228583ab4ad9ca9caad1bd5bfdcf336364625` |
| Reviewed upstream | `c/resource_plan.py` | `dfd18afc3e419c6a8afba97d3d893ec69ca4db4b41560abc910fd94e052f797c` |
| Independent NexusNet implementation | `nexusnet/runtime/moe_residency/heat.py` | `7b0eec65dba422090e86588ee70ddd6d00e8de3edffb7934a697b835e98e7bfb` |
| Independent NexusNet implementation | `nexusnet/runtime/moe_residency/planner.py` | `edbf4dd163e059b3bdc66743e4c01da7920540393e2e9779a5cc9ac69799b96f` |

Review and verification are executable in
`tests/runtime/test_moe_residency.py`, including plan admission, immutable
digest-verified shards, bounded cache/prefetch behavior, native MoE execution,
target-verified speculation, runtime evidence, and this provenance record.
