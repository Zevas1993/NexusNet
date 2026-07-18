import sys

from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.accelerator_packs.worker_factory import WorkerAdapterFactory
from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph, HardwareNode
from datetime import datetime, timezone


def test_worker_factory_resolves_declared_python_token_without_mutating_manifest():
    graph = HardwareCapabilityGraph(
        host_fingerprint="host::factory",
        collected_at=datetime.now(timezone.utc),
        nodes=[HardwareNode(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu")],
        links=[],
        adapters=[],
    )
    candidate = BuiltInPackCatalog().candidates(graph)[0]
    factory = WorkerAdapterFactory(interpreter=sys.executable)

    adapter = factory.create(candidate.manifest, environment={"NEXUSNET_TORCH_BACKEND": "cpu"})
    try:
        health = adapter.health()
    finally:
        adapter.supervisor.stop()

    assert health["available"] is True
    assert health["pack_id"] == "org.nexusnet.cpu.reference"
    assert candidate.manifest.launch.command[0] == "python"
