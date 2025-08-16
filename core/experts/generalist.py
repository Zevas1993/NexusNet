"""Generalist expert for general queries"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse

class GeneralistExpert(BaseExpert):
    """General purpose expert for queries that don't match specific domains"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="generalist",
            specialties=["general", "conversation", "reasoning", "common knowledge"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Generalist can handle any query as fallback"""
        # Always provide moderate confidence as fallback
        return 0.5
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process general query"""
        confidence = 0.7  # Standard confidence for general queries
        
        response = f"""I'll help you with your question:

{query}

As a general AI assistant, I can provide information and assistance on a wide variety of topics including:

- General knowledge and factual information
- Problem-solving and reasoning
- Explanations and clarifications
- Creative tasks and brainstorming
- General advice and guidance

If you need specialized expertise in areas like programming, finance, medicine, or other technical domains, I can also coordinate with domain-specific experts in our system for more detailed analysis.

How can I best assist you with this question?"""
        
        return self._format_response(
            response,
            confidence,
            "Generalist expert providing general assistance"
        )
