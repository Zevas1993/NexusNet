import pytest

from nexusnet.runtime.accelerator_packs.contracts import RuntimePackManifest


@pytest.fixture
def manifest_factory():
    def build(**overrides):
        payload = {
            "pack_id": "org.nexusnet.test.cuda",
            "version": "1.0.0",
            "pack_type": "native-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows"],
            "architectures": ["amd64"],
            "workload_kinds": ["llm-generate"],
            "model_formats": ["gguf"],
            "accelerator_apis": ["cuda"],
            "device_matches": [{"vendor_ids": ["10de"], "accelerator_apis": ["cuda"]}],
            "minimum_os_build": 26100,
            "dependency_constraints": {},
            "launch": {"command": ["worker.exe"], "environment_allowlist": ["TEMP", "TMP"]},
            "execution_modes": ["gpu"],
            "health_probe": {"operation": "health", "timeout_ms": 5000},
            "self_test_probe": {"operation": "self_test", "timeout_ms": 30000},
            "benchmark_probe": {"operation": "benchmark", "timeout_ms": 60000},
            "artifacts": [
                {
                    "url": "https://example.invalid/worker.zip",
                    "size_bytes": 1024,
                    "sha256": "a" * 64,
                }
            ],
            "capabilities": ["streaming"],
            "known_limitations": [],
            "rollback_compatible_from": ["0.9.0"],
            "data_migration_policy": "none",
        }
        payload.update(overrides)
        return RuntimePackManifest.model_validate(payload)

    return build
