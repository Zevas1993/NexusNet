
from __future__ import annotations
try:
    from llama_cpp import Llama
except Exception:
    Llama = None

class LlamaCppEngine:
    def __init__(self, gguf_path: str, n_ctx: int = 4096):
        if Llama is None: raise RuntimeError("llama-cpp-python not installed")
        self.llm = Llama(model_path=gguf_path, n_ctx=n_ctx)
    def generate(self, prompt: str, **kw) -> str:
        out = self.llm(prompt, max_tokens=kw.get("max_new_tokens",256), temperature=kw.get("temperature",0.7))
        return out.get("choices",[{}])[0].get("text","")
