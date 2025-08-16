from typing import Dict, Any
from core.providers.openrouter import OpenRouterClient
from core.providers.requesty import RequestyClient
from core.config import env_var

class TeacherGate:
    def __init__(self):
        self.openrouter = None
        self.requesty = None
        
        # Initialize providers if API keys are available
        or_key = env_var('OPENROUTER_API_KEY')
        if or_key:
            self.openrouter = OpenRouterClient(or_key)
        
        req_key = env_var('REQUESTY_API_KEY')
        if req_key:
            self.requesty = RequestyClient(req_key)
    
    async def get_teacher_response(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get response from teacher models for guidance"""
        if not self.openrouter and not self.requesty:
            return {"error": "No teacher providers available", "text": ""}
        
        # Try OpenRouter first, then Requesty
        if self.openrouter:
            try:
                response = await self.openrouter.generate(query)
                if not response.get('error'):
                    return {**response, "provider": "openrouter"}
            except Exception as e:
                pass
        
        if self.requesty:
            try:
                response = await self.requesty.generate(query)
                if not response.get('error'):
                    return {**response, "provider": "requesty"}
            except Exception as e:
                pass
        
        return {"error": "All teacher providers failed", "text": ""}
    
    def is_available(self) -> bool:
        """Check if any teacher providers are available"""
        return self.openrouter is not None or self.requesty is not None