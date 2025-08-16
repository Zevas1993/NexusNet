from .base import ExpertBase
from typing import Dict, Any

class DesignExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Design",
            description="UI/UX design, visual design, user experience, and design systems",
            triggers=["design", "ui", "ux", "interface", "user experience", "visual", "layout", "prototype"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Design Expert] Analyzing design requirements: {query[:100]}..."
        
        principles = []
        if "user" in query.lower():
            principles.append("Focus on user-centered design principles")
        if "interface" in query.lower():
            principles.append("Ensure consistency and intuitive navigation")
        
        return {
            "response": response,
            "principles": principles,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }