# Synapse Connectome Simulation Ladder Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet graph, memory, and simulation infrastructure.

## Source Evidence

- FlyWire Nature collection: https://www.nature.com/collections/hgcfafejia
- Nature interactive FlyWire connectome overview: https://www.nature.com/immersive/d42859-024-00053-4/index.html
- FlyWire neuronal wiring paper: https://www.nature.com/articles/s41586-024-07558-y
- OpenWorm project docs: https://docs.openworm.org/projects/index.html
- NeuroML documentation: https://docs.neuroml.org/
- Source status: primary Nature pages and official open computational-neuroscience project docs.

## Finding

The fly whole-brain connectome and OpenWorm show that a wiring diagram is only a starting point. Useful emulation needs cell identities, synapse types, dynamics, body interaction, environment, and validation against behavior. This is a direct warning against treating NexusNet graphs as intelligence by themselves.

## NexusNet Assimilation Target

Build a connectome simulation ladder for NexusNet architecture experiments. The ladder should let a component graph graduate from static wiring to executable dynamics, embodied task loops, perturbation tests, and behavior validation.

## Proposed NexusNet Components

- `NexusConnectomeGraph`: components, weighted links, recurrent loops, inhibitory gates, and evidence class.
- `DynamicsAnnotation`: update rule, timescale, plasticity rule, decay, and activation constraints.
- `EmbodiedTaskLoop`: environment, sensors, actions, reward/surprise signal, and observed behavior.
- `PerturbationProbe`: ablation, stimulation, noise, link deletion, and routing interruption tests.
- `BehavioralValidityReport`: compares simulated behavior to expected NexusNet lane behavior.

## Promotion Gates

- Do not promote static graphs without dynamic and behavioral tests.
- Require perturbation evidence for important circuit claims.
- Track which edges are designed, learned, inferred, or speculative.
- Keep biological connectome sources separate from NexusNet implementation evidence.
- Use small executable circuits before attempting full-system simulations.

## Risks

- Connectome language can overstate what a graph explains.
- Biological simulations require parameters that are not present in the wiring diagram.
- NexusNet graphs can become too complex unless simulation targets are narrow.
