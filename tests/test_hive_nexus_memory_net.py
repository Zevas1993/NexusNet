from __future__ import annotations

from nexusnet.hive.memory import (
    NexusMemoryNet,
    sparse_pre_filter,
    semantic_compress,
    dual_track_attention,
    external_memory_router,
    compressed_summary,
    long_context_scale,
)


# --- 1. sparse pre-filter ---

def test_pre_filter_keeps_top_relevance_fraction():
    res = sparse_pre_filter(relevances=[0.1, 0.9, 0.4, 0.8, 0.2], keep_fraction=0.4)
    assert res["kept_count"] == 2
    assert res["kept_indices"] == [1, 3]      # the two highest


def test_pre_filter_keeps_at_least_one():
    res = sparse_pre_filter(relevances=[0.1, 0.2, 0.3], keep_fraction=0.01)
    assert res["kept_count"] == 1


# --- 2. semantic compressor ---

def test_semantic_compress_assigns_every_token_to_nearest_centroid():
    vectors = [[0.0, 0.0], [0.1, 0.1], [9.0, 9.0], [9.1, 8.9]]
    res = semantic_compress(vectors=vectors, num_clusters=2, iterations=10)
    assert res["num_clusters"] == 2
    # the two near-origin tokens share a cluster; the two near (9,9) share the other
    a = res["assignments"]
    assert a[0] == a[1]
    assert a[2] == a[3]
    assert a[0] != a[2]


# --- 3. dual-track attention ---

def test_dual_track_attentions_each_sum_to_one():
    res = dual_track_attention(
        query=[1.0, 0.0],
        local_track=[[1.0, 0.0], [0.0, 1.0]],
        global_track=[[0.5, 0.5], [1.0, 1.0], [0.0, 1.0]],
        local_gate=0.6,
    )
    assert abs(sum(res["local_attention"]) - 1.0) < 1e-9
    assert abs(sum(res["global_attention"]) - 1.0) < 1e-9
    assert len(res["combined"]) == 2


# --- 4. external memory router ---

def test_router_prefers_external_only_beyond_margin():
    assert external_memory_router(in_context_score=0.5, external_score=0.9)["route"] == "external_memory"
    assert external_memory_router(in_context_score=0.5, external_score=0.52)["route"] == "in_context"


# --- 5. compressed summary injector ---

def test_compressed_summary_is_weighted_mean():
    summary = compressed_summary(centroids=[[2.0, 0.0], [0.0, 2.0]])
    assert summary == [1.0, 1.0]


# --- 6. position encoding overhaul ---

def test_long_context_scale_extends_and_floors_at_one():
    assert long_context_scale(trained_context=4096, target_context=1_000_000) > 1.0
    assert long_context_scale(trained_context=8192, target_context=4096) == 1.0


# --- end-to-end ---

def test_nexus_memory_net_pipeline_is_gated_and_consistent():
    net = NexusMemoryNet(keep_fraction=0.6, num_clusters=3, local_gate=0.5)
    tokens = [[float(i % 3), float((i + 1) % 2), 0.5] for i in range(20)]
    rel = [0.05 * i for i in range(20)]
    out = net.process(token_vectors=tokens, relevances=rel, query=[1.0, 0.0, 0.5])
    assert out["pre_filter"]["kept_count"] == 12          # ceil(0.6*20)
    assert out["num_centroids"] == 3
    assert out["dual_track"]["local_attention_sums_to_one"] is True
    assert out["dual_track"]["global_attention_sums_to_one"] is True
    assert out["memory_route"] in {"in_context", "external_memory"}
    assert out["long_context_scale"] > 1.0
    assert out["production_mutation_allowed"] is False
