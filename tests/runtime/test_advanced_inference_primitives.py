from __future__ import annotations

from nexusnet.runtime.advanced_inference import (
    GrammarConstrainedDecoder,
    LearnedCascadeRouter,
    SpeculativeDecoder,
    VerifiedSemanticCache,
)


def test_grammar_decoder_selects_only_schema_valid_candidate():
    decoder = GrammarConstrainedDecoder()
    result = decoder.select(
        candidates=['{"answer": 7}', '{"answer": "wrong"}', "not-json"],
        schema={"type": "object", "required": ["answer"], "properties": {"answer": {"type": "integer"}}},
    )
    assert result["value"] == {"answer": 7}
    assert result["rejected_count"] == 0


def test_speculative_decoder_verifies_drafts_and_falls_back_on_rejection():
    decoder = SpeculativeDecoder()
    drafts = iter([["A", "B", "BAD"], ["C", "D"]])
    result = decoder.decode(
        prompt_tokens=["P"],
        max_new_tokens=5,
        draft=lambda _context, _remaining: next(drafts, []),
        verify=lambda _context, token: token != "BAD",
        fallback=lambda _context: "FIX",
    )
    assert result["tokens"] == ["A", "B", "FIX", "C", "D"]
    assert result["accepted_draft_tokens"] == 4
    assert result["fallback_tokens"] == 1


def test_learned_cascade_updates_route_from_feedback():
    router = LearnedCascadeRouter(
        models={
            "small": {"weights": {"complexity": -0.5}, "cost": 0.1},
            "large": {"weights": {"complexity": 0.2}, "cost": 0.9},
        }
    )
    before = router.route({"complexity": 1.0})
    for _ in range(8):
        router.update(model_id="large", features={"complexity": 1.0}, reward=1.0, learning_rate=0.25)
    after = router.route({"complexity": 1.0})
    assert before["model_id"] == "small"
    assert after["model_id"] == "large"
    assert after["learned"] is True


def test_semantic_cache_requires_similarity_and_evidence_version_match():
    cache = VerifiedSemanticCache(similarity_threshold=0.95)
    cache.put(
        cache_id="cache:1",
        vector=[1.0, 0.0],
        value={"answer": 42},
        evidence_version="source:v1",
        verification_refs=["eval:1"],
    )
    assert cache.get(vector=[0.99, 0.01], evidence_version="source:v1")["hit"] is True
    assert cache.get(vector=[0.99, 0.01], evidence_version="source:v2")["hit"] is False
