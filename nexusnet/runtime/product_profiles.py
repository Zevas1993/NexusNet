from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RuntimeStatus = Literal["locked", "candidate", "disabled", "research_only"]


class ProductRuntimeProfile(BaseModel):
    profile_id: str
    mode: Literal["local", "gpu", "cloud", "constrained-device"]
    adapter: str
    status: RuntimeStatus
    runnable: bool = False
    fallback_profile: str = "mock"
    context_budget_tokens: int = 8192
    context_strategy: str = "effective_context"
    unsupported_reason: str | None = None
    candidate_adapters: list[str] = Field(default_factory=list)


class ProductRuntimeProfileRegistry:
    """Runtime profile contract for the full product sweep."""

    def __init__(self):
        self._profiles = {
            "local": ProductRuntimeProfile(
                profile_id="runtime-local",
                mode="local",
                adapter="mock",
                status="locked",
                runnable=True,
                fallback_profile="mock",
                context_budget_tokens=8192,
                candidate_adapters=["llama.cpp", "transformers", "lmstudio"],
            ),
            "gpu": ProductRuntimeProfile(
                profile_id="runtime-gpu",
                mode="gpu",
                adapter="vllm",
                status="candidate",
                runnable=False,
                fallback_profile="local",
                context_budget_tokens=131072,
                unsupported_reason="GPU serving adapter remains candidate until health/eval proof exists.",
                candidate_adapters=["vllm", "sglang", "lmcache", "torchao"],
            ),
            "cloud": ProductRuntimeProfile(
                profile_id="runtime-cloud",
                mode="cloud",
                adapter="openai-compatible",
                status="candidate",
                runnable=False,
                fallback_profile="local",
                context_budget_tokens=128000,
                unsupported_reason="Cloud profile requires explicit endpoint, identity, cost, and eval gates.",
                candidate_adapters=["openai-compatible", "vllm", "sglang"],
            ),
            "constrained-device": ProductRuntimeProfile(
                profile_id="runtime-constrained-device",
                mode="constrained-device",
                adapter="llama.cpp",
                status="candidate",
                runnable=False,
                fallback_profile="local",
                context_budget_tokens=4096,
                unsupported_reason="Constrained-device mode requires validated model pack and runtime health.",
                candidate_adapters=["llama.cpp", "torchao"],
            ),
        }

    def list_profiles(self) -> list[ProductRuntimeProfile]:
        return list(self._profiles.values())

    def select_profile(self, mode: str, *, requested_adapter: str | None = None) -> ProductRuntimeProfile:
        profile = self._profiles.get(mode, self._profiles["local"]).model_copy(deep=True)
        if requested_adapter:
            profile.adapter = requested_adapter
            if requested_adapter not in profile.candidate_adapters:
                profile.runnable = False
                profile.status = "disabled"
                profile.fallback_profile = "local"
                profile.unsupported_reason = f"{requested_adapter} is not part of the {profile.mode} candidate adapter set."
            elif profile.status != "locked":
                profile.runnable = False
        return profile

    def summary(self) -> dict:
        return {
            "status": "effective_context_profiles",
            "raw_million_token_context": "unresolved",
            "profiles": [profile.model_dump(mode="json") for profile in self.list_profiles()],
        }
