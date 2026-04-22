from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow

from ..function_calling.validator import validate_function_call
from ..grounding.validator import validate_grounding_payload
from ..latency_profiles.evaluator import evaluate_latency_profile


class EdgeVisionOperationalBenchmarkSuite:
    def __init__(self, *, artifacts_dir: Path, config: dict[str, Any]):
        self.artifacts_dir = artifacts_dir
        self.config = config

    def run(self, provider_id: str | None = None) -> dict[str, Any]:
        provider_id = provider_id or self.config.get("default_provider")
        providers = self.config.get("providers", {}) or {}
        provider = dict(providers.get(provider_id, {}))
        cases = list(((self.config.get("operationalization") or {}).get("benchmark_cases", [])))
        if not provider or not cases:
            return {
                "status_label": "IMPLEMENTATION BRANCH",
                "provider_id": provider_id,
                "summary": {"case_count": 0, "reason": "Missing edge vision provider metadata or benchmark cases."},
                "artifacts": {},
            }

        profiles = self.config.get("latency_profiles", {}) or {}
        schema = self.config.get("grounding_schema", {}) or {}
        catalog = list(self.config.get("function_catalog", []))
        case_results: list[dict[str, Any]] = []
        for case in cases:
            profile_eval = evaluate_latency_profile(
                profile_id=str(case.get("profile_id")),
                profiles=profiles,
                max_resolution=int(case.get("max_resolution", 0) or 0),
            )
            grounding_eval = validate_grounding_payload(
                schema=schema,
                payload={"boxes": list(case.get("sample_boxes", []))},
            )
            function_eval = validate_function_call(
                catalog=catalog,
                payload={"function": case.get("expected_function")},
            )
            locale = str(case.get("locale", "en"))
            language_ok = locale in set(provider.get("languages") or provider.get("multilingual_languages", []))
            safe_mode_ok = (not case.get("require_safe_mode")) or (
                "safe-mode" in set(provider.get("candidate_modes", []))
                and "safe-mode" in set(profile_eval.get("intended_modes", []))
            )
            structured_ok = (not case.get("require_structured_output")) or bool(provider.get("structured_outputs"))
            passed = all(
                [
                    profile_eval["found"],
                    profile_eval["resolution_ok"],
                    grounding_eval["valid"],
                    function_eval["valid"],
                    language_ok,
                    safe_mode_ok,
                    structured_ok,
                ]
            )
            case_results.append(
                {
                    "case_id": case.get("case_id"),
                    "profile_id": case.get("profile_id"),
                    "locale": locale,
                    "passed": passed,
                    "profile": profile_eval,
                    "grounding": grounding_eval,
                    "function_call": function_eval,
                    "language_ok": language_ok,
                    "safe_mode_ok": safe_mode_ok,
                    "structured_output_ok": structured_ok,
                }
            )

        summary = {
            "case_count": len(case_results),
            "pass_rate": round(sum(1 for case in case_results if case["passed"]) / max(len(case_results), 1), 4),
            "provider_id": provider_id,
            "safe_mode_ready": all(case["safe_mode_ok"] for case in case_results if case.get("profile_id")),
            "grounding_ready": all(case["grounding"]["valid"] for case in case_results),
            "function_calling_ready": all(case["function_call"]["valid"] for case in case_results),
            "multilingual_ready": all(case["language_ok"] for case in case_results),
            "generated_at": utcnow().isoformat(),
        }
        report_id = new_id("edgevision")
        destination = self.artifacts_dir / "vision" / "edge-bench" / report_id
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        cases_path = destination / "cases.json"
        report_path = destination / "report.md"
        metrics_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        cases_path.write_text(json.dumps(case_results, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# Edge Vision Operationalization {report_id}",
                    "",
                    f"- Provider: {provider_id}",
                    f"- Case count: {summary['case_count']}",
                    f"- Pass rate: {summary['pass_rate']}",
                    f"- Safe-mode ready: {summary['safe_mode_ready']}",
                    f"- Grounding ready: {summary['grounding_ready']}",
                    f"- Function-calling ready: {summary['function_calling_ready']}",
                    f"- Multilingual ready: {summary['multilingual_ready']}",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "report_id": report_id,
            "summary": summary,
            "cases": case_results,
            "artifacts": {
                "metrics": str(metrics_path),
                "cases": str(cases_path),
                "report": str(report_path),
            },
        }

    def summary(self, provider_id: str | None = None) -> dict[str, Any]:
        base = self.artifacts_dir / "vision" / "edge-bench"
        latest = None
        if base.exists():
            candidates = sorted([path for path in base.iterdir() if path.is_dir()], key=lambda item: item.name, reverse=True)
            for candidate in candidates:
                metrics_path = candidate / "metrics.json"
                if metrics_path.exists():
                    latest = json.loads(metrics_path.read_text(encoding="utf-8"))
                    break
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "provider_id": provider_id or self.config.get("default_provider"),
            "latest_benchmark": latest,
        }
