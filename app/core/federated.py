
import os, json, secrets
from typing import List, Dict
from .config import settings

FED_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "federated"))
os.makedirs(FED_ROOT, exist_ok=True)

def _mask_vector(vec: List[float]) -> List[float]:
    # pairwise random mask
    rnd = secrets.SystemRandom()
    return [v + rnd.uniform(-0.1, 0.1) for v in vec]

class FedClient:
    def __init__(self, client_id: str):
        self.client_id = client_id

    def upload(self, vector: List[float]) -> str:
        masked = _mask_vector(vector)
        path = os.path.join(FED_ROOT, f"{self.client_id}.json")
        with open(path, "w") as f:
            json.dump(masked, f)
        return path

class FedCoordinator:
    def aggregate(self) -> List[float]:
        parts = []
        for name in os.listdir(FED_ROOT):
            if name.endswith(".json"):
                with open(os.path.join(FED_ROOT, name)) as f:
                    parts.append(json.load(f))
        if not parts: return []
        size = len(parts[0])
        agg = [0.0]*size
        for p in parts:
            for i,v in enumerate(p):
                agg[i] += v
        agg = [v/len(parts) for v in agg]
        with open(os.path.join(FED_ROOT, "aggregate.json"), "w") as f:
            json.dump(agg, f)
        return agg
