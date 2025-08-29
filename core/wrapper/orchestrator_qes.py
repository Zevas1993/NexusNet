
from core.inference.selector import pick
from core.safe.controller import advise
from core.governance.enforcer import require_acceptance

def generate(prompt:str)->str:
    if not require_acceptance():
        return "[ToU not accepted] Please accept terms to enable generation."
    backend, cfg = pick()
    health = advise()
    prefix=f"[{backend}:{cfg}]"
    if health.get("action")=="pause":
        return prefix + " [paused due to temps/VRAM]; try again later."
    # defer to backend
    if backend=="transformers":
        from core.inference.transformers import generate as g; return prefix+" "+g(prompt, quant=cfg.get("quant","auto"))
    if backend=="vllm_http":
        from core.inference.vllm_http import generate as g; return prefix+" "+g(cfg["url"], prompt)
    if backend=="ollama_http":
        from core.inference.ollama_http import generate as g; return prefix+" "+g(cfg["url"], prompt)
    if backend=="lmstudio_http":
        from core.inference.lmstudio_http import generate as g; return prefix+" "+g(cfg["url"], prompt)
    return "[no backend available] " + prompt[:120]
