
def available(): 
    try:
        import torch, transformers  # noqa: F401
        return True
    except Exception:
        return False

def generate(prompt:str, quant:str|None=None)->str:
    # Placeholder; real impl would load model with quantization choice
    return f"[transformers/{quant or 'auto'}] {prompt[:80]}"
