from __future__ import annotations
from typing import Dict, Any, Optional, List
import os, yaml, json
try:
    from services.otel import start_span
except Exception:
    def start_span(name: str, **attrs):
        from contextlib import contextmanager
        @contextmanager
        def _n():
            yield None
        return _n()
try:
    from services.metrics_server import record_router_pair
except Exception:
    record_router_pair = None

from .hw.scan import suggest
from .engines.transformers_engine import TransformersEngine
from .engines.vllm_http_engine import VLLMHttpEngine
from .engines.ollama_engine import OllamaEngine
from .engines.lmstudio_engine import LMStudioEngine
try:
    from .engines.llamacpp_engine import LlamaCppEngine
except Exception:
    LlamaCppEngine = None

from .rag.pipeline import RAGPipeline
from .experts.registry import ExpertRegistry
from .safety.input_filter import enforce_length, redact_pii
from .safety.output_filter import sanitize
from .ebt.energy import energy_score
from core.router.inference import LearnedRouter
from quantlab.policy import current_policy
import yaml
try:
    from apps.api.main import _emit_chat_event
except Exception:
    _emit_chat_event = None

# Optional providers (TeacherGate)
try:
    from .providers.openrouter import OpenRouterClient
except Exception:
    OpenRouterClient = None
try:
    from .providers.requesty import RequestyClient
except Exception:
    RequestyClient = None

# Optional experts registry (files may come from MERGED-FULL bundle)
try:
    from .experts import __all__ as EXPERT_MODULES  # type: ignore
except Exception:
    EXPERT_MODULES = []

class Orchestrator:
    def __init__(self, cfg_path: str = "runtime/config/settings.yaml"):
        # Learned router (optional)
        try:
            rcfg = yaml.safe_load(open('runtime/config/router.yaml','r',encoding='utf-8')) or {}
            self._router_cfg = rcfg.get('learned',{})
            self.learned_router = LearnedRouter()
        except Exception:
            self._router_cfg = {}
            self.learned_router = None
        with open(cfg_path,"r",encoding="utf-8") as f: self.cfg = yaml.safe_load(f)
        self.engine = None; self.engine_name = None
        self.rag = RAGPipeline("runtime/config/rag.yaml")
        self.registry = ExpertRegistry("runtime/config/experts.yaml")
        # load providers config & secrets
        self.providers_cfg = self._load_yaml("runtime/config/providers.yaml")
        self.secrets = self._load_json("runtime/config/secrets.json")
        # simple expert registry parsed from config (names only)
        self.experts_cfg = self._load_yaml("runtime/config/experts.yaml")

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        try:
            with open(path,"r",encoding="utf-8") as f: return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _load_json(self, path: str) -> Dict[str, Any]:
        try:
            with open(path,"r",encoding="utf-8") as f: return json.load(f)
        except Exception:
            return {}

    def _ensure_engine(self):
        if self.engine is not None: return
        order = self.cfg.get("engine_order", ["transformers"])
        defaults = self.cfg.get("defaults", {})
        hw = suggest()
        model_id = os.environ.get("NEXUSNET_MODEL_ID", defaults.get("model_id"))
        for name in order:
            try:
                if name == "transformers":
                    self.engine = TransformersEngine(model_id, device=hw["device"])
                elif name == "vllm_http":
                    self.engine = VLLMHttpEngine()
                elif name == "ollama":
                    self.engine = OllamaEngine()
                elif name == "lmstudio":
                    self.engine = LMStudioEngine()
                elif name == "llamacpp" and LlamaCppEngine is not None and os.path.exists(model_id):
                    self.engine = LlamaCppEngine(model_id)
                if self.engine: self.engine_name = name; break
            except Exception:
                self.engine = None
        if self.engine is None: raise RuntimeError("No engine could be initialized.")

    def _teacher_gate_complete(self, prompt: str, **kw) -> Optional[str]:
        tg = (self.providers_cfg.get("teacher_gate") or {})
        if not tg.get("enabled", False): return None
        # Prefer OpenRouter then Requesty if configured
        openrouter_key = (self.secrets.get("openrouter") or {}).get("api_key","")
        requesty_key = (self.secrets.get("requesty") or {}).get("api_key","")
        models = tg.get("models") or []
        if OpenRouterClient and openrouter_key:
            try:
                client = OpenRouterClient(api_key=openrouter_key)
                # choose first listed model or use a default placeholder
                model = models[0] if models else "openrouter/openai/gpt-3.5"
                return client.complete(prompt, model=model, max_tokens=kw.get("max_new_tokens",256), temperature=kw.get("temperature",0.7))
            except Exception:
                pass
        if RequestyClient and requesty_key:
            try:
                client = RequestyClient(api_key=requesty_key)
                model = models[0] if models else "meta-llama/Meta-Llama-3-8B-Instruct"
                return client.complete(prompt, model=model, max_tokens=kw.get("max_new_tokens",256), temperature=kw.get("temperature",0.7))
            except Exception:
                pass
        return None

    def _route_expert(self, message: str) -> Optional[str]:
        # Minimal heuristic routing: look up experts that are enabled in config; in a real system,
        # we would load per-expert adapters or call into expert modules.
        try:
            ex = (self.experts_cfg.get("experts") or {})
            # placeholder: prefer 'code' if code-like tokens
            if any(tok in message.lower() for tok in ["def ", "class ", "import ", "error:", "traceback"]):
                if ex.get("code",{}).get("route", True):
                    return "code"
            return "generalist" if "generalist" in ex else None
        except Exception:
            return None

    def chat(self, message: str, rag: bool = True, **kw) -> Dict[str, Any]:
        self._ensure_engine()
        s = self.cfg.get("safety", {})
        prompt = enforce_length(message, s.get("max_input_chars",8000))
        prompt = redact_pii(prompt, s.get("pii_redact", True))
        # Expert routing (lightweight label only)
        capsule = self._route_expert(prompt) or self.registry.select(prompt) or "generalist"
        if rag:
            prompt = self.rag.augment(prompt)
        params = self.cfg.get("defaults",{}); params.update(kw)
        feat = self.cfg.get("features", {})
        # per-expert model override
        override_model_id = self.registry.model_override(capsule)
        if override_model_id:
            params["override_model_id"] = override_model_id

        # Try local engine first
        try:
            text = self.engine.generate(prompt, **params)
        except Exception:
            text = ""

        # TeacherGate fallback if local empty or disabled by config
        if (not text) or feat.get("teacher_gate_force", False) or (self.providers_cfg.get("teacher_gate",{}).get("force", False)):
            tg_out = self._teacher_gate_complete(prompt, **params)
            if tg_out:
                text = tg_out if not text else f"{text}\n\n[TeacherGate]\n{tg_out}"

        
        # Dreamer improvement (optional)
        if feat.get("dreamer", False):
            try:
                from recursive_dreamer.loop import dream_once  # expected API
                improved = dream_once(prompt, text)
                if improved and isinstance(improved, str):
                    text = improved
            except Exception:
                pass
    
        return {"text": sanitize(text), "engine": self.engine_name, "capsule": capsule}

    def rag_ingest(self, texts):
        return self.rag.ingest(texts)



# --- r11.4 policy-aware wrapper (safe, no behavior change if policy files missing) ---
try:
    from core.quant.apply import choose_for_capsule as _nn_choose_policy
except Exception:  # allow import if package layout differs
    try:
        from quant.apply import choose_for_capsule as _nn_choose_policy
    except Exception:
        _nn_choose_policy = None

try:
    _Orc = Orchestrator
    if hasattr(_Orc, "generate") and _nn_choose_policy is not None:
        _orig_gen = _Orc.generate
        def _patched_generate(self, prompt: str, capsule: str | None = None, **kw):
            pol = _nn_choose_policy(capsule)
            # expose choice for downstream engines (if any read these attrs)
            setattr(self, "_policy_choice", pol)
            # thread capsule into original call if it accepts it
            try:
                return _orig_gen(self, prompt, capsule=capsule, **kw)
            except TypeError:
                return _orig_gen(self, prompt, **kw)
        _Orc.generate = _patched_generate
except Exception:
    pass
