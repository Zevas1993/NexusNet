"""Operations audit and monitoring"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from core.config import STATE_DIR
import json
import time

class AuditLogger:
    """System audit and monitoring"""
    
    def __init__(self):
        self.audit_file = STATE_DIR / "audit.jsonl"
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_id: str = None):
        """Log an audit event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "user_id": user_id
        }
        
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_events(self, 
                   event_type: str = None,
                   since: datetime = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit events"""
        if not self.audit_file.exists():
            return []
        
        events = []
        with open(self.audit_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    
                    # Filter by event type
                    if event_type and event.get('event_type') != event_type:
                        continue
                    
                    # Filter by timestamp
                    if since:
                        event_time = datetime.fromisoformat(event['timestamp'])
                        if event_time < since:
                            continue
                    
                    events.append(event)
                    
                    # Apply limit
                    if len(events) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return list(reversed(events))  # Most recent first
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system usage statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        events_24h = self.get_events(since=last_24h, limit=10000)
        events_1h = self.get_events(since=last_hour, limit=10000)
        
        stats = {
            "events_last_24h": len(events_24h),
            "events_last_hour": len(events_1h),
            "event_types_24h": {},
            "top_users_24h": {},
            "system_health": "healthy"
        }
        
        # Count event types
        for event in events_24h:
            event_type = event.get('event_type', 'unknown')
            stats["event_types_24h"][event_type] = stats["event_types_24h"].get(event_type, 0) + 1
        
        # Count user activity
        for event in events_24h:
            user_id = event.get('user_id', 'anonymous')
            stats["top_users_24h"][user_id] = stats["top_users_24h"].get(user_id, 0) + 1
        
        # Determine system health
        if len(events_1h) > 1000:  # High activity
            stats["system_health"] = "high_load"
        elif any(event.get('event_type') == 'error' for event in events_1h):
            stats["system_health"] = "degraded"
        
        return stats

# Global audit logger instance
audit_logger = AuditLogger()

def log_query(query: str, expert: str, response_time: float, user_id: str = None):
    """Log a query event"""
    audit_logger.log_event("query", {
        "query_length": len(query),
        "expert": expert,
        "response_time_ms": round(response_time * 1000, 2)
    }, user_id)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Log an error event"""
    audit_logger.log_event("error", {
        "error_type": error_type,
        "error_message": error_message,
        "context": context or {}
    })

def log_system_event(event_type: str, details: Dict[str, Any]):
    """Log a system event"""
    audit_logger.log_event("system", {
        "system_event_type": event_type,
        **details
    })
