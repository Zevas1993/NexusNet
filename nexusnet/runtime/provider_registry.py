from __future__ import annotations

from typing import Any


def provider_catalog() -> list[dict[str, Any]]:
    return [
        {
            "provider_id": "ollama",
            "label": "Ollama",
            "location": "local",
            "auth_type": "local",
            "base_url": "http://localhost:11434",
            "capabilities": ["chat", "coding", "tools"],
            "default_models": [
                {
                    "model_id": "local/small-instruct",
                    "quality_score": 1.8,
                    "reasoning_capable": False,
                    "tool_capable": True,
                    "cost_per_1m_input": 0.0,
                    "cost_per_1m_output": 0.0,
                    "tier_fit": ["simple", "standard"],
                },
                {
                    "model_id": "local/coder-instruct",
                    "quality_score": 2.6,
                    "reasoning_capable": False,
                    "tool_capable": True,
                    "cost_per_1m_input": 0.0,
                    "cost_per_1m_output": 0.0,
                    "tier_fit": ["standard", "complex"],
                },
            ],
        },
        {
            "provider_id": "lmstudio",
            "label": "LM Studio",
            "location": "local",
            "auth_type": "local",
            "base_url": "http://localhost:1234/v1",
            "capabilities": ["chat", "coding", "data_analysis", "tools"],
            "default_models": [
                {
                    "model_id": "local/lmstudio-balanced",
                    "quality_score": 2.7,
                    "reasoning_capable": False,
                    "tool_capable": True,
                    "cost_per_1m_input": 0.0,
                    "cost_per_1m_output": 0.0,
                    "tier_fit": ["standard", "complex"],
                }
            ],
        },
        {
            "provider_id": "llamacpp",
            "label": "llama.cpp",
            "location": "local",
            "auth_type": "local",
            "base_url": "http://localhost:8080/v1",
            "capabilities": ["chat"],
            "default_models": [
                {
                    "model_id": "local/llamacpp-chat",
                    "quality_score": 1.6,
                    "reasoning_capable": False,
                    "tool_capable": False,
                    "cost_per_1m_input": 0.0,
                    "cost_per_1m_output": 0.0,
                    "tier_fit": ["simple", "standard"],
                }
            ],
        },
        {
            "provider_id": "openai",
            "label": "OpenAI-Compatible",
            "location": "cloud",
            "auth_type": "api_key",
            "base_url": "https://api.openai.com/v1",
            "capabilities": ["chat", "coding", "data_analysis", "tools", "reasoning"],
            "default_models": [
                {
                    "model_id": "cloud/standard-tool-model",
                    "quality_score": 3.4,
                    "reasoning_capable": False,
                    "tool_capable": True,
                    "cost_per_1m_input": 0.4,
                    "cost_per_1m_output": 1.6,
                    "tier_fit": ["standard", "complex"],
                },
                {
                    "model_id": "cloud/reasoning-model",
                    "quality_score": 4.3,
                    "reasoning_capable": True,
                    "tool_capable": True,
                    "cost_per_1m_input": 4.0,
                    "cost_per_1m_output": 16.0,
                    "tier_fit": ["complex", "reasoning"],
                },
            ],
        },
        {
            "provider_id": "anthropic-compatible",
            "label": "Anthropic-Compatible",
            "location": "cloud",
            "auth_type": "api_key",
            "base_url": "https://api.anthropic.com",
            "capabilities": ["chat", "coding", "tools", "reasoning"],
            "default_models": [
                {
                    "model_id": "cloud/creative-reasoning-model",
                    "quality_score": 4.2,
                    "reasoning_capable": True,
                    "tool_capable": True,
                    "cost_per_1m_input": 3.0,
                    "cost_per_1m_output": 15.0,
                    "tier_fit": ["complex", "reasoning"],
                }
            ],
        },
        {
            "provider_id": "manifest",
            "label": "Manifest Optional Adapter",
            "location": "local-proxy",
            "auth_type": "self_hosted_proxy",
            "base_url": "http://localhost:2099/v1",
            "capabilities": ["chat", "coding", "data_analysis", "tools", "reasoning", "provider_mix"],
            "default_models": [
                {
                    "model_id": "manifest/auto",
                    "quality_score": 3.0,
                    "reasoning_capable": True,
                    "tool_capable": True,
                    "cost_per_1m_input": 0.0,
                    "cost_per_1m_output": 0.0,
                    "tier_fit": ["simple", "standard", "complex", "reasoning"],
                }
            ],
        },
    ]


def candidate_routes(*, allow_cloud: bool, allow_external_proxy: bool = False) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for provider in provider_catalog():
        if provider["location"] == "cloud" and not allow_cloud:
            continue
        if provider["location"] == "local-proxy" and not allow_external_proxy:
            continue
        for model in provider["default_models"]:
            routes.append(
                {
                    "provider_id": provider["provider_id"],
                    "provider_label": provider["label"],
                    "location": provider["location"],
                    "auth_type": provider["auth_type"],
                    "base_url": provider["base_url"],
                    "capabilities": provider["capabilities"],
                    **model,
                }
            )
    return routes


def provider_from_route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": route["provider_id"],
        "label": route["provider_label"],
        "location": route["location"],
        "auth_type": route["auth_type"],
        "base_url": route["base_url"],
    }


def model_from_route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_id": route["model_id"],
        "quality_score": route["quality_score"],
        "reasoning_capable": route["reasoning_capable"],
        "tool_capable": route["tool_capable"],
        "tier_fit": route["tier_fit"],
    }
