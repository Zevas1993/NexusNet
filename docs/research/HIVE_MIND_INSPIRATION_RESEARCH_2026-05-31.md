# Hive Mind - Sources of Inspiration (Canon + Online Research)

Status: research document. Earlier work covered the NEURAL-NETWORK inspirations (Capsule Nets, EBT,
attention, MoE) but skipped the HIVE-MIND / collective-intelligence inspirations. This doc digs the
book for what the canon actually says NexusNet's hive mind is modeled on, and researches the real
science/algorithms behind each so they become computable mechanisms, not flavor.

Canon sources: canon book C06M0122/0123/0175/0183, C12M0027, C37M0146/0162, C34M0021, C39M0035;
substrate spec section 2.2 "Hive Mind Sources"; post-book PB-017 (neuroplasticity fabric).

## 1. What the canon actually says the hive mind IS
- The NexusNet **Core is itself a neural network** (input->hidden->output) acting as the **master
  brain at the centre of the hive**, with neural connections to every expert mini-brain / capsule
  (C06M0122/0123). "Each mini brain is its own neural network in the grand scheme of the total hive
  mind neural network" (C06M0021).
- The Core is the **"conductor" of the system's collective intelligence**: it does not solve domain
  problems directly; it manages which capsule does what and when, then synthesizes outputs (C12M0027).
- Canon names a **Collective Intelligence Framework** with three explicit protocols (C37M0146):
  `knowledge_distillation`, `differential_evolution`, `swarm_intelligence`. Plus **Neural Sleep**,
  **Model Birth Protocol**, **Independence Milestones**, **self-modification** (C37M0162).
- **Hive-wide neuroplasticity** (PB-017): everything connects to everything via typed contracts;
  sparse activation controls compute, not awareness; any node can request research/dream/eval.

So the hive mind = a central neural Core conducting many specialist neural sub-brains, coordinating
through collective-intelligence protocols, under governed neuroplasticity.

## 2. Hive-mind sources the substrate spec lists (fictional pattern -> safe inversion)
The substrate spec (section 2.2) explicitly assimilates collective-organism patterns WITH safety
inversions. These are not decoration; each maps to a real algorithm (section 3):
| Source pattern | Assimilated trait | Safety inversion (canon) |
| --- | --- | --- |
| Borg (Star Trek) | rapid assimilation, shared collective memory | permissioned, sandboxed, ledgered, reversible, non-coercive |
| Zerg (StarCraft) | fast specialization, essence extraction | extract reusable traits from candidates, not takeover |
| Tyranid synapse | distributed synapse nodes coordinate specialists | SynapseRelays = bounded, revocable coordination |
| Flood/Gravemind | critical-mass memory -> higher-order mind | key-mind clusters quarantined, provenance-scored |
| Geth (Mass Effect) | networked consensus intelligence | consensus for routing/promotion, not identity erasure |
| Social insects | stigmergy / pheromone trails | HiveBlackboard priority trails decay + are audited |
| Honeybee democracy | quorum + stop-signal group choice | promotion requires quorum + explicit stop-signal |
| Siphonophores | specialized organisms = one organism | AOs/Mini-NexusNets = organs of one harness brain |
| Hermes Curator | scheduled skill cleanup/grading | Curator can archive/propose, not mutate protected canon |

## 3. The real science behind the collective-intelligence protocols (researched 2026-05-31)
These turn the fictional/biological inspiration into deterministic, computable mechanisms.

### 3.1 Stigmergy (ant colony / HiveBlackboard)
Indirect coordination through environment marks: agents deposit "pheromone," others follow it; trails
**evaporate** so stale paths fade. ACO update (computable):
`tau_ij <- (1 - rho) * tau_ij + sum_k delta_tau_ij^k`  (rho = evaporation rate; delta = deposit by
agents that used edge ij, e.g. `Q / cost_k`). NexusNet use: the HiveBlackboard priority trails are
pheromone; routing affinity = trail strength; **decay (rho) is mandatory** so old routes fade and the
trail is auditable. Invariant: with no deposits, all trails decay to 0 (no permanent silent bias).

### 3.2 Quorum sensing (honeybee democracy / promotion)
A colony acts only after a critical density of agreement. Computable: a candidate accumulates support
votes; commit only when `support_fraction >= quorum_threshold` AND no active stop-signal. NexusNet
use: this is the canon's promotion quorum + stop-signal (immune veto). Invariant: below quorum or with
an active stop-signal, no promotion - balances decision speed vs accuracy.

### 3.3 Swarm decision-making (PSO/ABC consensus)
Decentralized agents share opinions, explore alternatives, converge by voting/negotiation. PSO update
(computable): `v <- w*v + c1*r1*(pbest - x) + c2*r2*(gbest - x)`, `x <- x + v` - each particle pulled
toward its own best and the global best. NexusNet use: route/parameter consensus across capsules; the
"gbest" is the Cortex's global pick, "pbest" each capsule's local model (ties to reference-frame swarm).

### 3.4 Differential Evolution (canon `differential_evolution` for expert evolution)
Population-based optimizer (Storn-Price). Exact operators:
- **Mutation**: `v_i = x_r1 + F * (x_r2 - x_r3)`  (r1,r2,r3 distinct; F in [0,2] scale factor)
- **Crossover**: `u_i[j] = v_i[j] if rand()<=CR else x_i[j]`  (CR in [0,1])
- **Selection**: keep `u_i` if `fitness(u_i)` better than `fitness(x_i)`, else keep `x_i`.
NexusNet use: evolve expert genomes / router policies / prompt-policies as a population; fitness = eval
scorecard. This is the computable engine behind "Recursive Neural Dreaming generates expert
combinations" + GrowthArchive. Invariant: selection is elitist (population fitness never decreases).

### 3.5 Knowledge distillation (canon `knowledge_distillation`, Ivy-League teachers)
Teacher(s) -> student via soft targets: `L = alpha * CE(student, hard_labels) + (1-alpha) *
T^2 * KL(softmax(student/T), softmax(teacher/T))` (T = temperature). NexusNet use: the Ivy-League
School distills teacher models into expert students; the parent-retirement review (PB-020) is
distillation-grade. Computable KL/temperature terms; invariant: KL >= 0, =0 iff distributions match.

### 3.6 Neural sleep / consolidation (hippocampal replay, target 117)
Wake = capture traces; sleep = replay important events, strengthen useful patterns, weaken noise,
extract abstractions. Computable: prioritized replay (sample by salience/TD-error), running EMA of
pattern strength, threshold to promote an abstraction. Invariant: replay distribution sums to 1.

## 4. How this binds to the neural-network engineering blueprint
The neural side (capsules + EBT + MoE) is HOW a single brain instance computes; the hive side
(stigmergy + quorum + swarm + DE + distillation + sleep) is HOW many brain instances COORDINATE,
EVOLVE, and CONSOLIDATE as one collective. Together:
- Capsules emit pose vectors -> stigmergic trails on the HiveBlackboard mark useful routes.
- Routing-by-agreement + PSO/swarm consensus pick the active set; EBT energy refines the decision.
- Promotion needs quorum + stop-signal (honeybee); evolution of experts uses DE; teachers distill
  the winners; neural sleep consolidates traces into durable abstractions.
- All under PB-017 neuroplasticity (everything connected, sparsely activated, fully monitored, gated).

## 5. Buildable mapping (modular, pure-Python, shadow-only, additive)
New self-contained modules (each TDD with the exact formula invariants above):
- `nexusnet/hive/collective/stigmergy.py` - pheromone trail + evaporation (ACO update).
- `nexusnet/hive/collective/quorum.py` - quorum + stop-signal promotion gate.
- `nexusnet/hive/collective/swarm_consensus.py` - PSO-style route/parameter consensus.
- `nexusnet/hive/collective/differential_evolution.py` - expert/policy population evolution.
- `nexusnet/hive/collective/distillation.py` - KD soft-target loss (teacher->student).
- `nexusnet/hive/collective/neural_sleep.py` - prioritized replay + abstraction extraction.
These compose with the capsule/EBT kernel (engineering blueprint section 6). The collective layer
proposes; the existing policy/eval/governance gates still decide. Shadow-only; no production mutation.

## 6. Boundaries (canon safety inversions, unchanged)
Assimilate the IDEAS, not the fiction's coercion (C08M0006). Borg/Zerg/Tyranid/Gravemind patterns are
permissioned, sandboxed, ledgered, reversible, consensus-based, non-coercive. No consciousness/upload/
physics claims. Pheromone trails decay and are audited; quorum + stop-signal required for promotion;
DE/KD/sleep run shadow-only and feed the gated promotion pipeline, never bypass it.

## Sources
Canon (in repo): canon book messages cited inline; substrate spec section 2.2; PB-017.
External (researched 2026-05-31):
- Swarm intelligence / stigmergy / quorum: https://www.sciencedirect.com/topics/computer-science/swarm-intelligence-algorithm , https://medium.com/@jsmith0475/collective-stigmergic-optimization-leveraging-ant-colony-emergent-properties-for-multi-agent-ai-55fa5e80456a , https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10217149/
- Differential Evolution: https://www.sciencedirect.com/topics/computer-science/differential-evolution-algorithm , https://www.mdpi.com/2227-7390/12/15/2311
- (Capsule Nets, EBT, MoE, etc. in the engineering blueprint + math docs.)
