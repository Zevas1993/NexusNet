
import os, json, time, random
from typing import Dict, Any, List
from .memory import PlaneStore, MemoryNode
from .config import settings

DREAM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "dreams"))
os.makedirs(DREAM_ROOT, exist_ok=True)

class CritiqueAgent:
    def evaluate(self, sample: str) -> Dict[str, Any]:
        # Simple heuristic scoring
        return {"coherence": min(1.0, len(sample)/200.0), "novelty": random.uniform(0.3, 0.9)}

class DreamLoop:
    def __init__(self):
        self.crit = CritiqueAgent()
        self.proc_store = PlaneStore("procedural")
        self.imag_store = PlaneStore("imaginal")

    def run_once(self):
        # Generate
        idea = f"Idea at {time.time()}: improve retrieval by adding time-aware decay."
        # Evaluate
        score = self.crit.evaluate(idea)
        # Learn (write to memory planes)
        self.proc_store.write(MemoryNode("procedural", {"idea": idea, "score": score}))
        self.imag_store.write(MemoryNode("imaginal", {"dream": f"Simulate {idea}"}))
        # Package assimilation
        fname = os.path.join(DREAM_ROOT, f"assim_{int(time.time())}.json")
        with open(fname, "w") as f:
            json.dump({"idea": idea, "score": score}, f)

        return {"idea": idea, "score": score, "package": fname}
