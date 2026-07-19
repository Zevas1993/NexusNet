from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any, Callable


class GrammarConstrainedDecoder:
    def select(self, *, candidates: list[str], schema: dict[str, Any]) -> dict[str, Any]:
        rejected = []
        for candidate in candidates:
            try:
                value = json.loads(candidate)
                self._validate(value, schema, path="$", errors=[])
                return {"value": value, "raw": candidate, "rejected_count": len(rejected), "rejections": rejected}
            except (json.JSONDecodeError, ValueError) as exc:
                rejected.append({"candidate": candidate, "reason": str(exc)})
        raise ValueError(f"no candidate satisfied grammar/schema: {rejected}")

    def _validate(self, value: Any, schema: dict[str, Any], *, path: str, errors: list[str]) -> None:
        expected = schema.get("type")
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "null": type(None),
        }
        if expected in type_map and (not isinstance(value, type_map[expected]) or expected in {"integer", "number"} and isinstance(value, bool)):
            raise ValueError(f"{path} must be {expected}")
        if "enum" in schema and value not in schema["enum"]:
            raise ValueError(f"{path} is outside enum")
        if isinstance(value, dict):
            missing = [key for key in schema.get("required", []) if key not in value]
            if missing:
                raise ValueError(f"{path} missing required keys: {missing}")
            for key, child_schema in schema.get("properties", {}).items():
                if key in value:
                    self._validate(value[key], child_schema, path=f"{path}.{key}", errors=errors)
        if isinstance(value, list) and "items" in schema:
            for index, item in enumerate(value):
                self._validate(item, schema["items"], path=f"{path}[{index}]", errors=errors)


class SpeculativeDecoder:
    def decode(
        self,
        *,
        prompt_tokens: list[str],
        max_new_tokens: int,
        draft: Callable[[list[str], int], list[str]],
        verify: Callable[[list[str], str], bool],
        fallback: Callable[[list[str]], str],
    ) -> dict[str, Any]:
        if max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be positive")
        context = list(prompt_tokens)
        generated: list[str] = []
        accepted = 0
        fallback_count = 0
        while len(generated) < max_new_tokens:
            proposed = list(draft(list(context), max_new_tokens - len(generated)))
            if not proposed:
                token = fallback(list(context))
                context.append(token)
                generated.append(token)
                fallback_count += 1
                continue
            rejected = False
            for token in proposed:
                if len(generated) >= max_new_tokens:
                    break
                if verify(list(context), token):
                    context.append(token)
                    generated.append(token)
                    accepted += 1
                else:
                    replacement = fallback(list(context))
                    context.append(replacement)
                    generated.append(replacement)
                    fallback_count += 1
                    rejected = True
                    break
            if not rejected and not proposed:
                break
        return {"tokens": generated, "accepted_draft_tokens": accepted, "fallback_tokens": fallback_count}


class LearnedCascadeRouter:
    def __init__(self, *, models: dict[str, dict[str, Any]]) -> None:
        if not models:
            raise ValueError("models are required")
        self.models = deepcopy(models)
        self.update_count = 0

    def route(self, features: dict[str, float]) -> dict[str, Any]:
        scores = {}
        for model_id, config in self.models.items():
            score = sum(float(config.get("weights", {}).get(key, 0.0)) * float(value) for key, value in features.items())
            score -= float(config.get("cost", 0.0))
            scores[model_id] = score
        selected = min(scores, key=lambda model_id: (-scores[model_id], model_id))
        return {
            "model_id": selected,
            "scores": {key: round(value, 6) for key, value in scores.items()},
            "learned": self.update_count > 0,
            "fallback_order": sorted(scores, key=lambda model_id: (-scores[model_id], model_id)),
        }

    def update(self, *, model_id: str, features: dict[str, float], reward: float, learning_rate: float = 0.05) -> None:
        if model_id not in self.models:
            raise KeyError(model_id)
        weights = self.models[model_id].setdefault("weights", {})
        for key, value in features.items():
            weights[key] = float(weights.get(key, 0.0)) + float(learning_rate) * float(reward) * float(value)
        self.update_count += 1


class VerifiedSemanticCache:
    def __init__(self, *, similarity_threshold: float = 0.95) -> None:
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between zero and one")
        self.threshold = similarity_threshold
        self._items: dict[str, dict[str, Any]] = {}

    def put(self, *, cache_id: str, vector: list[float], value: Any, evidence_version: str, verification_refs: list[str]) -> None:
        if not cache_id or not evidence_version or not verification_refs:
            raise ValueError("verified cache requires id, evidence version, and verification refs")
        self._items[cache_id] = {
            "vector": self._normalized(vector),
            "value": deepcopy(value),
            "evidence_version": evidence_version,
            "verification_refs": list(verification_refs),
        }

    def get(self, *, vector: list[float], evidence_version: str) -> dict[str, Any]:
        query = self._normalized(vector)
        candidates = []
        for cache_id, item in self._items.items():
            if item["evidence_version"] != evidence_version or len(item["vector"]) != len(query):
                continue
            similarity = sum(left * right for left, right in zip(query, item["vector"]))
            if similarity >= self.threshold:
                candidates.append((similarity, cache_id, item))
        if not candidates:
            return {"hit": False, "reason": "no-verified-similar-entry"}
        similarity, cache_id, item = max(candidates, key=lambda candidate: (candidate[0], candidate[1]))
        return {"hit": True, "cache_id": cache_id, "similarity": round(similarity, 6), "value": deepcopy(item["value"]), "verification_refs": item["verification_refs"]}

    @staticmethod
    def _normalized(vector: list[float]) -> list[float]:
        values = [float(item) for item in vector]
        norm = math.sqrt(sum(item * item for item in values))
        if not values or norm == 0.0 or not math.isfinite(norm):
            raise ValueError("vector must have finite non-zero norm")
        return [item / norm for item in values]
