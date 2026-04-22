from __future__ import annotations

from typing import Any

from ..schemas import TeacherCapabilityCard


TOOL_TEACHERS = {
    "codestral",
    "deepseek-coder",
    "qwen3-coder-next",
    "devstral-2",
    "devstral-small-1-1",
    "toolbench-trained-llama",
    "gorilla-api-agent",
    "mistral-toolformer",
    "lfm2",
}

STRUCTURED_OUTPUT_TEACHERS = TOOL_TEACHERS | {
    "qwen3-30b-a3b",
    "mistral-small-4",
    "deepseek-r1-distill-qwen-32b",
    "deepseek-v2-lite",
    "kimi-k2-5",
    "deepseek-r1",
    "deepseek-v3",
}

EDGE_TEACHERS = {
    "qwen-0.5b-moe",
    "qwen-moe-0.5b",
    "intent-bert",
    "distilbert-intent",
    "polycoder",
    "deepseek-r1-distill-qwen-1.5b",
    "deepseek-r1-distill-qwen-7b",
    "lfm2",
}

DEEP_TEACHERS = {
    "qwen3-30b-a3b",
    "deepseek-r1",
    "deepseek-v3",
    "deepseek-r1-distill-qwen-32b",
    "mixtral-8x7b",
    "claude-eval-finetunes",
    "claude-eval-historical",
    "kimi-k2-5",
}

HIGH_RISK_TEACHERS = {
    "claude-eval-finetunes",
    "claude-eval-historical",
    "cyberseceval-llms",
    "gpt-j-security-finetunes",
    "code-llama-secure",
}

LONG_CONTEXT_TEACHERS = {
    "deepseek-v2-lite",
    "qwen3-30b-a3b",
    "qwen3-vl",
    "kimi-k2-5",
    "mpt-storywriter",
    "longlora-llama-3-8b",
    "recurrentgemma-memory-tuned",
}


def build_teacher_capability_card(*, teacher_id: str, payload: dict[str, Any], role_tags: list[str]) -> TeacherCapabilityCard:
    modalities = list(payload.get("modalities") or _infer_modalities(teacher_id))
    supports_tools = bool(payload.get("supports_tools", teacher_id in TOOL_TEACHERS))
    supports_structured_output = bool(
        payload.get("supports_structured_output", teacher_id in STRUCTURED_OUTPUT_TEACHERS or supports_tools)
    )
    best_for = list(payload.get("specialties") or _infer_best_for(teacher_id, role_tags))
    budget_class = str(payload.get("budget_class") or _infer_budget_class(teacher_id)).lower()
    risk_tier = str(payload.get("risk_tier") or _infer_risk_tier(teacher_id, role_tags)).lower()
    context_window = int(payload.get("context_window") or _infer_context_window(teacher_id))
    locality = str(payload.get("locality") or _infer_locality(payload)).lower()
    reasoning_modes = list(payload.get("reasoning_modes", []))
    hardware_targets = list(payload.get("hardware_targets") or _infer_hardware_targets(teacher_id, locality))
    bounded_lanes = list(payload.get("bounded_lanes") or (["router_fastpath", "toolsmith", "memory_budgeting"] if teacher_id == "lfm2" else []))
    return TeacherCapabilityCard(
        teacher_id=teacher_id,
        modalities=modalities,
        supports_tools=supports_tools,
        supports_structured_output=supports_structured_output,
        best_for=best_for,
        budget_class=budget_class,
        risk_tier=risk_tier,
        context_window=context_window,
        locality=locality,
        reasoning_modes=reasoning_modes,
        hardware_targets=hardware_targets,
        bounded_lanes=bounded_lanes,
    )


def _infer_modalities(teacher_id: str) -> list[str]:
    if teacher_id in {"openclip", "blip-2", "sam", "eva-clip", "qwen3-vl"}:
        return ["image", "text"]
    if teacher_id in {"whisper-large-v3", "wav2vec-2-0", "audiolm", "bark-tts", "voxtral-small"}:
        return ["audio", "text"]
    return ["text"]


def _infer_best_for(teacher_id: str, role_tags: list[str]) -> list[str]:
    inferred = [tag for tag in role_tags if tag not in {"core-brain", "multi-role"}]
    if teacher_id == "lfm2":
        inferred.extend(["efficiency", "bounded-tool-discipline"])
    return inferred or ["general"]


def _infer_budget_class(teacher_id: str) -> str:
    if teacher_id in EDGE_TEACHERS:
        return "edge_constrained"
    if teacher_id in LONG_CONTEXT_TEACHERS:
        return "long_context"
    if teacher_id in DEEP_TEACHERS:
        return "deep"
    return "standard"


def _infer_risk_tier(teacher_id: str, role_tags: list[str]) -> str:
    if teacher_id in HIGH_RISK_TEACHERS or "security" in role_tags or "critique" in role_tags:
        return "high"
    if "researcher" in role_tags or "meta-reasoner" in role_tags:
        return "medium"
    return "low" if teacher_id in EDGE_TEACHERS else "medium"


def _infer_context_window(teacher_id: str) -> int:
    if teacher_id in LONG_CONTEXT_TEACHERS:
        return 131072
    if teacher_id in DEEP_TEACHERS:
        return 65536
    if teacher_id in EDGE_TEACHERS:
        return 8192
    return 32768


def _infer_locality(payload: dict[str, Any]) -> str:
    hints = " ".join(payload.get("model_hints", []))
    if "openai/" in hints and "ollama/" not in hints:
        return "remote_only"
    if "ollama/" in hints:
        return "local_first"
    return "mixed_local_then_remote"


def _infer_hardware_targets(teacher_id: str, locality: str) -> list[str]:
    if teacher_id in EDGE_TEACHERS:
        return ["cpu-safe", "edge-safe", "low-vram"]
    if locality == "remote_only":
        return ["remote-service"]
    return ["local-gpu", "fallback-safe"]
