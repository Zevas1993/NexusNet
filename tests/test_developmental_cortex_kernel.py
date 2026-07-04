from nexusnet.developmental.kernel import DevelopmentalCortexKernel


def test_developmental_cortex_kernel_returns_non_mutating_growth_packet(tmp_path):
    kernel = DevelopmentalCortexKernel(artifacts_dir=tmp_path)

    result = kernel.assess(
        request_id="dev:req:001",
        task_ref="task:improve-routing",
        trace_refs=["trace:route-1"],
        evidence_refs=["eval:route-shadow", "cache-ledger:baseline"],
        runtime_state={"runtime_state": "live-bound", "provider_count": 2},
        memory_state={"runtime_state": "live-bound", "claim_count": 1},
        authority_state={"runtime_state": "live-bound", "grant_count": 0},
        eval_state={"runtime_state": "live-bound", "suite_count": 1},
    )

    assert result["surface_id"] == "developmental-cortex-kernel"
    assert result["status"] == "shadow-ready"
    assert result["production_mutation_allowed"] is False
    assert result["body_schema_snapshot"]["surface_id"] == "nexus-body-schema"
    assert result["reference_frame"]["frame_id"].startswith("frame:task:")
    assert result["simulation"]["status"] == "shadow-recorded"
    assert result["growth_candidate"]["promotion_state"] == "archived-shadow"
    assert result["promotion_case"]["decision"] == "accepted-shadow"
