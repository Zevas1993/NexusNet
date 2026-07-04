# Neuromorphic Event Driven Substrate Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet local runtime and edge-inference needs.

## Source Evidence

- Intel Loihi 2 technology brief page: https://www.intel.com/content/www/us/en/research/neuromorphic-computing-loihi-2-technology-brief.html
- Intel Loihi 2 PDF brief: https://download.intel.com/newsroom/2021/new-technologies/neuromorphic-computing-loihi-2-brief.pdf
- SpiNNaker documentation page: https://docs.hpc.gwdg.de/services/neuromorphic-computing/spinnaker/index.html
- Nengo documentation: https://www.nengo.ai/nengo/
- Source status: official vendor/project documentation.

## Finding

Neuromorphic systems emphasize sparse event-driven computation, spiking signals, local learning, asynchronous updates, and energy efficiency. NexusNet can borrow this as an execution strategy even on normal hardware: do not recompute the whole brain when only a few signals changed.

## NexusNet Assimilation Target

Add a neuromorphic-inspired event substrate for NexusNet: sparse activations, local route updates, event streams, plasticity hooks, and energy/latency-aware scheduling. This should complement transformer inference rather than replace it.

## Proposed NexusNet Components

- `SpikeEvent`: sparse activation event with source, target, time, strength, and semantic class.
- `EventDrivenRouter`: wakes only affected components rather than polling every lane.
- `LocalPlasticityRule`: bounded update rule for route weights, memory salience, and evaluator confidence.
- `EnergyLatencyMeter`: tracks compute saved by sparse execution.
- `SpikingSandboxAdapter`: optional future adapter for neuromorphic hardware or spiking simulation.

## Promotion Gates

- Start with software event sparsity before hardware dependency.
- Require deterministic replay for sparse event schedules.
- Limit plasticity to reviewable route/memory/eval metadata, not uncontrolled model mutation.
- Compare latency and quality against normal batch execution.
- Keep hardware-specific code optional.

## Risks

- Spiking/neuromorphic ecosystems are less mature than GPU transformer stacks.
- Sparse events can miss global context if routing is too local.
- Plasticity can accumulate drift unless bounded and audited.
