# Goose Extension Bundle Governance

## Scope
- Goose-inspired extensions are now treated as governed bundle artifacts, not just catalog rows.
- Enablement remains subordinate to NexusNet gateway, permissions, sandboxing, ACP diagnostics, and approval logic.

## Bundle Artifact Fields
- bundle ID
- policy-set ID and version
- bundle family
- enabled or disabled state
- workspace scope
- roots
- allowed tools
- inherited permissions
- ACP compatibility summary
- approval path
- sandbox posture
- risk flags
- provenance artifact ID
- report ID

## Current Governance Rules
- bundles outside workspace scope are denied
- disabled bundles are denied
- high-risk or ACP-facing bundles move to `allow-if-approved`
- bundle-level privilege escalation and ACP inheritance confusion are surfaced for bounded review
- versioned policy sets now govern baseline bundle families instead of relying only on static maps

## Operator Surfaces
- `GET /ops/brain/extensions`
- `GET /ops/brain/extensions/policy-sets`
- `GET /ops/brain/extensions/policy-sets/{policy_set_id}`
- `GET /ops/brain/extensions/policy-history`
- `GET /ops/brain/extensions/policy-history/compare`
- `GET /ops/brain/extensions/policy-rollouts`
- `GET /ops/brain/extensions/certifications`
- `GET /ops/brain/extensions/certifications/compare`
- `GET /ops/brain/extensions/certifications/{artifact_id}`
- `GET /ops/brain/extensions/{bundle_id}`
- gateway history and resolution artifacts carry selected bundle IDs and provenance
- wrapper surface and visualizer expose latest governed bundle IDs and report IDs read-only

## Lifecycle and Certification Additions
- bundle detail now links the governing policy lifecycle artifact and report
- certification artifacts now record certification status, ACP inheritance confusion, remediation actions, and linked adversary-review report IDs
- policy lifecycle history and bundle certification remain inspectable read-only through the same extension surface
- certification compare output is read-only and highlights certification-state changes, allowed-tool drift, risk-flag deltas, remediation changes, and adversary-review linkage differences
- certification drill-down now also exposes stable lineage IDs, supersession references, permission deltas, policy lineage status history, and restoration detection when a bundle returns from rolled-back or superseded policy lineage
- policy and certification compare flows now emit operator-facing compare reports instead of existing only as transient HTTP payloads
- certification lineage depth is now backed by stored historical certification artifacts, not only current-artifact restoration inference
- certification detail and bundle provenance now expose historical certification artifact IDs, lineage-status sequences, restoration targets, and latest transition summaries
- certification compare exports now group state, lineage, permission, and remediation drift for read-only operator review
- stored certification history now spans multiple governed bundle families:
  - filesystem bridge lineage with superseded, rolled-back, and restored phases
  - retrieval-pack lineage with rollback, supersession, and restored continuity
  - ACP provider lineage with superseded, held, shadow-approved, and restored continuity
- the same extension detail surface now exposes stable lineage IDs and historical certification artifact anchors across those families instead of keeping that history implicit

## Closeout Note
- Goose-derived extension governance is operationally sufficient for the current governed families.
- Additional family expansion should stay deferred unless a new governed bundle family appears in-repo or operators identify a concrete audit gap.

## Sources
- Goose docs: https://goose-docs.ai/
- Goose repository: https://github.com/aaif-goose/goose
