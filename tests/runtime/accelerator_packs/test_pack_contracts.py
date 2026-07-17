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
