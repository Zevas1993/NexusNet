# Colibrì MoE Architecture Intake

Target ID: `colibri-moe-architecture-intake`

NexusNet uses the source as a clean-room behavioral reference for explicit
MoE topology accounting, tier-readiness planning, and cache-residency evidence.
The implementation is NexusNet-owned and is deliberately model-family neutral:
it accepts exact layer, expert, KV, and byte-size metadata; it does not infer
unknown layouts from a model name or path.

Implementation seams:

- `architecture.py` calculates CPU/RAM or GPU dense placement, bounded expert
  cache slots, and a storage-bandwidth cold ceiling without loading a model.
- `system.py` accepts only numeric, sanitized residency telemetry after an
  external equivalence result and turns it into the existing evidence stream
  used by Pareto selection and governed evolution.

Boundary: no Colibrì source import, Python dependency, CLI, server, process,
provider, or model weight is part of NexusNet. See
`docs/third-party/COLIBRI_ASSIMILATION_NOTICE.md` for the pinned source and
license boundary.
