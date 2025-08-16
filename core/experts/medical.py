from .base import ExpertBase
from typing import Dict, Any

class MedicalExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Medical",
            description="Medical information, health guidance, and wellness advice",
            triggers=["medical", "health", "symptom", "treatment", "diagnosis", "medicine", "wellness", "doctor"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Medical Expert] Providing health information: {query[:100]}..."
        
        disclaimers = [
            "This is general health information only, not medical advice",
            "Always consult with healthcare professionals for medical concerns"
        ]
        
        guidance = []
        if "symptom" in query.lower():
            guidance.append("Monitor symptoms and seek professional evaluation if persistent")
        if "wellness" in query.lower():
            guidance.append("Maintain balanced nutrition, exercise, and adequate sleep")
        
        return {
            "response": response,
            "guidance": guidance,
            "disclaimers": disclaimers,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }