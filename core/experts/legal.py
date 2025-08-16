from .base import ExpertBase
from typing import Dict, Any

class LegalExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Legal",
            description="Legal advice, compliance, contracts, and regulatory matters",
            triggers=["legal", "law", "contract", "compliance", "regulation", "rights", "liability", "terms"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Legal Expert] Reviewing legal considerations: {query[:100]}..."
        
        disclaimers = [
            "This is general information only, not legal advice",
            "Consult with a qualified attorney for specific legal matters"
        ]
        
        guidance = []
        if "contract" in query.lower():
            guidance.append("Ensure all terms are clearly defined and mutually agreed upon")
        if "compliance" in query.lower():
            guidance.append("Stay updated with relevant regulations in your jurisdiction")
        
        return {
            "response": response,
            "guidance": guidance,
            "disclaimers": disclaimers,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }