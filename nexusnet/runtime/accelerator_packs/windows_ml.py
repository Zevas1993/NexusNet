from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, computed_field, field_validator

from nexusnet.runtime.hardware_contracts import AcceleratorBackend


class WindowsMlProviderObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider_name: StrictStr = Field(min_length=1)
    provider_version: StrictStr = Field(min_length=1)
    backend: AcceleratorBackend
    state: Literal["ready", "not-present", "unavailable"]
    certified: StrictBool
    device_kind: Literal["cpu", "gpu"]
    device_node_id: StrictStr = Field(min_length=1)

    @field_validator("provider_name", "provider_version", "device_node_id")
    @classmethod
    def sanitize_text(cls, value: str) -> str:
        if value != value.strip() or any(ord(character) < 32 for character in value):
            raise ValueError("Windows ML provider evidence must be sanitized")
        return value

    @computed_field
    @property
    def evidence_token(self) -> str:
        payload = {
            "provider_name": self.provider_name,
            "provider_version": self.provider_version,
            "backend": self.backend,
            "state": self.state,
            "certified": self.certified,
            "device_kind": self.device_kind,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return f"windows-ml-provider::{digest}"


class WindowsMlProviderDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    available: StrictBool
    provider_name: StrictStr | None = None
    backend: AcceleratorBackend | None = None
    provider_version: StrictStr | None = None
    evidence_token: StrictStr | None = None
    reason_codes: tuple[StrictStr, ...]


class WindowsMlDiscovery(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    os_build: StrictInt = Field(ge=0)
    runtime_version: StrictStr | None = None
    available: StrictBool
    providers: tuple[WindowsMlProviderObservation, ...] = ()
    reason_codes: tuple[StrictStr, ...]

    def select(self, provider_name: str) -> WindowsMlProviderDecision:
        ready = [provider for provider in self.providers if provider.state == "ready" and provider.certified]
        if provider_name != "auto":
            selected = next((provider for provider in ready if provider.provider_name == provider_name), None)
            if selected is None:
                return WindowsMlProviderDecision(
                    available=False,
                    reason_codes=("explicit-provider-unavailable",),
                )
            return _provider_decision(selected, "explicit-provider-ready")
        directml = next((provider for provider in ready if provider.backend == "directml"), None)
        if directml is not None:
            return _provider_decision(directml, "auto-directml-ready")
        cpu = next((provider for provider in ready if provider.backend == "cpu"), None)
        if cpu is not None:
            return _provider_decision(cpu, "auto-cpu-fallback")
        return WindowsMlProviderDecision(available=False, reason_codes=("no-ready-windows-ml-provider",))


def _provider_decision(provider: WindowsMlProviderObservation, reason_code: str) -> WindowsMlProviderDecision:
    return WindowsMlProviderDecision(
        available=True,
        provider_name=provider.provider_name,
        backend=provider.backend,
        provider_version=provider.provider_version,
        evidence_token=provider.evidence_token,
        reason_codes=(reason_code,),
    )


class WindowsMlCatalog:
    MINIMUM_DYNAMIC_PROVIDER_BUILD = 26100

    @classmethod
    def discover(
        cls,
        *,
        os_build: int,
        runtime_version: str | None,
        providers: list[WindowsMlProviderObservation] | tuple[WindowsMlProviderObservation, ...],
    ) -> WindowsMlDiscovery:
        if os_build < cls.MINIMUM_DYNAMIC_PROVIDER_BUILD:
            return WindowsMlDiscovery(
                os_build=os_build,
                runtime_version=runtime_version,
                available=False,
                reason_codes=("windows-build-below-26100",),
            )
        if runtime_version is None:
            return WindowsMlDiscovery(
                os_build=os_build,
                available=False,
                reason_codes=("windows-ml-runtime-unavailable",),
            )
        ordered = tuple(sorted(providers, key=lambda provider: provider.provider_name))
        ready = any(provider.state == "ready" and provider.certified for provider in ordered)
        return WindowsMlDiscovery(
            os_build=os_build,
            runtime_version=runtime_version,
            available=ready,
            providers=ordered,
            reason_codes=("windows-ml-providers-enumerated",) if ready else ("no-ready-windows-ml-provider",),
        )
