
import yaml
from core.inference import transformers as T
from core.inference import vllm_http as V
from core.inference import ollama_http as O
from core.inference import lmstudio_http as L

def load_cfg(path:str="runtime/config/inference.yaml"):
    with open(path,"r",encoding="utf-8") as f: return yaml.safe_load(f) or {}

def _provider_cfg(cfg: dict, key: str, fallback_key: str | None = None) -> dict:
    data = cfg.get(key) or {}
    if fallback_key and not data:
        data = cfg.get(fallback_key) or {}
    if "url" not in data and data.get("endpoint"):
        data = {**data, "url": data["endpoint"]}
    return data

def pick()->tuple[str, dict]:
    cfg=load_cfg(); pref=cfg.get("preferred","auto")
    transformers_cfg = cfg.get("transformers") or {}
    vllm_cfg = _provider_cfg(cfg, "vllm_http", "vllm")
    ollama_cfg = _provider_cfg(cfg, "ollama_http", "ollama")
    lmstudio_cfg = _provider_cfg(cfg, "lmstudio_http", "lmstudio")
    if pref=="transformers" and T.available(): return "transformers", transformers_cfg
    if pref=="vllm_http" and vllm_cfg.get("url") and V.available(vllm_cfg["url"]): return "vllm_http", vllm_cfg
    if pref=="ollama_http" and ollama_cfg.get("url") and O.available(ollama_cfg["url"]): return "ollama_http", ollama_cfg
    if pref=="lmstudio_http" and lmstudio_cfg.get("url") and L.available(lmstudio_cfg["url"]): return "lmstudio_http", lmstudio_cfg
    # auto-fallback order
    if T.available(): return "transformers", transformers_cfg
    if vllm_cfg.get("url") and V.available(vllm_cfg["url"]): return "vllm_http", vllm_cfg
    if ollama_cfg.get("url") and O.available(ollama_cfg["url"]): return "ollama_http", ollama_cfg
    if lmstudio_cfg.get("url") and L.available(lmstudio_cfg["url"]): return "lmstudio_http", lmstudio_cfg
    return "none", {}
