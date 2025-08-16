import httpx, json
from typing import Dict, Any, Optional

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient()
    
    async def generate(self, prompt: str, model: str = "anthropic/claude-3-haiku", max_tokens: int = 512) -> Dict[str, Any]:
        """Generate text using OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": model,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "model": model
            }