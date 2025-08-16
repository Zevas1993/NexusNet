from .base import ExpertBase
from typing import Dict, Any

class TranslationExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Translation",
            description="Language translation, localization, and cross-cultural communication",
            triggers=["translate", "language", "localization", "multilingual", "cultural", "international"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Translation Expert] Facilitating cross-language communication: {query[:100]}..."
        
        considerations = []
        if "translate" in query.lower():
            considerations.append("Consider context and cultural nuances, not just literal translation")
        if "localization" in query.lower():
            considerations.append("Adapt content to local customs and preferences")
        
        return {
            "response": response,
            "considerations": considerations,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }