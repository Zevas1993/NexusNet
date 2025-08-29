
from typing import List, Dict, Any, Optional
from .config import settings
from .hardware import local_first_policy

class BackendBase:
    name = "base"
    def generate(self, messages: List[Dict[str,str]], expert_hint: Optional[str]=None) -> str:
        raise NotImplementedError

class TransformersBackend(BackendBase):
    name = "transformers"
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._ready = False
        try:
            # Lazy import to keep startup light
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = settings.inference.get("transformers", {}).get("model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self._ready = True
        except Exception:
            self._ready = False

    def generate(self, messages: List[Dict[str,str]], expert_hint: Optional[str]=None) -> str:
        if not self._ready:
            return "[transformers backend not available; falling back to template reply.]"
        prompt = ""
        for m in messages:
            role = m.get("role","user")
            content = m.get("content","")
            if role == "user":
                prompt += f"User: {content}\n"
            else:
                prompt += f"{role.capitalize()}: {content}\n"
        prompt += "Assistant:"
        import torch
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=128)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).split("Assistant:",1)[-1].strip()

class LlamaCppBackend(BackendBase):
    name = "llama.cpp"
    def __init__(self):
        try:
            from llama_cpp import Llama
            model_path = settings.inference.get("llama_cpp", {}).get("model_path", "models/tiny/tinyllama.gguf")
            self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)
            self._ready = True
        except Exception:
            self._ready = False
            self.llm = None

    def generate(self, messages: List[Dict[str,str]], expert_hint: Optional[str]=None) -> str:
        if not self._ready:
            return "[llama.cpp backend not available; falling back to template reply.]"
        prompt = ""
        for m in messages:
            role = m.get("role","user")
            content = m.get("content","")
            prompt += f"{role.upper()}: {content}\n"
        prompt += "ASSISTANT:"
        out = self.llm(prompt, max_tokens=128)
        return out["choices"][0]["text"].strip()

class VLLMHTTPBackend(BackendBase):
    name = "vLLM"
    def __init__(self):
        self.endpoint = settings.inference.get("vllm", {}).get("endpoint")
        self._ready = bool(self.endpoint)

    def generate(self, messages: List[Dict[str,str]], expert_hint: Optional[str]=None) -> str:
        if not self._ready:
            return "[vLLM endpoint not configured; falling back to template reply.]"
        import requests
        payload = {
            "model": "any",
            "messages": messages,
            "max_tokens": 128,
            "temperature": 0.7
        }
        r = requests.post(f"{self.endpoint}/v1/chat/completions", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

class TemplateBackend(BackendBase):
    name = "template"
    def generate(self, messages: List[Dict[str,str]], expert_hint: Optional[str]=None) -> str:
        last = messages[-1]["content"] if messages else ""
        hint = f" (expert: {expert_hint})" if expert_hint else ""
        return f"I hear you said: '{last}'. Here's a concise answer{hint}: [offline default response]."

class InferenceSelector:
    def __init__(self):
        self.backends = {
            "transformers": TransformersBackend(),
            "llama.cpp": LlamaCppBackend(),
            "vLLM": VLLMHTTPBackend(),
            "template": TemplateBackend(),
        }

    def select_backend(self, model_hint: Optional[str]=None):
        policy = local_first_policy()
        prefer_local = policy["policy"]["prefer_local"]

        if model_hint and model_hint in self.backends and getattr(self.backends[model_hint], "_ready", True):
            return self.backends[model_hint]

        # Try local backends in order
        for name in ["llama.cpp", "transformers"]:
            b = self.backends.get(name)
            if b and getattr(b, "_ready", False):
                return b

        # Try vLLM if configured
        b = self.backends.get("vLLM")
        if b and getattr(b, "_ready", False):
            return b

        # Fallback
        return self.backends["template"]
