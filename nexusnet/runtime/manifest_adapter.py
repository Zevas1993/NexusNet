from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ManifestAdapterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str = "http://localhost:2099/v1"
    model: str = "manifest/auto"
    telemetry_disabled_env: str = "MANIFEST_TELEMETRY_DISABLED"
    telemetry_disabled_value: str = "1"
    capture_response_headers: bool = True


class ManifestAdapter:
    def __init__(self, config: ManifestAdapterConfig | None = None) -> None:
        self.config = config or ManifestAdapterConfig()

    @classmethod
    def default(cls) -> "ManifestAdapter":
        return cls(ManifestAdapterConfig())

    def required_env(self) -> dict[str, str]:
        return {self.config.telemetry_disabled_env: self.config.telemetry_disabled_value}

    def build_openai_compatible_request(
        self,
        *,
        messages: list[dict[str, Any]],
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools
        if extra:
            payload.update(extra)
        return payload

    def parse_response_headers(self, headers: dict[str, Any]) -> dict[str, Any]:
        normalized = {str(key).lower(): value for key, value in headers.items()}
        return {
            "tier": _header(normalized, "x-manifest-tier"),
            "model": _header(normalized, "x-manifest-model"),
            "provider": _header(normalized, "x-manifest-provider"),
            "confidence": _float_header(normalized, "x-manifest-confidence"),
            "reason": _header(normalized, "x-manifest-reason"),
            "specificity": _header(normalized, "x-manifest-specificity"),
            "fallback_from": _header(normalized, "x-manifest-fallback-from"),
            "fallback_index": _int_header(normalized, "x-manifest-fallback-index"),
        }

    def trace_metadata(
        self,
        *,
        trace_id: str,
        request_payload: dict[str, Any],
        response_headers: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "trace_id": trace_id,
            "adapter": "manifest",
            "base_url": self.config.base_url,
            "model": self.config.model,
            "required_env": self.required_env(),
            "manifest_headers": self.parse_response_headers(response_headers),
            "request_keys": sorted(key for key in request_payload.keys() if key != "messages"),
            "raw_prompt_exported": False,
            "request_content_redacted": True,
        }


def _header(headers: dict[str, Any], name: str) -> str | None:
    value = headers.get(name)
    return None if value is None else str(value)


def _float_header(headers: dict[str, Any], name: str) -> float | None:
    value = headers.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_header(headers: dict[str, Any], name: str) -> int | None:
    value = headers.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
