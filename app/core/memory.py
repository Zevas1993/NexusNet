
import os, json, time, hashlib
from typing import Dict, Any, List
from .config import settings, CONFIG_ROOT

DATA_ROOT = os.path.abspath(os.path.join(CONFIG_ROOT, "..", "..", "data"))
os.makedirs(DATA_ROOT, exist_ok=True)

class MemoryNode:
    def __init__(self, plane: str, content: Dict[str, Any], ts: float=None):
        self.plane = plane
        self.content = content
        self.ts = ts or time.time()
        self.id = hashlib.sha256(f"{plane}-{self.ts}-{json.dumps(content, sort_keys=True)}".encode()).hexdigest()[:16]

class PlaneStore:
    def __init__(self, plane: str):
        self.plane = plane
        self.path = os.path.join(DATA_ROOT, "memory", f"{plane}.jsonl")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def write(self, node: MemoryNode):
        with open(self.path, "a") as f:
            f.write(json.dumps({"id": node.id, "ts": node.ts, "plane": node.plane, "content": node.content}) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            return [json.loads(line) for line in f]

class PlaneAwareBudget:
    def __init__(self, planes_cfg: Dict[str, Any]):
        self.budget = {p["name"]: p.get("token_budget_ratio", 0.05) for p in planes_cfg.get("planes", [])}

    def allocate(self, total_tokens: int) -> Dict[str, int]:
        alloc = {plane: max(1, int(total_tokens * ratio)) for plane, ratio in self.budget.items()}
        return alloc

class ChatMemoryStore:
    def __init__(self):
        self.path = os.path.join(DATA_ROOT, "sessions")
        os.makedirs(self.path, exist_ok=True)

    def append(self, session_id: str, messages: List[Dict[str, Any]]):
        p = os.path.join(self.path, f"{session_id}.jsonl")
        with open(p, "a") as f:
            for m in messages:
                f.write(json.dumps(m) + "\n")

    def load(self, session_id: str) -> List[Dict[str, Any]]:
        p = os.path.join(self.path, f"{session_id}.jsonl")
        if not os.path.exists(p):
            return []
        with open(p) as f:
            return [json.loads(line) for line in f]
