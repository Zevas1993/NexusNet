# Context Compression Governor Spec

Status: P2 online assimilation target. Research-only until measured against NexusNet long-context, memory, and RAG workloads.

## Source Evidence

- LLMLingua repository: https://github.com/microsoft/LLMLingua
- LLMLingua paper: https://arxiv.org/abs/2310.05736
- LongLLMLingua paper: https://arxiv.org/abs/2310.06839
- SnapKV repository: https://github.com/FasterDecoding/SnapKV
- H2O repository: https://github.com/FMInference/H2O
- Source status: public repositories and primary paper pages.

## Finding

Prompt and KV-cache compression research shows real latency and cost opportunities, but also correctness risk. Compressing instructions, memory, retrieved evidence, or long chat state can silently drop the exact detail needed for a safe action.

## NexusNet Assimilation Target

Create a context compression governor that treats compression as a policy-controlled transform. NexusNet should know which context segments may be compressed, which must stay verbatim, and which require post-compression validation.

## Proposed NexusNet Components

- `ContextSegmentPassport`: source, role, data class, mutability, citation need, and compression eligibility.
- `CompressionPolicy`: never compress, lossy compress, extractive summarize, cache compress, or verbatim required.
- `CompressionDiffReport`: removed facts, retained anchors, token savings, and risk score.
- `CriticalFactVerifier`: checks that names, numbers, dates, policies, code, citations, and approvals survived compression.
- `CompressionRegressionSuite`: tests compressed prompts against uncompressed baselines.

## Promotion Gates

- Never lossy-compress policy, approvals, secrets, code diffs, citations, or exact user constraints without explicit verifier coverage.
- Measure answer quality and tool safety, not only token savings.
- Record compression version and retained source anchors in traces.
- Disable compression for high-authority actions until proven safe.

## Risks

- Compression can remove rare but critical constraints.
- KV-cache methods and prompt compression methods have different safety profiles.
- Token savings can mask increased hallucination, citation drift, or tool misuse.
