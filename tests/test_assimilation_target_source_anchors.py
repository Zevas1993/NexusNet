from __future__ import annotations

from pathlib import Path

from nexusnet.operations.assimilation_targets import AssimilationTargetRegistry


def test_every_assimilation_target_has_a_source_local_implementation_anchor():
    registry = AssimilationTargetRegistry()
    targets = [*registry.scorecard()["targets"], *registry.video_scorecard()["targets"]]
    repository_root = Path(__file__).resolve().parents[1]

    assert targets
    for target in targets:
        anchor_refs = target["implementation_refs"]
        implementation_source_refs = target["implementation_source_refs"]
        assert anchor_refs, target["target_id"]
        assert implementation_source_refs, target["target_id"]
        for anchor_ref in anchor_refs:
            anchor_path = repository_root / anchor_ref
            assert anchor_path.is_file(), anchor_ref
            assert f"Target ID: `{target['target_id']}`" in anchor_path.read_text(encoding="utf-8")
        for source_ref in implementation_source_refs:
            assert (repository_root / source_ref).is_file(), source_ref
