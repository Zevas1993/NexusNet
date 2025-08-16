import llama_cpp
from typing import Dict, Any, Optional

class LlamaCppClient:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_gpu_layers: int = 0):
        self.model_path = model_path
        self.model = None
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self._load_model()
    
    def _load_model(self):
        """Load the GGUF model"""
        try:
            self.model = llama_cpp.Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using llama.cpp"""
        if not self.model:
            return {
                "error": "Model not loaded",
                "text": "",
                "model": "llama_cpp"
            }
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "\n\nUser:", "\n\nAssistant:"],
                echo=False
            )
            
            return {
                "text": response["choices"][0]["text"],
                "model": "llama_cpp",
                "tokens_used": response["usage"]["total_tokens"]
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "model": "llama_cpp"
            }
    
    def is_ready(self) -> bool:
        """Check if model is ready"""
        return self.model is not None