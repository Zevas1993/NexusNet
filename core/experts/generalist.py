from .base import ExpertBase
from typing import Dict, Any

class GeneralistExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Generalist",
            description="General knowledge, common questions, and broad topic coverage",
            triggers=["general", "what", "how", "why", "explain", "help", "information"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Generalist Expert] Providing general assistance: {query[:100]}..."
        
        # Default fallback responses
        suggestions = [
            "Consider breaking down complex questions into smaller parts",
            "Look for reliable sources and cross-reference information"
        ]
        
        return {
            "response": response,
            "suggestions": suggestions,
            "expert": self.name,
            "confidence": max(0.3, self.can_handle(query))  # Always have some confidence as fallback
        }