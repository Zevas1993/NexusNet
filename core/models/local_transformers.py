import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Any, Optional

class TransformersClient:
    def __init__(self, model_name: str, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the transformers model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"Failed to load model {self.model_name}: {e}")
            self.model = None
            self.tokenizer = None
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using transformers"""
        if not self.model or not self.tokenizer:
            return {
                "error": "Model not loaded",
                "text": "",
                "model": "transformers"
            }
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = generated_text[len(prompt):].strip()
            
            return {
                "text": response_text,
                "model": "transformers",
                "tokens_used": len(outputs[0])
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "model": "transformers"
            }
    
    def is_ready(self) -> bool:
        """Check if model is ready"""
        return self.model is not None and self.tokenizer is not None