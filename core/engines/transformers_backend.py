
from __future__ import annotations
import os
from .base import BaseEngine

class TransformersEngine(BaseEngine):
    name = "transformers"

    def __init__(self):
        self.model_id = os.environ.get("HF_MODEL_ID")  # optional
        self.device = os.environ.get("HF_DEVICE", "cpu")
        self._pipe = None

    def _lazy_init(self):
        if self._pipe is not None or not self.model_id:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            tok = AutoTokenizer.from_pretrained(self.model_id)
            mdl = AutoModelForCausalLM.from_pretrained(self.model_id, device_map="auto" if self.device!="cpu" else None)
            self._pipe = pipeline("text-generation", model=mdl, tokenizer=tok, device=0 if self.device!="cpu" else -1)
        except Exception:
            self._pipe = None  # keep safe

    def generate(self, prompt: str, **kw) -> str:
        self._lazy_init()
        if self._pipe is None:
            return f"[transformers:dry] {prompt}"
        out = self._pipe(prompt, max_new_tokens=int(os.environ.get("HF_MAX_NEW_TOKENS", "64")))
        return out[0]["generated_text"]
