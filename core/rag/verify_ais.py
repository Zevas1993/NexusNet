
from __future__ import annotations
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

LABELS = ["contradiction","neutral","entailment"]

class AISVerifier:
    def __init__(self, model_id: str):
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
    def entailed_mask(self, query: str, passages: list[str], threshold: float = 0.5):
        inputs = self.tok([query]*len(passages), passages, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad(): probs = torch.softmax(self.model(**inputs).logits, dim=-1)
        entail = probs[:,2].tolist()
        return [p >= threshold for p in entail], entail
