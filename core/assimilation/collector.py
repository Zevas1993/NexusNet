import json, hashlib, datetime as dt
from typing import Dict, List

class AssimCollector:
    def __init__(self):
        self.buffer: List[Dict] = []
    
    def ingest(self, source: str, data: Dict):
        entry = {
            'timestamp': dt.datetime.utcnow().isoformat(),
            'source': source,
            'content_hash': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16],
            'data': data
        }
        self.buffer.append(entry)
    
    def dump_batch(self) -> List[Dict]:
        batch = self.buffer.copy()
        self.buffer.clear()
        return batch