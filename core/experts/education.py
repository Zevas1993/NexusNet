from .base import ExpertBase
from typing import Dict, Any

class EducationExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Education",
            description="Learning, teaching, curriculum design, and educational technology",
            triggers=["learn", "teach", "education", "curriculum", "student", "course", "training", "knowledge"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Education Expert] Facilitating learning: {query[:100]}..."
        
        learning_tips = []
        if "learn" in query.lower():
            learning_tips.append("Use spaced repetition and active recall techniques")
        if "teach" in query.lower():
            learning_tips.append("Employ varied teaching methods to accommodate different learning styles")
        
        return {
            "response": response,
            "learning_tips": learning_tips,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }