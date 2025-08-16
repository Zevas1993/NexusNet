import json, hashlib, datetime as dt
from typing import Dict, Any, List
from pathlib import Path

class AuditLogger:
    def __init__(self, log_dir: str = "runtime/state/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, data: Dict[str, Any], user_id: str = "system"):
        """Log an audit event"""
        timestamp = dt.datetime.utcnow().isoformat()
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "data": data,
            "event_hash": self._compute_hash(event_type, data, timestamp)
        }
        
        log_file = self.log_dir / f"audit_{dt.date.today().isoformat()}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    
    def _compute_hash(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """Compute event hash for integrity"""
        content = f"{event_type}|{json.dumps(data, sort_keys=True)}|{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_recent_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        events = []
        for i in range(days):
            date = dt.date.today() - dt.timedelta(days=i)
            log_file = self.log_dir / f"audit_{date.isoformat()}.jsonl"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            events.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)