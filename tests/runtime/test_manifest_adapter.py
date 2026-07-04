from __future__ import annotations

import importlib

import pytest


def _adapter_module():
    try:
        return importlib.import_module("nexusnet.runtime.manifest_adapter")
    except ModuleNotFoundError as exc:
        pytest.fail(f"manifest adapter module is missing: {exc}")


def test_manifest_adapter_requires_telemetry_opt_out_and_uses_auto_model():
    module = _adapter_module()
    adapter = module.ManifestAdapter.default()

    assert adapter.config.base_url == "http://localhost:2099/v1"
    assert adapter.config.model == "manifest/auto"
    assert adapter.required_env() == {"MANIFEST_TELEMETRY_DISABLED": "1"}

    payload = adapter.build_openai_compatible_request(
        messages=[{"role": "user", "content": "route this cheaply"}],
        max_tokens=128,
        tools=[{"type": "function", "function": {"name": "noop"}}],
    )

    assert payload["model"] == "manifest/auto"
    assert payload["max_tokens"] == 128
    assert payload["messages"][0]["content"] == "route this cheaply"
    assert payload["tools"][0]["function"]["name"] == "noop"


def test_manifest_adapter_parses_manifest_meta_headers_without_raw_prompt_export():
    module = _adapter_module()
    adapter = module.ManifestAdapter.default()

    metadata = adapter.parse_response_headers(
        {
            "X-Manifest-Tier": "complex",
            "X-Manifest-Model": "provider/model",
            "X-Manifest-Provider": "openai",
            "X-Manifest-Confidence": "0.87",
            "X-Manifest-Reason": "complexity route",
            "X-Manifest-Specificity": "coding",
            "X-Manifest-Fallback-From": "provider/old",
            "X-Manifest-Fallback-Index": "2",
        }
    )

    assert metadata["tier"] == "complex"
    assert metadata["model"] == "provider/model"
    assert metadata["provider"] == "openai"
    assert metadata["confidence"] == 0.87
    assert metadata["specificity"] == "coding"
    assert metadata["fallback_from"] == "provider/old"
    assert metadata["fallback_index"] == 2

    trace = adapter.trace_metadata(
        trace_id="trace::manifest",
        request_payload={"messages": [{"role": "user", "content": "private prompt"}]},
        response_headers={"X-Manifest-Tier": "standard", "X-Manifest-Provider": "ollama"},
    )

    assert trace["trace_id"] == "trace::manifest"
    assert trace["adapter"] == "manifest"
    assert trace["raw_prompt_exported"] is False
    assert trace["request_content_redacted"] is True
    assert trace["manifest_headers"]["tier"] == "standard"
    assert trace["manifest_headers"]["provider"] == "ollama"
    assert "messages" not in trace
