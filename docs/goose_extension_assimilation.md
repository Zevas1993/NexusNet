# Goose Extension Assimilation

## Scope
- Goose-inspired extension patterns are assimilated as a NexusNet-owned extension catalog lane.
- This includes enable/disable state, MCP-compatible flags, and workspace/root-aware visibility.

## What Landed
- Extension catalog with read-only enablement state.
- MCP-aware compatibility markers and workspace/root scoping.
- Skill catalog summaries now surface extension context.

## Operationalization
- ACP health and capability diagnostics now sit alongside extension/catalog state so operator surfaces can distinguish enabled catalogs from actually ready external bridges.
- Extension compatibility is now part of ACP provider drill-down and adversary-review inheritance checks, so ACP-capable extension lanes cannot silently widen privilege.
- Extension bundles now persist governed provenance artifacts and markdown/JSON reports instead of existing only as live catalog summaries.
- Bundle detail is exposed read-only through `GET /ops/brain/extensions/{bundle_id}` and linked through gateway execution history.
- Versioned policy sets and bundle families now back extension governance, and those policy-set IDs/versions are inspectable both through bundle detail and through dedicated policy-set summary/detail endpoints.
- Policy sets are now lifecycle-managed artifacts with rollout and rollback lineage, and extension bundles now emit distinct certification artifacts with certification status and privilege inheritance diagnostics.
- Policy-history and certification compare endpoints now let operators compare two governed artifacts read-only instead of reconstructing governance drift from raw JSON.
- Certification drill-down now also exposes lineage anchors, stable certification IDs, permission and risk deltas, restoration detection, and policy-lineage history so operator review can follow bundle governance over time.
- Certification lineage now persists across multiple stored artifacts per bundle so revoked, rolled-back, held, and restored phases remain directly inspectable through the same read-only extension surface.
- Certification lineage depth now spans multiple governed families, including filesystem bridge, retrieval-pack, and ACP-provider bundle families, rather than remaining strongest only on the current artifact chain.

## Boundaries
- Extensions remain subordinate to the NexusNet gateway and wrapper surfaces.
- No separate extension-manager UI or second control plane was introduced.

## Sources
- Goose docs: https://goose-docs.ai/
- Goose repository: https://github.com/aaif-goose/goose
