from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ExpertBase(ABC):
    def __init__(self, name: str, description: str, triggers: List[str]):
        self.name = name
        self.description = description
        self.triggers = triggers
        self.confidence_threshold = 0.7
    
    def can_handle(self, query: str) -> float:
        """Return confidence score 0-1 for handling this query"""
        query_lower = query.lower()
        matches = sum(1 for trigger in self.triggers if trigger.lower() in query_lower)
        return min(matches / len(self.triggers) * 2, 1.0)  # Scale appropriately
    
    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the query and return response"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'triggers': self.triggers
        }