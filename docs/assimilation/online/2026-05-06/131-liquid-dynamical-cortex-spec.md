# Liquid Dynamical Cortex Spec

Status: P2 final-pass assimilation target. Research-only until NexusNet needs time-continuous, edge-efficient adaptive controllers.

## Source Evidence

- Liquid Time-Constant Networks arXiv page: https://arxiv.org/abs/2006.04439
- MIT CSAIL liquid network navigation article: https://www.csail.mit.edu/news/drones-navigate-unseen-environments-liquid-neural-networks
- MIT CSAIL closed-form continuous-time article: https://www.csail.mit.edu/news/solving-brain-dynamics-gives-rise-flexible-machine-learning-models
- Liquid Time-Constant universal approximator paper: https://arxiv.org/abs/1811.00321
- Source status: primary paper pages and official MIT CSAIL articles.

## Finding

Liquid neural networks and closed-form continuous-time models represent computation as adaptive dynamics over time rather than fixed feed-forward passes. The useful NexusNet transfer is not replacing LLMs; it is adding small adaptive controllers for continuous telemetry, routing, and embodied edge behavior.

## NexusNet Assimilation Target

Use liquid dynamical controllers for NexusNet lanes that need continuous adaptation: health telemetry, sensor streams, latency/cost control, local robot/device loops, memory salience decay, and homeostatic state regulation.

## Proposed NexusNet Components

- `LiquidController`: small continuous-time or recurrent controller for a bounded control loop.
- `TimeConstantTrace`: tracks how quickly a controller adapts under changing conditions.
- `DynamicalStateProbe`: inspects hidden state, stability, and response to perturbation.
- `EdgeAdaptationPolicy`: decides when liquid controllers are useful versus ordinary rules.
- `ControllerFallback`: deterministic fallback when the learned dynamics become unstable.

## Promotion Gates

- Limit liquid controllers to narrow, measurable control loops.
- Test stability under distribution shift and perturbations.
- Preserve deterministic fallback for safety-critical actions.
- Do not use liquid dynamics for opaque high-authority decisions without explanation gates.
- Compare against simpler rule-based controllers.

## Risks

- Continuous dynamics can be hard to interpret and debug.
- Learned controllers can drift in unexpected environments.
- The benefit may be small unless the lane has real temporal dynamics.
