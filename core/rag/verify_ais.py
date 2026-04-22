
from __future__ import annotations
LABELS = ["contradiction","neutral","entailment"]

class AISVerifier:
    def __init__(self, model_id: str):
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch
        except Exception as exc:
            raise RuntimeError("AISVerifier requires transformers and torch.") from exc
        self._torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
    def entailed_mask(self, query: str, passages: list[str], threshold: float = 0.5):
        inputs = self.tok([query]*len(passages), passages, return_tensors="pt", padding=True, truncation=True)
        with self._torch.no_grad(): probs = self._torch.softmax(self.model(**inputs).logits, dim=-1)
        entail = probs[:,2].tolist()
        return [p >= threshold for p in entail], entail
