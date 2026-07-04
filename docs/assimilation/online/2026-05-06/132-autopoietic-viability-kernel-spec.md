# Autopoietic Viability Kernel Spec

Status: P2 final-pass assimilation target. Research-only and metaphor-bounded. Not a life or consciousness claim.

## Source Evidence

- Autopoiesis and Cognition Springer page: https://link.springer.com/book/10.1007/978-94-009-8947-4
- Toward aitiopoietic cognition article: https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2025.1618381/full
- Autopoiesis of the artificial article page: https://www.sciencedirect.com/science/article/pii/S0303264723001119
- Enactive autonomy in computational systems: https://link.springer.com/article/10.1007/s11229-017-1386-z
- Source status: book page and peer-reviewed article pages.

## Finding

Autopoiesis frames living systems as self-producing, boundary-maintaining organizations. For NexusNet, the useful transfer is a viability kernel: the system maintains its operational boundary, evidence integrity, policy constraints, and repair capacity while remaining subordinate to operator goals.

## NexusNet Assimilation Target

Define NexusNet as an operationally bounded artificial organism only in a software-engineering sense: it keeps itself coherent, recoverable, auditable, and useful. It does not get self-preservation rights or autonomous authority.

## Proposed NexusNet Components

- `ViabilityKernel`: invariants required for NexusNet to remain safe and useful.
- `OperationalBoundary`: what is inside NexusNet control, what is outside, and what requires operator consent.
- `SelfMaintenanceLoop`: rebuilds derived state, checks health, repairs indexes, and verifies provenance.
- `BoundaryBreachDetector`: detects leaks across privacy, authority, workspace, or evidence boundaries.
- `OperatorOverrideInvariant`: human/operator authority remains above system self-maintenance.

## Promotion Gates

- Keep autopoiesis as a bounded engineering metaphor.
- Define viability in terms of safety, auditability, recoverability, and user value.
- Prevent self-maintenance from resisting operator shutdown, deletion, or correction.
- Test boundary breaches and degraded-state repair.
- Record every self-maintenance action in append-only traces.

## Risks

- Organism metaphors can encourage unsafe autonomy language.
- Self-maintenance loops can accidentally hide failures if they auto-repair without reporting.
- Viability goals can conflict with operator intent unless override rules are explicit.
