# Intrinsic Motivation Empowerment Drive Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet developmental curriculum and safety gates.

## Source Evidence

- Intrinsic motivation systems record: https://web-archive.southampton.ac.uk/cogprints.org/5473/
- Intrinsic motivation systems PDF: https://www.pyoudeyer.com/ims.pdf
- Empowerment paper record: https://cir.nii.ac.jp/crid/1360292619337222400
- Schmidhuber curiosity page: https://people.idsia.ch/~juergen/curioussingapore/curioussingapore.html
- Source status: primary paper records and author/project pages.

## Finding

Intrinsic motivation research offers a better growth signal than vague autonomy: seek learning progress, compressibility improvement, and controllable states. Empowerment adds an information-theoretic measure of how much influence an agent can perceive itself as having over its environment.

## NexusNet Assimilation Target

Create a developmental drive system for NexusNet that selects tasks because they improve the system's world model, not because they are random, flashy, or immediately profitable. The drive should prefer "learnable frontier" tasks: neither already solved nor pure noise.

## Proposed NexusNet Components

- `LearningProgressSignal`: improvement in prediction, compression, retrieval, planning, or eval score.
- `EmpowermentEstimate`: safe measure of controllable future options inside a sandboxed task world.
- `DevelopmentalCuriosityQueue`: tasks selected for expected learning progress and bounded risk.
- `BoredomFilter`: demotes tasks that no longer improve the model.
- `SafeExplorationBudget`: limits compute, authority, privacy exposure, and time.

## Promotion Gates

- Curiosity must be bounded by safety, privacy, cost, and operator goals.
- Prefer sandbox worlds for self-directed exploration.
- Measure learning progress against held-out tasks, not only training reward.
- Prevent empowerment drive from seeking real-world control for its own sake.
- Log why a task was selected and what was learned.

## Risks

- Intrinsic motivation can reward risky exploration if constraints are weak.
- Empowerment language can be misread as self-preservation.
- Learning progress metrics can be gamed by creating artificial confusion.
