"""Real provider wrapping: the wrapper wraps local + API models (canon C39 dual-runtime/wrapper-first).

The wrapper talks to real external models through one uniform interface. OpenRouter, Requesty, LM Studio,
and vLLM all expose the OpenAI `/chat/completions` API, so a single `OpenAICompatibleProvider` covers
all four (configurable base_url + key + model + local/cloud flag). `EchoProvider` is a deterministic,
offline provider for tests and $0/no-network operation. Every provider is a SOURCE MODEL the continuous-
assimilation loop can learn from.

Honest boundary: real network/key/runtime calls only happen on the operator's machine; offline (here)
the OpenAI-compatible adapter returns a graceful `ok: False` instead of raising, so the wrapper degrades
safely rather than breaking.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Callable, Protocol, runtime_checkable

Message = dict[str, str]


@runtime_checkable
class WrapperProvider(Protocol):
    provider_id: str
    is_local: bool

    def complete(self, messages: list[Message]) -> dict[str, Any]: ...


class EchoProvider:
    """Deterministic offline provider (no network). Useful for $0 startup, tests, and degraded mode."""

    def __init__(self, *, provider_id: str = "echo", is_local: bool = True) -> None:
        self.provider_id = provider_id
        self.is_local = is_local

    def complete(self, messages: list[Message]) -> dict[str, Any]:
        last = messages[-1].get("content", "") if messages else ""
        text = f"[{self.provider_id}] {last.strip()[:400]}"
        return {"ok": True, "text": text, "model": self.provider_id, "local": self.is_local,
                "tokens": len(text.split())}


class OpenAICompatibleProvider:
    """One adapter for any OpenAI-`/chat/completions`-compatible endpoint (OpenRouter/Requesty/LM Studio/
    vLLM). Real httpx call when reachable; graceful `ok: False` when offline (skip-safe)."""

    def __init__(self, *, provider_id: str, base_url: str, model: str, api_key: str = "",
                 is_local: bool = False, timeout: float = 30.0) -> None:
        self.provider_id = provider_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.is_local = is_local
        self.timeout = timeout

    def complete(self, messages: list[Message]) -> dict[str, Any]:
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            resp = httpx.post(f"{self.base_url}/chat/completions",
                              json={"model": self.model, "messages": messages},
                              headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {"ok": True, "text": text, "model": self.model, "local": self.is_local,
                    "tokens": usage.get("completion_tokens")}
        except Exception as exc:                       # offline / no key / endpoint down -> degrade safely
            return {"ok": False, "text": "", "model": self.model, "local": self.is_local,
                    "error": f"{type(exc).__name__}: {exc}"[:160]}


# canon provider factories
def openrouter(model: str, api_key: str = "") -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(provider_id="openrouter", base_url="https://openrouter.ai/api/v1",
                                    model=model, api_key=api_key, is_local=False)


def requesty(model: str, api_key: str = "") -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(provider_id="requesty", base_url="https://router.requesty.ai/v1",
                                    model=model, api_key=api_key, is_local=False)


def lmstudio(model: str = "local-model", base_url: str = "http://localhost:1234/v1") -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(provider_id="lmstudio", base_url=base_url, model=model, is_local=True)


def vllm(model: str, base_url: str = "http://localhost:8000/v1") -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(provider_id="vllm", base_url=base_url, model=model, is_local=True)


class ProviderRegistry:
    """The wrapper's pool of wrapped models. Selecting a provider = choosing a source model to use/learn."""

    def __init__(self) -> None:
        self._providers: dict[str, WrapperProvider] = {}
        self.execution_authority: Any | None = None
        self.execution_observer: Callable[[dict[str, Any]], dict[str, Any]] | None = None
        self._dispatch_count = 0
        self._circuits: dict[str, dict[str, Any]] = {}

    def register(self, provider: WrapperProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> WrapperProvider | None:
        return self._providers.get(provider_id)

    def list(self) -> list[dict[str, Any]]:
        return [{"provider_id": p.provider_id, "local": p.is_local} for p in self._providers.values()]

    def readiness(
        self,
        *,
        default_provider_id: str = "nexusnet-offline",
        active_provider_ids: list[str] | None = None,
        latest_active_provider_id: str | None = None,
    ) -> dict[str, Any]:
        active_ids = {str(provider_id) for provider_id in (active_provider_ids or []) if str(provider_id)}
        providers = [
            _provider_readiness(
                provider,
                selected_by_default=provider.provider_id == default_provider_id,
                active_in_session=provider.provider_id in active_ids,
                latest_active=provider.provider_id == latest_active_provider_id,
            )
            for provider in self._providers.values()
        ]
        for provider in providers:
            provider["circuit"] = self._circuit_projection(
                self._circuit_for(str(provider["provider_id"]))
            )
        status_counts: dict[str, int] = {}
        for provider in providers:
            status = str(provider["status"])
            status_counts[status] = status_counts.get(status, 0) + 1
        usable_provider_count = status_counts.get("usable", 0)
        return {
            "surface_id": "release-wrapper-provider-readiness",
            "authority": "NexusBrain",
            "status_label": "LOCKED CANON",
            "status": "usable" if usable_provider_count else "blocked",
            "default_provider_id": default_provider_id,
            "latest_active_provider_id": latest_active_provider_id,
            "active_provider_ids": sorted(active_ids),
            "provider_count": len(providers),
            "usable_provider_count": usable_provider_count,
            "configured_unverified_count": status_counts.get("configured-unverified", 0),
            "missing_credentials_count": status_counts.get("missing-credentials", 0),
            "blocked_provider_count": sum(
                count for status, count in status_counts.items() if status not in {"usable", "configured-unverified"}
            ),
            "local_provider_count": sum(1 for provider in providers if provider["local"]),
            "cloud_provider_count": sum(1 for provider in providers if not provider["local"]),
            "status_counts": status_counts,
            "providers": providers,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "sanitized-provider-ids-statuses-and-dependency-classes-only-no-api-keys-prompts-outputs-or-raw-endpoints",
        }

    def local_providers(self) -> list[str]:
        return sorted(p.provider_id for p in self._providers.values() if p.is_local)

    def cloud_providers(self) -> list[str]:
        return sorted(p.provider_id for p in self._providers.values() if not p.is_local)

    def inference_scope(self, provider_id: str) -> dict[str, Any]:
        provider = self.get(provider_id)
        if provider is None:
            raise ValueError(f"unknown provider {provider_id}")
        return {
            "provider_id": provider_id,
            "provider_local": bool(provider.is_local),
            "operation": "chat_completion",
        }

    def complete(
        self,
        provider_id: str,
        messages: list[Message],
        *,
        authority_lease_id: str | None = None,
        session_id: str | None = None,
        correlation_ref: str | None = None,
    ) -> dict[str, Any]:
        p = self.get(provider_id)
        if p is None:
            return {"ok": False, "error": f"unknown provider {provider_id}", "text": ""}
        circuit = self._circuit_for(provider_id)
        if circuit["state"] == "open" and time.monotonic() < circuit["open_until"]:
            return {
                "ok": False,
                "error": "provider circuit is open",
                "text": "",
                "model": provider_id,
                "local": bool(p.is_local),
                "provider_id": provider_id,
                "provider_circuit": self._circuit_projection(circuit),
            }
        if circuit["state"] == "open":
            circuit.update({"state": "half-open", "consecutive_failures": 0, "open_until": 0.0})
        authority = self._inference_authority(
            provider_id=provider_id,
            provider=p,
            authority_lease_id=authority_lease_id,
        )
        if not authority["execution_allowed"]:
            authority["shared_event_spine"] = self._observe_inference_outcome(
                event_type="genesis.execution_authority.provider_inference.blocked",
                provider_ref=str(authority["provider_ref"]),
                authority=authority,
                session_id=session_id,
                correlation_ref=correlation_ref,
            )
            return {
                "ok": False,
                "error": "provider inference blocked by execution authority",
                "text": "",
                "model": provider_id,
                "local": bool(p.is_local),
                "provider_id": provider_id,
                "provider_authority": authority,
            }
        out = p.complete(messages)
        error_family = "none"
        retry_count = 0
        if not out.get("ok"):
            error_family = _provider_error_family(str(out.get("error") or ""))
            if error_family == "transient":
                retry_count = 1
                out = p.complete(messages)
        if out.get("ok"):
            self._record_provider_success(circuit)
        else:
            if error_family == "none":
                error_family = _provider_error_family(str(out.get("error") or ""))
            self._record_provider_failure(circuit, error_family)
        authority["shared_event_spine"] = self._observe_inference_outcome(
            event_type=(
                "genesis.execution_authority.provider_inference.executed"
                if out.get("ok")
                else "genesis.execution_authority.provider_inference.failed"
            ),
            provider_ref=str(authority["provider_ref"]),
            authority=authority,
            session_id=session_id,
            correlation_ref=correlation_ref,
        )
        out["provider_id"] = provider_id
        out["provider_authority"] = authority
        out["provider_circuit"] = self._circuit_projection(
            circuit,
            error_family=error_family,
            retry_count=retry_count,
        )
        return out

    def _circuit_for(self, provider_id: str) -> dict[str, Any]:
        return self._circuits.setdefault(
            provider_id,
            {
                "state": "closed",
                "consecutive_failures": 0,
                "open_until": 0.0,
                "last_error_family": "none",
            },
        )

    def _record_provider_success(self, circuit: dict[str, Any]) -> None:
        circuit.update(
            {
                "state": "closed",
                "consecutive_failures": 0,
                "open_until": 0.0,
                "last_error_family": "none",
            }
        )

    def _record_provider_failure(self, circuit: dict[str, Any], error_family: str) -> None:
        circuit["consecutive_failures"] += 1
        circuit["last_error_family"] = error_family
        threshold = 1 if error_family in {"context_length", "non_retryable"} else 2
        if circuit["consecutive_failures"] >= threshold:
            cooldown_seconds = 60.0 if error_family == "quota" else 15.0
            circuit.update({"state": "open", "open_until": time.monotonic() + cooldown_seconds})

    def _circuit_projection(
        self,
        circuit: dict[str, Any],
        *,
        error_family: str | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        return {
            "state": circuit["state"],
            "error_family": error_family or circuit["last_error_family"],
            "retry_count": retry_count,
            "consecutive_failures": circuit["consecutive_failures"],
            "cooldown_active": circuit["state"] == "open",
            "fallback_suggestion": "operator-or-router-select-next-healthy-provider",
            "automatic_provider_substitution": False,
        }

    def _observe_inference_outcome(
        self,
        *,
        event_type: str,
        provider_ref: str,
        authority: dict[str, Any],
        session_id: str | None,
        correlation_ref: str | None,
    ) -> dict[str, Any]:
        self._dispatch_count += 1
        correlation_seed = "|".join(
            [
                str(correlation_ref or "provider-registry"),
                str(authority.get("lease_id") or "none"),
                event_type,
                str(self._dispatch_count),
            ]
        )
        envelope = {
            "event_type": event_type,
            "source_surface_id": "provider-registry-inference",
            "correlation_ref": (
                "provider-inference::"
                f"{hashlib.sha256(correlation_seed.encode('utf-8')).hexdigest()[:24]}"
            ),
            "session_ref_digest": _privacy_digest(session_id) if session_id else None,
            "artifact_refs": [
                provider_ref,
                f"execution-authority-lease::{authority.get('lease_id') or 'none'}",
                "capability::model-inference",
            ],
            "planes": ["authority", "isolation", "model", "event", "evidence"],
        }
        if self.execution_observer is None:
            return {
                "status": "not-configured-event-spine",
                "event_type": event_type,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        try:
            projection = self.execution_observer(envelope)
        except Exception as exc:  # pragma: no cover - dispatch must survive telemetry failure
            return {
                "status": "degraded-event-spine",
                "event_type": event_type,
                "blocker_digest": (
                    "sha256:"
                    f"{hashlib.sha256(type(exc).__name__.encode('utf-8')).hexdigest()[:16]}"
                ),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        return {
            key: projection.get(key)
            for key in (
                "event_ref",
                "blackboard_snapshot_ref",
                "plane_trace_ref",
                "event_type",
                "source_surface_id",
                "raw_content_included",
                "active_production_mutation_allowed",
                "active_production_mutated",
            )
        }

    def _inference_authority(
        self,
        *,
        provider_id: str,
        provider: WrapperProvider,
        authority_lease_id: str | None,
    ) -> dict[str, Any]:
        provider_ref = f"provider::{hashlib.sha256(provider_id.encode('utf-8')).hexdigest()}"
        base = {
            "surface_id": "provider-registry-inference-authority",
            "capability": "model_inference",
            "provider_ref": provider_ref,
            "required": not isinstance(provider, EchoProvider),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        if isinstance(provider, EchoProvider):
            return {
                **base,
                "status": "native-contained",
                "execution_allowed": True,
                "reason": "native-no-network-provider",
            }
        if self.execution_authority is None:
            return {
                **base,
                "status": "blocked-authority",
                "execution_allowed": False,
                "reason": "execution_authority_not_bound",
            }
        lease_id = str(authority_lease_id or "")
        if not lease_id:
            return {
                **base,
                "status": "blocked-authority",
                "execution_allowed": False,
                "reason": "execution_authority_lease_required",
            }
        try:
            result = self.execution_authority.evaluate(
                lease_id=lease_id,
                capability="model_inference",
                scope=self.inference_scope(provider_id),
            )
        except KeyError:
            return {
                **base,
                "lease_id": lease_id,
                "status": "blocked-authority",
                "execution_allowed": False,
                "reason": "execution_authority_lease_not_found",
            }
        decision = result.get("decision") if isinstance(result.get("decision"), dict) else {}
        return {
            **base,
            "lease_id": decision.get("lease_id"),
            "status": "allowed" if decision.get("execution_allowed") else "blocked-authority",
            "execution_allowed": bool(decision.get("execution_allowed")),
            "reason": str(decision.get("reason") or "authority-decision-missing"),
            "scope_hash": decision.get("scope_hash"),
        }


def default_provider_registry(*, openrouter_key: str = "", requesty_key: str = "") -> ProviderRegistry:
    """The wrapper's default pool: an offline EchoProvider (always works) + the four canon providers
    (OpenRouter/Requesty cloud, LM Studio/vLLM local). Cloud providers activate when a key is supplied;
    local providers activate when their endpoint is reachable on the operator's machine."""
    reg = ProviderRegistry()
    reg.register(EchoProvider(provider_id="nexusnet-offline", is_local=True))
    reg.register(openrouter("openrouter/auto", api_key=openrouter_key))
    reg.register(requesty("requesty/auto", api_key=requesty_key))
    reg.register(lmstudio())
    reg.register(vllm("local-gpu-model"))
    return reg


def _provider_error_family(error: str) -> str:
    normalized = error.lower()
    if any(marker in normalized for marker in ("429", "quota", "rate limit", "rate_limit")):
        return "quota"
    if any(marker in normalized for marker in ("context length", "context_length", "too many tokens", "maximum context")):
        return "context_length"
    if any(marker in normalized for marker in ("timeout", "timed out", "connection", "temporarily", "503", "502")):
        return "transient"
    return "non_retryable"


def _provider_readiness(
    provider: WrapperProvider,
    *,
    selected_by_default: bool,
    active_in_session: bool,
    latest_active: bool,
) -> dict[str, Any]:
    is_openai_compatible = isinstance(provider, OpenAICompatibleProvider)
    is_echo = isinstance(provider, EchoProvider)
    configured = True
    status = "usable" if is_echo else "configured-unverified"
    reason = "bundled-offline-provider" if is_echo else "external-endpoint-not-probed"
    provider_kind = "offline-echo" if is_echo else ("local-openai-compatible" if provider.is_local else "api-openai-compatible")
    if is_openai_compatible and not provider.is_local and not provider.api_key:
        configured = False
        status = "missing-credentials"
        reason = "api-key-not-configured"
    return {
        "provider_id": provider.provider_id,
        "local": bool(provider.is_local),
        "provider_kind": provider_kind,
        "status": status,
        "reason": reason,
        "configured": configured,
        "external_dependency": not is_echo,
        "selected_by_default": selected_by_default,
        "active_in_session": active_in_session,
        "latest_active": latest_active,
        "credential_material_included": False,
        "raw_endpoint_included": False,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]
