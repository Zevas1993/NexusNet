
from __future__ import annotations
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from core.engines.token_counters import count_text
from services.metrics import begin_stream, tick_stream, end_stream

class TransformersChat:
    def __init__(self, model_id: str, load_8bit: bool = True, device_map: str = "auto"):
        self.model_id = model_id
        self.tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
        kwargs = {"device_map": device_map}
        if load_8bit and torch.cuda.is_available():
            try:
                import bitsandbytes  # noqa: F401
                kwargs["load_in_8bit"] = True
            except Exception:
                pass
        self.m = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
        if torch.cuda.is_available():
            self.m = self.m.to("cuda")

    def chat(self, messages, max_tokens: int = 256, temperature: float = 0.2) -> str:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages) + "\nassistant:"
        inputs = self.tok(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        begin_stream()
        out_ids = self.m.generate(**inputs, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
        text = self.tok.decode(out_ids[0], skip_special_tokens=True)
        reply = text.split("assistant:", 1)[-1].strip() if "assistant:" in text else text.strip()
        tick_stream(count_text(reply))
        end_stream(0)
        return reply
