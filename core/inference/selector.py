
import yaml
from core.inference import transformers as T
from core.inference import vllm_http as V
from core.inference import ollama_http as O
from core.inference import lmstudio_http as L

def load_cfg(path:str="runtime/config/inference.yaml"):
    with open(path,"r",encoding="utf-8") as f: return yaml.safe_load(f) or {}

def pick()->tuple[str, dict]:
    cfg=load_cfg(); pref=cfg.get("preferred","auto")
    if pref=="transformers" and T.available(): return "transformers", cfg.get("transformers") or {}
    if pref=="vllm_http" and V.available(cfg["vllm_http"]["url"]): return "vllm_http", cfg["vllm_http"]
    if pref=="ollama_http" and O.available(cfg["ollama_http"]["url"]): return "ollama_http", cfg["ollama_http"]
    if pref=="lmstudio_http" and L.available(cfg["lmstudio_http"]["url"]): return "lmstudio_http", cfg["lmstudio_http"]
    # auto-fallback order
    if T.available(): return "transformers", cfg.get("transformers") or {}
    if V.available(cfg["vllm_http"]["url"]): return "vllm_http", cfg["vllm_http"]
    if O.available(cfg["ollama_http"]["url"]): return "ollama_http", cfg["ollama_http"]
    if L.available(cfg["lmstudio_http"]["url"]): return "lmstudio_http", cfg["lmstudio_http"]
    return "none", {}
