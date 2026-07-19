import pytest
from pydantic import ValidationError


def test_manifest_is_strict_versioned_and_serializes_declared_capabilities(manifest_factory):
    manifest = manifest_factory()

    assert manifest.schema_version == "1.0"
    assert manifest.pack_id == "org.nexusnet.test.cuda"
    assert manifest.execution_modes[0].value == "gpu"
    assert manifest.artifacts[0].sha256 == "a" * 64

    with pytest.raises(ValidationError):
        manifest.__class__.model_validate({**manifest.model_dump(mode="json"), "undeclared_field": True})


def test_hybrid_mode_requires_an_explicit_hybrid_offload_capability(manifest_factory):
    with pytest.raises(ValidationError, match="hybrid-offload"):
        manifest_factory(execution_modes=["hybrid"])

    manifest = manifest_factory(execution_modes=["gpu", "hybrid"], capabilities=["streaming", "hybrid-offload"])
    assert [mode.value for mode in manifest.execution_modes] == ["gpu", "hybrid"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"minimum_os_build": "26100"},
        {"minimum_os_build": True},
        {"artifacts": [{"url": "https://example.invalid/worker.zip", "size_bytes": "1024", "sha256": "a" * 64}]},
        {"device_matches": [{"accelerator_apis": ["cuda"], "minimum_memory_bytes": "1024"}]},
        {"health_probe": {"operation": "health", "timeout_ms": True}},
    ],
)
def test_security_and_lifecycle_integers_are_type_strict(manifest_factory, overrides):
    with pytest.raises(ValidationError):
        manifest_factory(**overrides)


@pytest.mark.parametrize(
    "url",
    [
        "file:///untrusted/worker.zip",
        "http://example.invalid/worker.zip",
        "https://user:secret@example.invalid/worker.zip",
        "https://example.invalid/worker.zip#fragment",
        "https://example.invalid/worker\n.zip",
        "https://example.invalid:bad/worker.zip",
        r"https://example.invalid\@evil.invalid/worker.zip",
        "https://example.invalid/%2e%2e/private.zip",
        "https://example.invalid/%252e%252e/private.zip",
        "https://example.invalid/bin%5cworker.zip",
        "https://example.invalid/worker%0a.zip",
        r"https://example\invalid/worker.zip",
        "https://example.invalid/worker.zip?next=%250a",
        "https://example.invalid/worker.zip?next=\\",
    ],
)
def test_artifact_urls_require_sanitized_https_transport(manifest_factory, url):
    with pytest.raises(ValidationError, match="artifact URL"):
        manifest_factory(artifacts=[{"url": url, "size_bytes": 1024, "sha256": "a" * 64}])


@pytest.mark.parametrize(
    "launch",
    [
        {"command": ["../worker.exe"]},
        {"command": [r"C:\worker.exe"]},
        {"command": ["worker.exe\n"]},
        {"command": ["worker.exe", "../outside"]},
        {"command": ["worker.exe"], "working_directory_ref": "../outside"},
        {"command": ["worker.exe"], "environment_allowlist": ["TEMP=outside"]},
        {"command": ["worker.exe"], "environment_allowlist": ["TEMP", "temp"]},
    ],
)
def test_worker_launch_references_are_normalized_and_sanitized(manifest_factory, launch):
    with pytest.raises(ValidationError):
        manifest_factory(launch=launch)


@pytest.mark.parametrize(
    ("field", "probe"),
    [
        ("health_probe", {"operation": "benchmark", "timeout_ms": 5000}),
        ("self_test_probe", {"operation": "health", "timeout_ms": 30000}),
        ("benchmark_probe", {"operation": "self_test", "timeout_ms": 60000}),
    ],
)
def test_named_probes_require_their_matching_operation(manifest_factory, field, probe):
    with pytest.raises(ValidationError, match="probe operation"):
        manifest_factory(**{field: probe})


def test_approved_manifest_collections_are_deeply_immutable_and_json_serializable(manifest_factory):
    manifest = manifest_factory(dependency_constraints={"runtime": ">=1.0"})

    with pytest.raises(AttributeError):
        manifest.capabilities.append("undeclared")
    with pytest.raises(TypeError):
        manifest.dependency_constraints["runtime"] = "unbounded"
    with pytest.raises(AttributeError):
        manifest.launch.command.append("--unsafe")

    dumped = manifest.model_dump(mode="json")
    assert dumped["capabilities"] == ["streaming"]
    assert dumped["dependency_constraints"] == {"runtime": ">=1.0"}


def test_default_dependency_constraints_are_also_immutable(manifest_factory):
    manifest = manifest_factory()
    payload = manifest.model_dump(mode="json")
    payload.pop("dependency_constraints")
    admitted = manifest.__class__.model_validate(payload)

    with pytest.raises(TypeError):
        admitted.dependency_constraints["runtime"] = "unbounded"


def test_nested_contracts_reject_extra_fields_invalid_hashes_and_bounds(manifest_factory):
    with pytest.raises(ValidationError):
        manifest_factory(artifacts=[{
            "url": "https://example.invalid/worker.zip",
            "size_bytes": 1024,
            "sha256": "not-a-digest",
            "undeclared": True,
        }])
    with pytest.raises(ValidationError):
        manifest_factory(artifacts=[{
            "url": "https://example.invalid/worker.zip",
            "size_bytes": 0,
            "sha256": "a" * 64,
        }])
    with pytest.raises(ValidationError):
        manifest_factory(benchmark_probe={"operation": "benchmark", "timeout_ms": 300_001})
