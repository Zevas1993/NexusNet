
def available(): 
    try:
        import torch, transformers  # noqa: F401
        return True
    except Exception:
        return False

def generate(prompt: str, quant: str | None = None, model_id: str | None = None) -> str:
    import os

    from core.engines.transformers_engine import TransformersEngine

    selected_model = model_id or os.environ.get("NEXUS_TRANSFORMERS_MODEL")
    if not selected_model:
        raise RuntimeError("NEXUS_TRANSFORMERS_MODEL or model_id is required")
    device = "cuda" if os.environ.get("NEXUS_TRANSFORMERS_DEVICE") == "cuda" else "cpu"
    engine = TransformersEngine(selected_model, device=device)
    return engine.generate(prompt)
