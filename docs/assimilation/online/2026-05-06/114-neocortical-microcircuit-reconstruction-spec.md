# Neocortical Microcircuit Reconstruction Spec

Status: P1 online assimilation target. Research-only until translated into small NexusNet circuit experiments.

## Source Evidence

- Blue Brain digital reconstruction page: https://bbp.epfl.ch/bbp/research/domains/bluebrain/blue-brain/about/digital-reconstruction/
- Blue Brain Portal: https://portal.bluebrain.epfl.ch/
- Blue Brain simulation page: https://bluebrain.epfl.ch/bbp/research/domains/bluebrain/index.html%3Fp%3D505.html
- Cell paper page for neocortical microcircuit reconstruction: https://www.cell.com/cell/fulltext/S0092-8674(15)01191-5
- Source status: official project pages and primary journal page.

## Finding

Blue Brain's reconstruction work treats a cortical microcircuit as a data-integrated digital object: morphology, electrical properties, synapses, cell types, and simulated experiments. For NexusNet, the target is microcircuit design discipline: build small detailed circuits with measurable behavior instead of vague whole-brain diagrams.

## NexusNet Assimilation Target

Create small NexusNet microcircuits with known roles: perception, working memory, inhibitory gate, hippocampal replay, global broadcast, novelty detection, and consolidation. Each circuit should be executable, ablatable, and measurable.

## Proposed NexusNet Components

- `NexusMicrocircuit`: small component graph with typed nodes, recurrent edges, gates, and update rules.
- `CircuitMorphology`: readable diagram of layers, loops, inhibition, broadcast, and local memory.
- `InSilicoExperiment`: deterministic test that stimulates the circuit and records behavior.
- `AblationReport`: behavior difference after disabling a node, edge, or gate.
- `CircuitLibrary`: approved reusable microcircuits for NexusNet architecture.

## Promotion Gates

- Every microcircuit needs a clear behavior target.
- Require ablation tests before calling a circuit important.
- Keep circuits small enough to inspect and replay.
- Link each biological inspiration to a concrete software function.
- Avoid claiming cortical equivalence.

## Risks

- Detailed simulation can become expensive and distract from product behavior.
- Biological microcircuits are not directly portable to transformer systems.
- Circuit libraries need governance or they become decorative diagrams.
