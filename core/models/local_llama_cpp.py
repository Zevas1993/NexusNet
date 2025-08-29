
from __future__ import annotations
from core.engines.token_counters import count_text
from services.metrics import begin_stream, tick_stream, end_stream

class LlamaCppChat:
    def __init__(self, model_path: str, n_ctx: int = 4096, n_threads: int | None = None):
        try:
            from llama_cpp import Llama  # type: ignore
        except Exception as e:
            raise RuntimeError("llama_cpp is not installed") from e
        self.llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads or 0)

    def chat(self, messages, max_tokens: int = 256, temperature: float = 0.2) -> str:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages) + "\nassistant:"
        begin_stream()
        out = self.llm.create_completion(prompt, max_tokens=max_tokens, temperature=temperature)
        text = (out.get("choices") or [{}])[0].get("text", "")
        tick_stream(count_text(text))
        end_stream(0)
        return text.strip()
