# GFlowNet Diverse Thought Factory Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet research, design, and self-improvement proposal generation.

## Source Evidence

- Yoshua Bengio GFlowNet overview: https://yoshuabengio.org/en/blog/generative-flow-networks
- GFlowNet documentation: https://gflownet.readthedocs.io/
- GFlowNet introduction docs: https://gflownet.readthedocs.io/en/latest/get_started/introduction.html
- GFlowNets for scientific discovery paper: https://pubs.rsc.org/en/content/articlehtml/2023/dd/d3dd00002h
- Source status: official project docs, primary researcher overview, and peer-reviewed application paper.

## Finding

GFlowNets are designed to sample diverse high-reward compositional objects, not just the single best object. That is important for NexusNet because breakthroughs often come from preserving multiple strange but promising candidates rather than hill-climbing one obvious plan.

## NexusNet Assimilation Target

Create a diverse thought factory for NexusNet. It should generate many high-value candidate architectures, tool plans, memory structures, prompts, policies, and experiments, proportional to reward but preserving diversity and ancestry.

## Proposed NexusNet Components

- `CompositionalIdeaState`: partial candidate made of approved primitives.
- `ThoughtFlowPolicy`: forward/backward construction policy for candidate ideas.
- `RewardProxy`: scores novelty, feasibility, evidence support, safety, and NexusNet fit.
- `DiverseCandidateSet`: sampled set of high-reward non-identical candidates.
- `IdeaAncestryGraph`: records how candidates were constructed and revised.

## Promotion Gates

- Reward proxies must include safety and evidence terms, not only novelty.
- Keep candidate generation separate from production mutation.
- Require human review before a candidate becomes an implementation plan.
- Preserve low-probability high-upside candidates when they pass safety filters.
- Test against mode collapse where all candidates become the same obvious idea.

## Risks

- Reward design can distort the candidate search.
- Diversity without feasibility can become noise.
- The thought factory can generate persuasive but unsupported plans unless source evidence is mandatory.
