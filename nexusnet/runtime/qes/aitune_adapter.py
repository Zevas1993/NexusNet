from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any


class AITuneAdapter:
    def __init__(self, *, config: dict[str, Any], artifacts_dir: Path):
        self.config = config
        self.artifacts_dir = artifacts_dir

    def tune(
        self,
        *,
        capability: dict[str, Any],
        model_id: str,
        module_kind: str,
        backend_preferences: list[str],
        work_dir: Path,
    ) -> dict[str, Any]:
        if not capability.get("available", False):
            return {
                "status": "skipped",
                "reason": "AITune is unavailable in the current environment.",
                "selected_backend": None,
                "artifact_lineage": {},
                "errors": [],
            }
        if not bool(self.config.get("allow_live_invoke", False)):
            return {
                "status": "shadow-only",
                "reason": "AITune live invocation is disabled by config; provider remains benchmark-gated and non-mandatory.",
                "selected_backend": None,
                "artifact_lineage": {},
                "errors": [],
            }

        module = self._load_module()
        work_dir.mkdir(parents=True, exist_ok=True)
        request = {
            "model_id": model_id,
            "module_kind": module_kind,
            "backend_preferences": backend_preferences,
            "artifacts_dir": str(work_dir),
        }
        errors: list[str] = []
        for candidate in ["autotune", "tune"]:
            func = getattr(module, candidate, None)
            if not callable(func):
                continue
            try:
                result = self._invoke_callable(func, request)
                return self._normalize_result(result=result, request=request, surface=candidate)
            except Exception as exc:  # pragma: no cover - defensive runtime path
                errors.append(f"{candidate}: {exc}")
        tuner_cls = getattr(module, "AITuner", None)
        if tuner_cls is not None:
            try:
                tuner = tuner_cls()
                if hasattr(tuner, "tune"):
                    result = self._invoke_callable(getattr(tuner, "tune"), request)
                    return self._normalize_result(result=result, request=request, surface="AITuner.tune")
            except Exception as exc:  # pragma: no cover - defensive runtime path
                errors.append(f"AITuner.tune: {exc}")
        return {
            "status": "adapter-error",
            "reason": "AITune was installed but no supported callable surface was successfully invoked.",
            "selected_backend": None,
            "artifact_lineage": {"call_attempts": ["autotune", "tune", "AITuner.tune"]},
            "errors": errors,
        }

    def _load_module(self):
        return importlib.import_module("aitune")

    def _invoke_callable(self, func, request: dict[str, Any]):
        signature = inspect.signature(func)
        kwargs = {}
        for name in signature.parameters:
            if name in {"model", "model_id", "target"}:
                kwargs[name] = request["model_id"]
            elif name in {"module_kind", "kind"}:
                kwargs[name] = request["module_kind"]
            elif name in {"backends", "backend_preferences", "providers"}:
                kwargs[name] = request["backend_preferences"]
            elif name in {"artifacts_dir", "work_dir", "output_dir"}:
                kwargs[name] = request["artifacts_dir"]
        return func(**kwargs)

    def _normalize_result(self, *, result: Any, request: dict[str, Any], surface: str) -> dict[str, Any]:
        payload = result
        if hasattr(result, "to_dict"):
            payload = result.to_dict()
        elif not isinstance(result, dict):
            payload = {
                "selected_backend": getattr(result, "selected_backend", None),
                "metrics": getattr(result, "metrics", {}),
                "artifact_path": getattr(result, "artifact_path", None),
            }
        selected_backend = (
            payload.get("selected_backend")
            or payload.get("backend")
            or payload.get("selected_provider")
            or (request["backend_preferences"][0] if request["backend_preferences"] else None)
        )
        return {
            "status": "completed",
            "reason": f"AITune callable '{surface}' completed.",
            "selected_backend": selected_backend,
            "artifact_lineage": {
                "surface": surface,
                "request": request,
                "raw_artifact_path": payload.get("artifact_path"),
            },
            "metrics": payload.get("metrics", {}),
            "raw_payload": payload,
            "errors": [],
        }
