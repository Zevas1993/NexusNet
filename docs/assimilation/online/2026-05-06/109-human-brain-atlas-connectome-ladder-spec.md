# Human Brain Atlas Connectome Ladder Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet memory, model-routing, and architecture surfaces.

## Source Evidence

- Human Connectome Project official site: https://www.humanconnectomeproject.org/
- Human Connectome Project NIMH overview: https://www.nimh.nih.gov/research/research-funded-by-nimh/research-initiatives/human-connectome-project-hcp
- BRAIN Initiative Cell Atlas Network: https://braininitiative.nih.gov/research/tools-and-technologies-brain-cells-and-circuits/brain-initiative-cell-atlas-network
- Allen Brain Atlas Cell Types Database: https://celltypes.brain-map.org/
- EBRAINS human brain atlas: https://www.ebrains.eu/brain-atlases/reference-atlases/human-brain/
- Source status: official neuroscience atlas and data infrastructure pages.

## Finding

The strongest current brain-mapping work is not one magic upload map. It is a ladder of partial maps: macroscale connectivity, cell-type atlases, molecular profiles, anatomical regions, functional imaging, and multilevel atlas infrastructure. NexusNet should treat the brain as a layered reference architecture, not a single graph to copy.

## NexusNet Assimilation Target

Create a brain-atlas-inspired architecture map for NexusNet. Every model, memory surface, tool lane, policy layer, and runtime should have a place in a multiscale atlas: macro-area, circuit, cell-type analog, signal type, plasticity rule, and evidence status.

## Proposed NexusNet Components

- `CognitiveAtlasNode`: model, memory, tool, policy, router, evaluator, or operator surface.
- `AtlasScale`: macro lane, circuit cluster, micro function, signal type, or cell-role analog.
- `ConnectivityMap`: directed and recurrent links among NexusNet components with strength, authority, and evidence class.
- `CellTypeAnalogy`: stable role taxonomy such as fast relay, inhibitory gate, integrator, novelty detector, replay store, or global broadcaster.
- `AtlasCoverageReport`: maps which NexusNet capabilities have evidence-backed placement and which are speculative.

## Promotion Gates

- Keep biological analogy labels separate from implementation claims.
- Use public atlas data as inspiration for structure, not as evidence that NexusNet is brain-equivalent.
- Require live repo mapping before moving any atlas role into code.
- Track source status for each brain-inspired mapping.
- Prefer multiscale diagrams over one flat "neural brain" diagram.

## Risks

- Brain analogies can become marketing language if not tied to concrete system roles.
- Human brain atlases are incomplete and measured at different scales.
- Structure alone does not imply cognition; dynamics, learning, embodiment, and development matter.
