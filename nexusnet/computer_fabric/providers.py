from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import EnvironmentClass


@dataclass(frozen=True)
class ProviderRecord:
    provider_id: str
    environment_classes: tuple[EnvironmentClass, ...]
    capabilities: tuple[str, ...]
    default_network: str
    host_access: str

    def to_dict(self, *, selected: bool = False) -> dict[str, Any]:
        can_execute = "execute" in self.capabilities
        return {
            "provider_id": self.provider_id,
            "environment_classes": [item.value for item in self.environment_classes],
            "capabilities": list(self.capabilities),
            "default_network": self.default_network,
            "host_access": self.host_access,
            "selected": selected,
            "capability_probe": {
                "can_execute": can_execute,
                "can_browse": "browser" in self.capabilities,
                "can_persist": EnvironmentClass.PERSISTENT in self.environment_classes,
                "requires_operator_approval": EnvironmentClass.OPERATOR in self.environment_classes,
            },
        }


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers = {
            record.provider_id: record
            for record in (
                ProviderRecord("venv", (EnvironmentClass.EPHEMERAL,), ("execute", "python", "tests"), "task-scoped-egress", "session-only"),
                ProviderRecord("docker", (EnvironmentClass.EPHEMERAL, EnvironmentClass.PERSISTENT), ("execute", "container", "tests"), "deny-by-default", "container"),
                ProviderRecord("podman", (EnvironmentClass.EPHEMERAL, EnvironmentClass.PERSISTENT), ("execute", "container", "rootless"), "deny-by-default", "container"),
                ProviderRecord("wsl", (EnvironmentClass.EPHEMERAL, EnvironmentClass.OPERATOR), ("execute", "linux", "local-cli"), "operator-approved", "operator-granted"),
                ProviderRecord("devcontainer", (EnvironmentClass.EPHEMERAL,), ("execute", "container", "workspace"), "deny-by-default", "workspace"),
                ProviderRecord("remote-vm", (EnvironmentClass.PERSISTENT,), ("execute", "remote", "persistent"), "task-scoped-egress", "remote"),
                ProviderRecord("browser-operator", (EnvironmentClass.OPERATOR,), ("browser", "observe", "approval"), "authenticated-browser-or-local-only", "operator-session"),
                ProviderRecord("local-cli-bridge", (EnvironmentClass.OPERATOR,), ("execute", "local-cli", "approval"), "local-only", "operator-granted"),
            )
        }

    def summary(self, *, requested_provider: str | None, environment_class: EnvironmentClass) -> dict[str, Any]:
        selected_id = self._select(requested_provider=requested_provider, environment_class=environment_class)
        selected = self._providers[selected_id]
        return {
            "selected_provider": selected.to_dict(selected=True),
            "providers": {
                provider_id: record.to_dict(selected=provider_id == selected_id)
                for provider_id, record in sorted(self._providers.items())
            },
        }

    def _select(self, *, requested_provider: str | None, environment_class: EnvironmentClass) -> str:
        if requested_provider in self._providers and environment_class in self._providers[requested_provider].environment_classes:
            return requested_provider
        for provider_id, record in self._providers.items():
            if environment_class in record.environment_classes:
                return provider_id
        return "venv"
