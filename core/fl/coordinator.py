
from __future__ import annotations
import time, threading
from typing import Dict, List, Any
import hashlib, json

class Coordinator:
    def __init__(self, min_clients: int = 2, round_timeout: int = 20):
        self.min_clients = min_clients
        self.round_timeout = round_timeout
        self.round = 0
        self.seals: Dict[int,str] = {}
        self.pool: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def submit(self, client_id: str, deltas: List[float]):
        with self.lock:
            self.pool.setdefault(str(self.round), []).append(sum(deltas)/max(1,len(deltas)))

    def aggregate(self, eps: float | None = None) -> Dict[str, Any]:
        start = time.time()
        while time.time() - start < self.round_timeout:
            with self.lock:
                cur = self.pool.get(str(self.round), [])
                if len(cur) >= self.min_clients:
                    break
            time.sleep(1)
        with self.lock:
            vals = self.pool.get(str(self.round), [])
            avg = sum(vals)/max(1,len(vals))
            seal = hashlib.sha256(json.dumps({'round':self.round,'values':vals},sort_keys=True).encode()).hexdigest()
            self.seals[self.round]=seal
            res = {"round": self.round, "avg": avg, "n": len(vals), "seal": self.seals.get(self.round)}
            self.round += 1
            return res
