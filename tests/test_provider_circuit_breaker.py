from __future__ import annotations

from nexusnet.providers.model_providers import EchoProvider, ProviderRegistry


class _TransientThenHealthyProvider(EchoProvider):
    provider_id = "transient-then-healthy"

    def __init__(self) -> None:
        super().__init__(provider_id=self.provider_id)
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> dict[str, object]:
        self.calls += 1
        if self.calls == 1:
            return {"ok": False, "text": "", "error": "connection timed out", "model": self.provider_id, "local": True}
        return {"ok": True, "text": "recovered", "model": self.provider_id, "local": True}


class _QuotaFailingProvider(EchoProvider):
    provider_id = "quota-failing"

    def __init__(self) -> None:
        super().__init__(provider_id=self.provider_id)
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> dict[str, object]:
        self.calls += 1
        return {"ok": False, "text": "", "error": "HTTP 429 quota exceeded", "model": self.provider_id, "local": True}


def test_provider_registry_retries_a_transient_failure_and_records_the_recovery():
    provider = _TransientThenHealthyProvider()
    registry = ProviderRegistry()
    registry.register(provider)

    result = registry.complete(provider.provider_id, [{"role": "user", "content": "recover"}])

    assert result["ok"] is True
    assert provider.calls == 2
    assert result["provider_circuit"]["error_family"] == "transient"
    assert result["provider_circuit"]["retry_count"] == 1
    assert result["provider_circuit"]["state"] == "closed"


def test_provider_registry_opens_a_quota_circuit_without_silent_provider_substitution():
    provider = _QuotaFailingProvider()
    registry = ProviderRegistry()
    registry.register(provider)

    first = registry.complete(provider.provider_id, [{"role": "user", "content": "quota"}])
    second = registry.complete(provider.provider_id, [{"role": "user", "content": "quota"}])
    blocked = registry.complete(provider.provider_id, [{"role": "user", "content": "quota"}])

    assert first["provider_circuit"]["error_family"] == "quota"
    assert second["provider_circuit"]["state"] == "open"
    assert blocked["ok"] is False
    assert blocked["provider_circuit"]["state"] == "open"
    assert blocked["provider_circuit"]["fallback_suggestion"] == "operator-or-router-select-next-healthy-provider"
    assert provider.calls == 2
    readiness = registry.readiness(default_provider_id=provider.provider_id)
    assert readiness["providers"][0]["circuit"]["state"] == "open"
