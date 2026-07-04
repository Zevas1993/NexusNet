from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.cache_ledger import CacheLedgerEntryRequest, EffectiveContextCacheLedger
from tests.test_nexus_phase1_foundation import make_project


def test_effective_context_cache_ledger_records_measured_kv_cache_posture():
    ledger = EffectiveContextCacheLedger()

    entry = ledger.record(
        CacheLedgerEntryRequest(
            entry_id="cache::long-context-turboquant",
            runtime_id="runtime::vllm-local",
            model_id="open-model::long-context",
            workload_id="workload::research-canon",
            raw_context_tokens=128000,
            effective_context_tokens=96000,
            cached_prefix_tokens=42000,
            kv_cache_policy="turboquant-like",
            kv_bit_width=3.5,
            prefix_cache_hit_rate=0.72,
            kv_cache_hit_rate=0.64,
            cache_bytes_gpu=8_589_934_592,
            cache_bytes_cpu=17_179_869_184,
            cache_bytes_disk=34_359_738_368,
            privacy_scope="project",
            owner_ref="project::nexusnet",
            source_hashes=["sha256:canon-prompt-pack"],
            recall_score=0.88,
            latency_ttft_ms=840,
            decode_tokens_per_sec=92.5,
            eviction_policy="heavy-hitter-recent",
            evidence_refs=["bench::needle-recall", "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
        )
    )

    assert entry["status_label"] == "LOCKED CANON"
    assert entry["authority"] == "NexusBrain"
    assert entry["surface_id"] == "effective-context-cache-ledger"
    assert entry["status"] == "measured"
    assert entry["context_economics"]["raw_context_tokens"] == 128000
    assert entry["context_economics"]["effective_context_tokens"] == 96000
    assert entry["context_economics"]["effective_context_ratio"] == 0.75
    assert entry["kv_cache"]["policy"] == "turboquant-like"
    assert entry["kv_cache"]["bit_width"] == 3.5
    assert entry["policy_scan"]["summary"]["allow_merge"] is True


def test_effective_context_cache_ledger_blocks_private_remote_shared_cache_without_redaction():
    ledger = EffectiveContextCacheLedger()

    entry = ledger.record(
        {
            "entry_id": "cache::private-remote-shared",
            "runtime_id": "runtime::cloud-shared",
            "model_id": "model::private",
            "workload_id": "workload::operator-history",
            "raw_context_tokens": 64000,
            "effective_context_tokens": 70000,
            "cached_prefix_tokens": 50000,
            "kv_cache_policy": "lmcache",
            "kv_bit_width": 8,
            "prefix_cache_hit_rate": 0.8,
            "kv_cache_hit_rate": 0.8,
            "privacy_scope": "remote-shared",
            "contains_private_data": True,
            "redaction_verified": False,
            "evidence_refs": [],
        }
    )

    assert entry["status"] == "blocked"
    assert entry["runtime_state"] == "degraded"
    assert entry["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "cache_ledger_private_remote_scope_requires_redaction",
        "cache_ledger_requires_evidence_refs",
        "cache_ledger_effective_context_cannot_exceed_raw_without_explanation",
    }.issubset({finding["rule_id"] for finding in entry["ledger_findings"]})


def test_effective_context_cache_ledger_blocks_upstream_quantization_gate():
    ledger = EffectiveContextCacheLedger()

    entry = ledger.record(
        {
            "entry_id": "cache::blocked-quant-gate",
            "runtime_id": "runtime::vllm-local",
            "model_id": "model::candidate",
            "workload_id": "workload::agentic",
            "raw_context_tokens": 32768,
            "effective_context_tokens": 24000,
            "cached_prefix_tokens": 12000,
            "kv_cache_policy": "fp8",
            "kv_bit_width": 8,
            "prefix_cache_hit_rate": 0.44,
            "kv_cache_hit_rate": 0.33,
            "privacy_scope": "project",
            "recall_score": 0.85,
            "latency_ttft_ms": 900,
            "decode_tokens_per_sec": 72.0,
            "evidence_refs": ["bench::cache"],
            "upstream_quantization_gate": {
                "promotion_allowed": False,
                "status": "blocked",
                "blockers": ["runtime_scorecard_blocked"],
                "source": "quantization_catalog",
            },
        }
    )

    assert entry["status"] == "blocked"
    assert entry["runtime_state"] == "degraded"
    assert entry["promotion_allowed"] is False
    assert "runtime_scorecard_blocked" in entry["promotion_blockers"]
    assert entry["upstream_quantization_gate"]["promotion_allowed"] is False
    assert "cache_ledger_blocks_quantization_gate" in {finding["rule_id"] for finding in entry["ledger_findings"]}

    summary = ledger.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_entry"]["promotion_allowed"] is False


def test_cache_ledger_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/cache-ledger/entries",
        json={
            "entry_id": "cache::api-vllm-prefix",
            "runtime_id": "runtime::api-vllm",
            "model_id": "model::api-open",
            "workload_id": "workload::api-agentic",
            "raw_context_tokens": 32768,
            "effective_context_tokens": 30000,
            "cached_prefix_tokens": 18000,
            "kv_cache_policy": "fp8",
            "kv_bit_width": 8,
            "prefix_cache_hit_rate": 0.66,
            "kv_cache_hit_rate": 0.58,
            "cache_bytes_gpu": 4_294_967_296,
            "privacy_scope": "session",
            "owner_ref": "session::api",
            "source_hashes": ["sha256:api-context"],
            "recall_score": 0.82,
            "latency_ttft_ms": 950,
            "decode_tokens_per_sec": 74.0,
            "eviction_policy": "ttl",
            "evidence_refs": ["bench::api-cache"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "measured"

    summary = client.get("/ops/brain/cache-ledger")
    assert summary.status_code == 200
    assert summary.json()["entry_count"] == 1

    effective = client.get("/ops/brain/runtime/effective-context")
    assert effective.status_code == 200
    assert effective.json()["latest_entry"]["entry_id"] == "cache::api-vllm-prefix"

    scorecard = client.get("/ops/brain/canon/cache-ledger")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record"]["endpoint"] == "/ops/brain/cache-ledger/entries"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "cache-ledger-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["cache_ledger_scorecard"]["entry_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "cache-ledger-cockpit"}).json()
    assert blackbox["scorecard_refs"]["cache_ledger"] == "/ops/brain/canon/cache-ledger"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Effective Context and KV Cache" in ui.text
    assert "cacheLedgerScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderCacheLedgerScorecard" in app_js
    assert "/ops/brain/canon/cache-ledger" in app_js
    assert "Cache upstream quantization gate" in app_js
