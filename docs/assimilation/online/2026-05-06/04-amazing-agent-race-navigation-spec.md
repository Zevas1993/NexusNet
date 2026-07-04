# Amazing Agent Race Navigation Spec

Status: P1 online assimilation target. Research-only until project assets are inspected.

## Source Evidence

- The Amazing Agent Race paper page: https://huggingface.co/papers/2604.10261
- Project page listed by the paper: https://minnesotanlp.github.io/the-amazing-agent-race
- Source status: primary paper index with project link.

## Finding

The benchmark uses DAG-style navigation and tool-use puzzles. Its important lesson for NexusNet is that many agents fail by navigating to the wrong context, not by failing to call tools. Wrong-page drift, search spirals, and compensatory tool use can look active while the agent is operating on bad evidence.

## NexusNet Assimilation Target

Improve retrieval and browser/navigation planning by scoring whether the agent is on the right evidence path before letting tool use continue. Navigation quality should be a first-class signal beside answer correctness.

## Proposed NexusNet Components

- `EvidencePathPlan`: expected sources, branch points, merge points, and stop conditions.
- `NavigationDriftDetector`: flags repeated searches, wrong-source loops, and tool calls on untrusted context.
- `PitStopMetric`: tracks whether required intermediate evidence nodes were actually visited.
- `Retrieval Planner UI`: shows current branch, skipped branches, and drift warnings.

## Promotion Gates

- Add deterministic fixture tasks before using live web browsing.
- Require source-status updates when the agent switches branches.
- Treat extra searching as potential failure, not automatically as diligence.

## Risks

- Live web drift makes reproduction hard.
- Over-constraining navigation can block legitimate alternate paths.
- Search-provider results are unstable and need dated capture.
