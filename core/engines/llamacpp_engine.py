
from __future__ import annotations

try:
    import llama_cpp
    from llama_cpp import Llama
except Exception:
    llama_cpp = None
    Llama = None


class LlamaCppEngine:
    def __init__(
        self,
        gguf_path: str,
        n_ctx: int = 4096,
        n_gpu_layers: int = 0,
        n_batch: int = 256,
        n_threads: int | None = None,
        n_threads_batch: int | None = None,
        cache_type_k: str | int | None = None,
        cache_type_v: str | int | None = None,
        flash_attn: bool = False,
        offload_kqv: bool = True,
        main_gpu: int = 0,
        split_mode: str | int = "layer",
        tensor_split: str | list[float] | None = None,
    ):
        if Llama is None:
            raise RuntimeError("llama-cpp-python not installed")
        if n_threads is not None and n_threads <= 0:
            raise ValueError("n_threads must be positive")
        if n_threads_batch is not None and n_threads_batch <= 0:
            raise ValueError("n_threads_batch must be positive")
        if main_gpu < 0:
            raise ValueError("main_gpu must be non-negative")
        kwargs = {
            "model_path": gguf_path,
            "n_ctx": n_ctx,
            "n_gpu_layers": n_gpu_layers,
            "n_batch": n_batch,
            "n_threads": n_threads,
            "n_threads_batch": n_threads_batch,
            "type_k": self._cache_type(cache_type_k),
            "type_v": self._cache_type(cache_type_v),
            "flash_attn": flash_attn,
            "offload_kqv": offload_kqv,
            "main_gpu": main_gpu,
            "split_mode": self._split_mode(split_mode),
            "tensor_split": self._tensor_split(tensor_split),
            "use_mmap": True,
        }
        self.llm = Llama(**{key: value for key, value in kwargs.items() if value is not None})

    @staticmethod
    def _cache_type(value: str | int | None) -> int | None:
        if value is None or isinstance(value, int):
            return value
        if llama_cpp is None:
            raise RuntimeError("llama-cpp-python not installed")
        constant = f"GGML_TYPE_{value.strip().upper()}"
        resolved = getattr(llama_cpp, constant, None)
        if resolved is None:
            raise ValueError(f"unsupported llama.cpp KV cache type: {value}")
        return int(resolved)

    @staticmethod
    def _split_mode(value: str | int) -> int:
        if isinstance(value, int):
            return value
        if llama_cpp is None:
            raise RuntimeError("llama-cpp-python not installed")
        constant = f"LLAMA_SPLIT_MODE_{value.strip().upper()}"
        resolved = getattr(llama_cpp, constant, None)
        if resolved is None:
            raise ValueError(f"unsupported llama.cpp split mode: {value}")
        return int(resolved)

    @staticmethod
    def _tensor_split(value: str | list[float] | None) -> list[float] | None:
        if value is None:
            return None
        values = (
            [float(item.strip()) for item in value.split(",")]
            if isinstance(value, str)
            else list(value)
        )
        if not values or any(item < 0 for item in values) or sum(values) <= 0:
            raise ValueError("tensor_split must contain non-negative values with a positive sum")
        return values

    def generate(self, prompt: str, **kw) -> str:
        out = self.llm(
            prompt,
            max_tokens=kw.get("max_new_tokens", 256),
            temperature=kw.get("temperature", 0.7),
        )
        return out.get("choices", [{}])[0].get("text", "")
