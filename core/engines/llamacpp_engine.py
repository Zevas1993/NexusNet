
from __future__ import annotations
try:
    from llama_cpp import Llama
except Exception:
    Llama = None

class LlamaCppEngine:
    def __init__(
        self,
        gguf_path: str,
        n_ctx: int = 4096,
        n_gpu_layers: int = 0,
        n_batch: int = 256,
    ):
        if Llama is None: raise RuntimeError("llama-cpp-python not installed")
        self.llm = Llama(
            model_path=gguf_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            use_mmap=True,
        )
    def generate(self, prompt: str, **kw) -> str:
        out = self.llm(prompt, max_tokens=kw.get("max_new_tokens",256), temperature=kw.get("temperature",0.7))
        return out.get("choices",[{}])[0].get("text","")
