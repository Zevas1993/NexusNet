
from __future__ import annotations
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_CACHE = {}

class TransformersEngine:
    def __init__(self, model_id: str, device: str = "cpu", dtype: Optional[torch.dtype] = None):
        self._default_id = model_id

        if model_id in MODEL_CACHE:
            self.tok, self.model = MODEL_CACHE[model_id]
        else:
            self.tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype or (torch.float16 if device == "cuda" else torch.float32),
            device_map="auto" if device == "cuda" else None
        )
        self.device = device
        if device == "cuda":
            self.model = self.model.to("cuda")
        MODEL_CACHE[model_id] = (self.tok, self.model)

    def generate(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.95, override_model_id: str | None = None) -> str:
        if override_model_id and override_model_id != self._default_id:
            # lazy swap to cache (or load if missing)
            from transformers import AutoTokenizer, AutoModelForCausalLM
            if override_model_id in MODEL_CACHE:
                self.tok, self.model = MODEL_CACHE[override_model_id]
            else:
                tok = AutoTokenizer.from_pretrained(override_model_id, trust_remote_code=True)
                mdl = AutoModelForCausalLM.from_pretrained(override_model_id, torch_dtype=(torch.float16 if self.device=="cuda" else torch.float32))
                if self.device=="cuda": mdl = mdl.to("cuda")
                MODEL_CACHE[override_model_id] = (tok, mdl)
                self.tok, self.model = tok, mdl
        inputs = self.tok(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k:v.to("cuda") for k,v in inputs.items()}
        out = self.model.generate(**inputs, do_sample=True, temperature=temperature, top_p=top_p,
                                  max_new_tokens=max_new_tokens, pad_token_id=self.tok.eos_token_id)
        text = self.tok.decode(out[0], skip_special_tokens=True)
        if text.startswith(prompt): text = text[len(prompt):]
        return text.strip()
