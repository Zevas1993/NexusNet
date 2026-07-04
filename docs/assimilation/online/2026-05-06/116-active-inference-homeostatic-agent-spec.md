# Active Inference Homeostatic Agent Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet control loops and eval metrics.

## Source Evidence

- Free Energy Principle resource index: https://activeinference.github.io/
- Friston free energy principle paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC3510653/
- Predictive coding under the free-energy principle: https://www.fil.ion.ucl.ac.uk/~karl/Predictive%20coding%20under%20the%20free-energy%20principle.pdf
- Active inference paper resources: https://activeinference.github.io/papers/
- Source status: primary paper and curated active-inference resource pages.

## Finding

Active inference frames agents as systems that act to reduce prediction error and maintain viable states. For NexusNet, the strongest transfer is homeostasis: the system should know its acceptable operating ranges and act to keep itself coherent, grounded, authorized, and useful.

## NexusNet Assimilation Target

Build a homeostatic agent loop for NexusNet. The loop should monitor prediction error, uncertainty, contradiction, resource use, policy risk, and operator satisfaction, then choose actions that restore stable operation rather than blindly maximize task completion.

## Proposed NexusNet Components

- `HomeostaticStateVector`: grounding, uncertainty, authority, cost, latency, memory coherence, and operator confidence.
- `PredictionErrorSignal`: expected versus observed tool results, model outputs, user reactions, and eval scores.
- `ViabilityRange`: acceptable bounds for each state dimension.
- `ActiveInferencePlanner`: chooses information gathering, action, abstention, or escalation to reduce harmful surprise.
- `HomeostasisTrace`: records what variable was out of range and what action corrected it.

## Promotion Gates

- Define measurable state variables before implementing control loops.
- Prefer conservative corrective actions for high-authority risk.
- Test whether the system escalates when uncertainty remains high.
- Keep active-inference language as a control metaphor unless validated.
- Do not let homeostasis become self-preservation against operator intent.

## Risks

- Free-energy language can become too abstract without concrete metrics.
- Bad viability ranges can make the system overcautious or reckless.
- A self-stabilizing agent must remain subordinate to operator control.
