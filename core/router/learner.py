
from __future__ import annotations
import json, math, os
from typing import Dict, List, Tuple
from .featurize import features

class SoftmaxRouter:
    def __init__(self, classes: List[str] | None = None):
        self.classes = classes or []
        self.weights: Dict[str, Dict[str,float]] = {c:{} for c in self.classes}
        self.bias: Dict[str,float] = {c:0.0 for c in self.classes}

    def _score(self, fv: Dict[str,float]) -> Dict[str,float]:
        z = {}
        for c in self.classes:
            s = self.bias.get(c, 0.0)
            wc = self.weights.get(c, {})
            for k, v in fv.items():
                s += wc.get(k, 0.0) * v
            z[c] = s
        m = max(z.values()) if z else 0.0
        exps = {c: math.exp(zc - m) for c, zc in z.items()}
        S = sum(exps.values()) or 1.0
        return {c: exps[c]/S for c in self.classes}

    def predict_topk(self, text: str, k: int = 3) -> List[Tuple[str,float]]:
        fv = features(text)
        probs = self._score(fv)
        return sorted(probs.items(), key=lambda x: x[1], reverse=True)[:k]

    def fit_online(self, text: str, label: str, lr: float = 0.2):
        if label not in self.classes:
            self.classes.append(label)
            self.weights[label] = {}
            self.bias[label] = 0.0
        fv = features(text)
        probs = self._score(fv)
        for c in self.classes:
            y = 1.0 if c == label else 0.0
            p = probs.get(c, 1.0/len(self.classes))
            g = (y - p)
            self.bias[c] = self.bias.get(c,0.0) + lr * g
            wc = self.weights.setdefault(c, {})
            for k, v in fv.items():
                wc[k] = wc.get(k, 0.0) + lr * g * v

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump({"classes": self.classes, "weights": self.weights, "bias": self.bias}, open(path, "w", encoding="utf-8"))

    @classmethod
    def load(cls, path: str) -> "SoftmaxRouter":
        obj = json.load(open(path, "r", encoding="utf-8"))
        r = cls(obj.get("classes", []))
        r.weights = obj.get("weights", {})
        r.bias = obj.get("bias", {})
        return r
