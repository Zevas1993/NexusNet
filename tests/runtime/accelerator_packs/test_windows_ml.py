from __future__ import annotations

from datetime import datetime, timezone

from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.accelerator_packs.windows_ml import (
    WindowsMlCatalog,
    WindowsMlProviderObservation,
)
from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph, HardwareNode


def _provider(
    name: str,
    *,
    backend: str,
    state: str = "ready",
    version: str = "1.0.0",
    device_kind: str = "gpu",
) -> WindowsMlProviderObservation:
    return WindowsMlProviderObservation(
        provider_name=name,
        provider_version=version,
        backend=backend,
        state=state,
        certified=True,
        device_kind=device_kind,
        device_node_id="cpu:0" if device_kind == "cpu" else "gpu:0",
    )


def _graph() -> HardwareCapabilityGraph:
    return HardwareCapabilityGraph(
        host_fingerprint="host::windows-ml",
        collected_at=datetime.now(timezone.utc),
        nodes=[
            HardwareNode(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu"),
            HardwareNode(node_id="gpu:0", kind="gpu", name="GPU", backend="portable"),
        ],
        links=[],
        adapters=[],
    )


def test_windows_ml_dynamic_catalog_requires_build_26100_and_runtime() -> None:
    old = WindowsMlCatalog.discover(os_build=26099, runtime_version="2.0.0", providers=[])
    missing = WindowsMlCatalog.discover(os_build=26100, runtime_version=None, providers=[])

    assert old.available is False
    assert old.reason_codes == ("windows-build-below-26100",)
    assert missing.available is False
    assert missing.reason_codes == ("windows-ml-runtime-unavailable",)


def test_windows_ml_enumerates_and_explicitly_selects_ready_provider() -> None:
    discovery = WindowsMlCatalog.discover(
        os_build=26100,
        runtime_version="2.1.0",
        providers=[
            _provider("CPUExecutionProvider", backend="cpu", device_kind="cpu"),
            _provider("DmlExecutionProvider", backend="directml"),
        ],
    )

    selected = discovery.select("DmlExecutionProvider")

    assert discovery.available is True
    assert [provider.provider_name for provider in discovery.providers] == [
        "CPUExecutionProvider",
        "DmlExecutionProvider",
    ]
    assert selected.available is True
    assert selected.provider_name == "DmlExecutionProvider"
    assert selected.reason_codes == ("explicit-provider-ready",)


def test_windows_ml_auto_uses_cpu_only_when_directml_is_not_ready() -> None:
    discovery = WindowsMlCatalog.discover(
        os_build=26100,
        runtime_version="2.1.0",
        providers=[
            _provider("DmlExecutionProvider", backend="directml", state="not-present"),
            _provider("CPUExecutionProvider", backend="cpu", device_kind="cpu"),
        ],
    )

    forced = discovery.select("DmlExecutionProvider")
    automatic = discovery.select("auto")

    assert forced.available is False
    assert forced.provider_name is None
    assert forced.reason_codes == ("explicit-provider-unavailable",)
    assert automatic.provider_name == "CPUExecutionProvider"
    assert automatic.reason_codes == ("auto-cpu-fallback",)


def test_provider_version_changes_invalidate_provider_evidence() -> None:
    first = _provider("DmlExecutionProvider", backend="directml", version="1.0.0")
    second = _provider("DmlExecutionProvider", backend="directml", version="1.1.0")

    assert first.evidence_token != second.evidence_token


def test_catalog_projects_windows_ml_candidates_as_unverified() -> None:
    discovery = WindowsMlCatalog.discover(
        os_build=26100,
        runtime_version="2.1.0",
        providers=[
            _provider("DmlExecutionProvider", backend="directml"),
            _provider("CPUExecutionProvider", backend="cpu", device_kind="cpu"),
        ],
    )

    candidates = BuiltInPackCatalog().candidates(_graph(), windows_ml=discovery)
    by_id = {candidate.manifest.pack_id: candidate for candidate in candidates}

    assert "org.nexusnet.windows-ml.directml" in by_id
    assert "org.nexusnet.windows-ml.cpu" in by_id
    assert by_id["org.nexusnet.windows-ml.directml"].verification_state == "unverified"
    assert "provider-correctness-unverified" in by_id["org.nexusnet.windows-ml.directml"].reason_codes
