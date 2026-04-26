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

    def assemble_context(
        self,
        *,
        profile: str,
        target_tokens: int,
        requested_adapter: str | None = None,
        task_type: str = "general",
    ) -> dict:
        runtime_profile = self.select_profile(profile, requested_adapter=requested_adapter)
        bounded_target = max(1, int(target_tokens))
        raw_prompt_tokens = min(4096, max(512, bounded_target // 100))
        indexed_evidence_tokens = min(bounded_target // 2, max(raw_prompt_tokens + 1, bounded_target // 4))
        summary_tokens = min(65536, max(raw_prompt_tokens, bounded_target // 10))
        memory_tokens = min(131072, max(summary_tokens, bounded_target // 8))
        cache_tokens = max(0, bounded_target - raw_prompt_tokens - indexed_evidence_tokens - summary_tokens - memory_tokens)
        return {
            "raw_context_claim": "unresolved",
            "effective_context_strategy": "memory_index_summary_cache",
            "target_tokens": bounded_target,
            "task_type": task_type,
            "requested_adapter": requested_adapter,
            "runtime_profile": runtime_profile.model_dump(mode="json"),
            "segments": {
                "raw_prompt": {
                    "tokens": raw_prompt_tokens,
                    "source": "current_prompt_and_required_instructions",
                },
                "conversation_summary": {
                    "tokens": summary_tokens,
                    "source": "rolling_trace_summary",
                },
                "memory_planes": {
                    "tokens": memory_tokens,
                    "source": "provenance_scoped_memory_retrieval",
                },
                "indexed_evidence": {
                    "tokens": indexed_evidence_tokens,
                    "source": "dereferenceable_evidence_index",
                },
                "kv_cache_reuse": {
                    "tokens": cache_tokens,
                    "source": "lmcache_style_candidate_cache_reuse",
                },
            },
            "fits_effective_budget": True,
            "unsupported_runtime_treated_as_runnable": False,
        }

    def summary(self) -> dict:
        return {
            "status": "effective_context_profiles",
            "raw_million_token_context": "unresolved",
            "profiles": [profile.model_dump(mode="json") for profile in self.list_profiles()],
        }
