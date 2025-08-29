
import os, time
from typing import Dict, Any
from .config import CONFIG_ROOT, settings, save_yaml

LOG_PATH = os.path.join(CONFIG_ROOT, "..", "..", "data", "qes.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

class QES:
    def record(self, event: str, payload: Dict[str, Any]):
        with open(LOG_PATH, "a") as f:
            f.write(f"{time.time()}\t{event}\t{payload}\n")

    def propose(self) -> Dict[str, Any]:
        # naive: alternate quantization levels/timeouts based on crude counter
        counter = int(time.time()) % 3
        if counter == 0:
            return {"transformers": {"dtype": "float16"}, "llama_cpp": {"n_gpu_layers": 0}}
        elif counter == 1:
            return {"transformers": {"dtype": "float32"}, "llama_cpp": {"n_gpu_layers": 20}}
        else:
            return {"transformers": {"dtype": "bfloat16"}, "llama_cpp": {"n_gpu_layers": 8}}

def apply_qes_to_inference(proposal: Dict[str, Any]):
    path = os.path.join(CONFIG_ROOT, "inference.yaml")
    inf = settings.inference or {}
    for k,v in proposal.items():
        if k not in inf: inf[k] = {}
        inf[k].update(v)
    save_yaml(path, inf)
    settings.inference = inf
