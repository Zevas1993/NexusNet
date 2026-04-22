# Gateway Skills Approvals

## Canon
- Gateway remains a subordinate NexusNet-owned local runtime pattern.
- It does not replace the brain/wrapper path and does not create a second control plane.

## Operational Additions
- Resolution history with `resolution_id`, timestamps, selected skill packages, policy path, approval path, and fallback reason
- Explicit matched-package provenance from skill precedence resolution
- Deny-by-default behavior on ambiguous execution binding remains intact
- Read-only inspection through wrapper and ops endpoints

## Policy Outcomes
- `allow`
- `deny`
- `ask`
- `allow-if-approved`

## Inspection Surfaces
- `/ops/brain/gateway`
- `/ops/brain/wrapper-surface`
