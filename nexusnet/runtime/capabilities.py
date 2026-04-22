from __future__ import annotations

from ..schemas import BackendCapabilityCard


def vllm_capability_card() -> BackendCapabilityCard:
    return BackendCapabilityCard(
        runtime_name="vllm",
        backend_type="openai-http",
        status_label="STRONG ACCEPTED DIRECTION",
        local_first=False,
        supports_structured_output=True,
        supports_streaming=True,
        supports_gguf=False,
        supports_edge_portability=False,
        supports_tools=True,
        notes=["High-throughput serving lane under the NexusNet brain."],
    )


def llama_cpp_capability_card() -> BackendCapabilityCard:
    return BackendCapabilityCard(
        runtime_name="llama.cpp",
        backend_type="local-python",
        status_label="STRONG ACCEPTED DIRECTION",
        local_first=True,
        supports_structured_output=False,
        supports_streaming=False,
        supports_gguf=True,
        supports_edge_portability=True,
        supports_tools=False,
        notes=["Local-first, CPU-safe, GGUF-safe safe-mode backend."],
    )


def onnx_genai_capability_card() -> BackendCapabilityCard:
    return BackendCapabilityCard(
        runtime_name="onnx-genai",
        backend_type="portable-runtime",
        status_label="STRONG ACCEPTED DIRECTION",
        local_first=True,
        supports_structured_output=True,
        supports_streaming=False,
        supports_gguf=False,
        supports_edge_portability=True,
        supports_tools=False,
        notes=["Portable ONNX Runtime GenAI lane for edge and offline deployment."],
    )
