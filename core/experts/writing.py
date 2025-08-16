from .base import ExpertBase
from typing import Dict, Any

class WritingExpert(ExpertBase):
    def __init__(self):
        super().__init__(
            name="Writing",
            description="Content writing, copywriting, technical writing, and communication",
            triggers=["write", "content", "copy", "article", "documentation", "communication", "text"]
        )
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = f"[Writing Expert] Crafting written content: {query[:100]}..."
        
        guidelines = []
        if "documentation" in query.lower():
            guidelines.append("Structure content clearly with headings and examples")
        if "copy" in query.lower():
            guidelines.append("Focus on benefits and clear calls-to-action")
        
        return {
            "response": response,
            "guidelines": guidelines,
            "expert": self.name,
            "confidence": self.can_handle(query)
        }