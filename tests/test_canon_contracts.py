from pathlib import Path

import nexusnet.canon.contracts as contracts


def _write_canon_sources(project_root: Path) -> None:
    for index, source_ref in enumerate(contracts.CANON_CONTRACT_SOURCE_REFS):
        path = project_root / source_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Canon source {index}\nwrapper federation assimilation\n", encoding="utf-8")


def test_ingested_source_record_rebuilds_canonical_keywords_after_module_state_contamination(
    tmp_path: Path,
    monkeypatch,
):
    source = tmp_path / "canon-source.md"
    source.write_text(
        "# Wrapper federation\nAssimilation research drives self-repair and expert growth.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        contracts,
        "_canonical_keyword_pairs",
        lambda: ("corrupted-entry",),
        raising=False,
    )

    record = contracts._ingested_source_record(
        contracts.CANON_CONTRACT_SOURCE_REFS[0],
        path=source,
        resolved_from="test-fixture",
    )

    assert record["status"] == "ingested"
    assert record["keyword_counts"]["wrapper"] == 1
    assert record["keyword_counts"]["federation"] == 1
    assert record["keyword_counts"]["assimilation"] == 1
    assert record["keyword_counts"]["self-repair"] == 1
    assert record["keyword_counts"]["expert"] == 1


def test_canon_source_manifest_cache_is_content_aware_and_returns_isolated_snapshots(
    tmp_path: Path,
    monkeypatch,
):
    _write_canon_sources(tmp_path)
    contracts._cached_canon_source_manifest.cache_clear()

    first = contracts.build_canon_source_manifest(tmp_path)
    first_digest = first["sources"][0]["sha256"]
    first["sources"][0]["status"] = "caller-contaminated"

    original_open = Path.open

    def fail_canon_reopen(path: Path, *args, **kwargs):
        if any(path == tmp_path / source_ref for source_ref in contracts.CANON_CONTRACT_SOURCE_REFS):
            raise AssertionError("unchanged Canon sources must be served from the fingerprint cache")
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as cache_hit_patch:
        cache_hit_patch.setattr(Path, "open", fail_canon_reopen)
        second = contracts.build_canon_source_manifest(tmp_path)

    assert second["sources"][0]["status"] == "ingested"
    assert second["sources"][0]["sha256"] == first_digest

    changed = tmp_path / contracts.CANON_CONTRACT_SOURCE_REFS[0]
    changed.write_text("# Changed Canon source\nwrapper federation assimilation research\n", encoding="utf-8")
    third = contracts.build_canon_source_manifest(tmp_path)

    assert third["sources"][0]["sha256"] != first_digest
    assert third["sources"][0]["keyword_counts"]["research"] == 1
