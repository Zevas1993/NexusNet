# Embeddable Agent Core Spec

Status: P2 online assimilation target. Research-only architecture comparison.

## Source Evidence

- Sema Code paper: https://arxiv.org/abs/2604.11045
- OpenDev paper: https://arxiv.org/abs/2603.05344
- OpenHands repository: https://github.com/OpenHands/OpenHands
- Source status: primary paper pages and public repository page.

## Finding

Several recent agent systems are moving away from product-form-specific assistants toward reusable agent cores. The recurring mechanisms are engine/client separation, isolated sessions, FIFO or controlled input queues, adaptive context compression, explicit permission layers, multi-agent scheduling, background tasks, and sandboxed execution.

## NexusNet Assimilation Target

Use these systems as architecture comparison targets for NexusNet's native brain and Control Panel. NexusNet should keep one governed brain path while exposing different clients or surfaces around it, rather than duplicating reasoning kernels per UI.

## Proposed NexusNet Components

- `AgentCoreBoundaryDoc`: defines what belongs in the NexusNet brain versus UI/client adapters.
- `SessionReconstructionLog`: lets background or resumed work reconstruct state without private implicit context.
- `PermissionLayerMatrix`: separates observe, propose, edit, execute, publish, and delegate authority.
- `ContextCompactionTrace`: records what was compacted, retained, and excluded.

## Promotion Gates

- Treat competitor architecture as clean-room inspiration only.
- Do not import licenses or code without review.
- Preserve NexusNet brain-first routing and refs-only knowledge boundaries.

## Risks

- "Embeddable core" can become a vague architecture slogan without testable boundaries.
- Multi-agent scheduling can create coordination overhead if not tied to disjoint ownership.
- Background task privilege must not exceed visible session privilege.
