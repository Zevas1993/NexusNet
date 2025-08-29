
from __future__ import annotations
import importlib, pkgutil, os, yaml
from typing import Dict, Any, Optional

class ExpertModule:
    def __init__(self, name: str, module):
        self.name = name
        self.module = module
        self.prompt_prefix = getattr(module, "PROMPT_PREFIX", "")
        self.generate = getattr(module, "infer", None) or getattr(module, "generate", None)

class ExpertRegistry:
    def __init__(self, cfg_path: str = "runtime/config/experts.yaml"):
        with open(cfg_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f) or {}
        self.modules: Dict[str, ExpertModule] = {}
        self._discover()

    def _discover(self):
        try:
            import core.experts as pkg
        except Exception:
            return
        for m in pkgutil.iter_modules(pkg.__path__):
            if m.ispkg: continue
            mod = importlib.import_module(f"core.experts.{m.name}")
            self.modules[m.name] = ExpertModule(m.name, mod)

    def select(self, message: str) -> Optional[str]:
        # Heuristic: use config patterns if defined; fallback to simple keyword rules
        ex_cfg = self.cfg.get("experts", {})
        # Priority based on config order
        for name, conf in ex_cfg.items():
            if not conf.get("route", True): continue
            pats = [p.lower() for p in conf.get("patterns", [])]
            if pats and any(p in message.lower() for p in pats):
                return name
        # fallback heuristics
        low = message.lower()
        if any(k in low for k in ["def ", "class ", "import ", "error:", "traceback", "stack overflow", "compile"]):
            return "code" if "code" in ex_cfg else None
        if any(k in low for k in ["theorem","proof","integral","derivative","∑","∫","≅","≈","=~"]):
            return "math" if "math" in ex_cfg else None
        return "generalist" if "generalist" in ex_cfg else None

    def prompt_prefix(self, name: str) -> str:
        try:
            return self.cfg["experts"][name].get("prompt_prefix", "") or self.modules.get(name, None).prompt_prefix if name in self.cfg.get("experts",{}) else ""
        except Exception:
            return ""

    def model_override(self, name: str) -> Optional[str]:
        try:
            return self.cfg["experts"][name].get("model_id")
        except Exception:
            return None
