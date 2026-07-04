# Verified Semantic Cache Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet RAG, model routing, and privacy gates.

## Source Evidence

- GPTCache GitHub repository: https://github.com/zilliztech/GPTCache
- RedisVL semantic cache API docs: https://redis.io/docs/latest/develop/ai/redisvl/0.12.0/api/cache/
- Redis semantic caching guide: https://redis.github.io/redis-vl-java/redisvl/current/llmcache.html
- LangChain cache reference: https://api.python.langchain.com/en/latest/community/cache.html
- Source status: official project docs and source repositories.

## Finding

Semantic caches reuse responses based on embedding similarity rather than exact prompt identity. This can reduce latency and cost, but agent systems need stronger safety controls than normal LLM apps because cached answers may ignore current state, permissions, private context, or tool results.

## NexusNet Assimilation Target

Create a verified semantic cache that only returns cached model/tool answers when the semantic match, source state, policy context, privacy class, and freshness window all pass. Treat cache hits as evidence candidates, not unconditional truth.

## Proposed NexusNet Components

- `SemanticCacheKey`: prompt embedding, normalized task intent, model route, tool state, and privacy class.
- `StateDependencyFingerprint`: hashes of sources, memory entries, tool outputs, policy version, and flag assignments.
- `CacheSafetyPolicy`: decides which lanes can use exact, semantic, or no cache.
- `CacheHitVerifier`: confirms similarity threshold, state fingerprint, citations, freshness, and authority class.
- `CacheInvalidationTrace`: records why a cached response was skipped or invalidated.

## Promotion Gates

- Disable semantic cache for private, state-changing, high-authority, or legal/medical/financial outputs unless exact state fingerprinting exists.
- Require citation/source compatibility for grounded answers.
- Record cache hit/miss, similarity, and invalidation reason in traces.
- Separate embedding cache from answer cache.
- Include adversarial tests for stale, permission-mismatched, and near-neighbor wrong cache hits.

## Risks

- Semantically similar prompts can require different answers.
- Cached responses can leak private context if privacy class is wrong.
- Cache savings can hide quality regressions unless hits are sampled and verified.
