import httpx, json
from typing import Dict, Any, Optional

class VLLMClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using vLLM server"""
        payload = {
            "model": "default",  # vLLM server model
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["text"],
                "model": "vllm",
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "model": "vllm"
            }
    
    async def check_health(self) -> bool:
        """Check if vLLM server is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except:
            return False