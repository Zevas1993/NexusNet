# Goose Compare Views

## Scope
- Goose-derived compare endpoints now have first-class read-only operator controls in the visualizer and wrapper-facing inspection surfaces.
- Compare workflows remain subordinate to NexusNet governance and do not create a second UI or control plane.

## Supported Compare Views
- gateway execution artifact A vs B
- policy-set version A vs B
- certification artifact A vs B
- adversary-review report A vs B
- ACP provider readiness/probe report A vs B

## Visualizer Controls
- `Compare Gateway`
- `Compare Policies`
- `Compare Certifications`
- `Compare Adversary`
- `Compare ACP`
- `Goose Diff Filters`
- `Expand All Groups`
- `Collapse All Groups`
- `Reset Group Filters`

## Human-Readable Output
- compare cards now show:
  - left/right artifact identities
  - human summary
  - export/report IDs
  - summarized diff chips
  - scene-reference summary
  - grouped and collapsible diff sections
  - raw diff only as a drill-down section

## Grouped Diff Sections
- compare cards now group large Goose payloads into read-only operator sections such as:
  - policy lifecycle
  - certification state
  - permission deltas
  - approval or fallback changes
  - ACP readiness and remediation
  - adversary outcome changes
  - gateway execution path changes
  - trace and artifact deltas
- the visualizer overlay and wrapper surface both expose the canonical Goose compare group catalog so UI grouping stays aligned with the read-only backend surfaces.

## Filter And Collapse Controls
- large compare payloads now support explicit category filtering instead of forcing operators to scan every grouped section at once
- filters align to the canonical Goose compare categories exposed by the backend surfaces:
  - `policy-lifecycle`
  - `certification-state`
  - `permission-deltas`
  - `approval-fallback`
  - `acp-readiness`
  - `adversary-outcome`
  - `gateway-execution-path`
  - `trace-and-artifacts`
- the default expanded set favors the highest-signal governance groups:
  - policy lifecycle
  - certification state
  - ACP readiness
- stable IDs, export IDs, report IDs, and evidence links remain visible while filters or collapse actions are applied

## Endpoints
- `GET /ops/brain/gateway/history/compare`
- `GET /ops/brain/extensions/policy-history/compare`
- `GET /ops/brain/extensions/certifications/compare`
- `GET /ops/brain/security/adversary-reviews/compare`
- `GET /ops/brain/acp/providers/compare`
