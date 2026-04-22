# NexusNet Visual Spec

## Canon Status
- Core neural structure: `LOCKED CANON`
- Authoritative 19 expert capsules: `LOCKED CANON`
- Dream / critique / consequence loops: `LOCKED CANON`
- Renderer policy: `LOCKED CANON`
- Optional Three.js enhancement path: `STRONG ACCEPTED DIRECTION`

## Purpose
The NexusNet visual subsystem is a read-only inspection surface for the brain-first architecture. It must show the NexusNet core as a real neural structure, the authoritative 19 experts as mini-brains, hive-mind links, recursive cognitive loops, and governed overlays from teacher, promotion, foundry, and runtime posture data.

## Canonical Rendering Rules
- One canonical visualizer only: `/ui/visualizer/`.
- Default renderer path: repo-local HTML/CSS/JS with layered SVG + Canvas.
- Repo-local Three.js is allowed only where depth, parallax, deep zoom, or capsule interiors materially benefit fidelity.
- No external CDN dependencies.
- `ui/3d/` remains a legacy shim that redirects to the canonical visualizer.

## Structural Requirements
- `NexusNet Core` is represented as a layered neural sculpture with internal substructure.
- The authoritative 19-core expert roster is the default capsule ring.
- Auxiliary roles remain auxiliary and off by default.
- Core-to-capsule and capsule-to-capsule links form a hive topology.
- Recursive Dreaming, Skeptical Critique, and Consequence Feedback are visually distinct loops.
- Safe mode, thermal mode, VRAM pressure, and retry/fallback posture are representable as physiology overlays.

## Overlay Policy
- Overlay sources are read-only and come from existing NexusNet surfaces.
- Teacher, benchmark, threshold, promotion, takeover, fleet, cohort, and retirement evidence must appear as optional inspectable overlays where available.
- Missing telemetry is shown as inactive or unbound, never fabricated.

## Live Telemetry Contract
- `GET /ops/brain/visualizer/state` must expose structured:
  - `link_activity`
  - `loop_activity`
  - `evidence_activity`
  - `physiology_activity`
  - `telemetry_window`
  - `telemetry_sources`
  - `filter_catalog`
  - `diff_catalog`
  - `replay_catalog`
  - `performance_profile`
- Link emphasis, loop pulse strength, and physiology posture in the visualizer should derive from those values rather than random animation.
- When live telemetry is sparse, the visualizer should degrade to inactive or low-intensity channels without breaking the scene.
- Telemetry providers are layered:
  - wrapper snapshot state
  - trace store history
  - brain telemetry logs
  - simulated fallback when live sources are sparse
- Provider binding state must remain inspectable from the visualizer operator panels.
- Provider provenance should expose:
  - provider kind
  - signal counts
  - latest trace reference when available
  - bound vs degraded health summary
  - log-channel coverage where available

## Inspection Workflows
- The visualizer supports read-only filtering by registry layer, expert capsule, teacher pair, promotion kind, takeover posture, benchmark family, threshold set, lineage, and recent trace window.
- Read-only compare workflows are supported for:
  - teacher evidence bundles
  - disagreement artifacts
  - replacement-readiness reports
  - route-activity windows
  - fleet / cohort window comparisons where the teacher governance layer exposes them
- Compare payloads should carry scene-aware delta hints so differences can be highlighted in the neural scene, not only in side panels.
- Scene-aware compare now includes:
  - subject delta badges in the neural scene
  - link delta badges on hot edges
  - cohort/fleet window deltas that can light up affected subject and collaboration links
- Replay is bounded and read-only. It replays recent route, loop, and governance emphasis without mutating underlying NexusNet state.
- Replay inspection now includes:
  - scrubber selection
  - anchor-frame comparison
  - live-vs-frame comparison
  - replay source provenance when available
  - timeline browsing with stable frame metadata
  - compare-now-vs-then workflow from the same canonical scene

## Depth Inspection
- The canonical visualizer may host a bounded depth subrenderer inside the same `/ui/visualizer/` surface.
- Depth inspection is optional, read-only, and subordinate to the main SVG + Canvas scene.
- Current bounded depth inspection supports:
  - selected core or capsule interior cross-section
  - render-tier-aware point budgets
  - mesh-link projection between internal neural nodes
  - port-anchor cues derived from topology motifs
  - graceful fallback when depth mode is disabled
- This depth panel does not create a second visualizer and does not replace the main scene.

## Physiology And Fallback
- Safe Mode should intentionally contract and simplify the scene rather than making it look broken.
- Thermal posture should remain explicit in both engineering and cinematic modes.
- VRAM pressure must remain representable even when unbound or unavailable.
- RAM pressure may remain degraded/unbound until a stronger runtime source exists, but the channel should still be visible.
- Retry and fallback posture should surface as visible backflow or pulse reuse, not silent state changes.
- The visualizer must support render tiers:
  - `full`
  - `balanced`
  - `safe`
- Reduced-fidelity tiers preserve engineering readability and keep the scene usable on weaker systems.
- Client-side render-tier adaptation may further constrain the server-recommended tier based on frame budget, reduced-motion preference, and low-power posture.
- Production visualizer fallback behavior additionally includes:
  - explicit low-power clamp
  - hidden-tab downgrade / animation pause behavior
  - reduced ambient-field density under safe or low-power tiers
  - continued operator readability even when depth or richer animation is suppressed

## Integration Points
- Static scene assets live under `ui/visualizer/data/`.
- Canonical config lives under `nexusnet/visuals/`.
- Live overlay state is served from `GET /ops/brain/visualizer/state`.
- Bounded replay is served from `GET /ops/brain/visualizer/replay`.
- Read-only compare helpers are served from:
  - `GET /ops/brain/visualizer/disagreements/compare`
  - `GET /ops/brain/visualizer/replacement-readiness/compare`
  - `GET /ops/brain/visualizer/route-activity/compare`
  - existing teacher evidence/cohort compare endpoints reused from the teacher governance surfaces
- The existing wrapper `/ui/` remains the operational shell and links to the visualizer without losing its current role.
