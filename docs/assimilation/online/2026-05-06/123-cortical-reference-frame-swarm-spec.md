# Cortical Reference Frame Swarm Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet KAC, Hive Mind routing, and Control Panel views.

## Source Evidence

- Numenta Thousand Brains Project release: https://thousandbrains.org/newsroom/press-release/2024/11/20/thousand-brains-project/
- Numenta framework paper page: https://www.numenta.com/resources/research-publications/papers/a-framework-for-intelligence-and-cortical-function-based-on-grid-cells-in-the-neocortex/
- Tolman-Eichenbaum Machine record: https://discovery.ucl.ac.uk/id/eprint/10115119/
- Nature Neuroscience predictive map paper: https://www.nature.com/articles/nn.4650
- Source status: official project pages and primary paper/record pages.

## Finding

The Thousand Brains theory and hippocampal cognitive-map research converge on one useful design pressure: intelligence may depend on many parallel models organized in reference frames, not one monolithic model. Each cortical column can model an object or concept from its own sensorimotor perspective, then a voting/consensus process forms stable recognition and action.

## NexusNet Assimilation Target

Turn NexusNet from a flat assistant into a swarm of cortical reference frames. Each expert lane should maintain a local model of an object, task, project, user goal, codebase, memory region, or tool state. A consensus router should combine those models without forcing them into one lossy summary.

## Proposed NexusNet Components

- `ReferenceFrame`: local coordinate system for a concept, workspace, artifact, or task.
- `CorticalColumnAgent`: specialized lane that learns a complete model from its own perspective.
- `ObjectConsensusVote`: weighted vote among columns about identity, state, risk, or next action.
- `SensorimotorTrace`: action-observation sequence that updates a reference frame.
- `FrameConflictResolver`: handles contradictory local models through evidence, recency, and authority class.

## Promotion Gates

- Require evidence links for every reference-frame update.
- Preserve minority expert votes when they flag risk or contradiction.
- Test whether consensus improves retrieval, planning, and contradiction handling over flat context stuffing.
- Keep private and cross-workspace frames isolated unless the operator explicitly merges them.
- Do not claim biological equivalence; treat this as a software architecture inspired by cortical theory.

## Risks

- Too many local frames can create coordination overhead.
- Consensus can hide rare but important expert warnings.
- Reference-frame language can become decorative unless tied to measurable retrieval and planning gains.
