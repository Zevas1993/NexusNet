from __future__ import annotations

import json
from statistics import mean

from nexus.schemas import new_id

from ..memory import NeuralMemoryCortex
from ..schemas import BenchmarkCase, BenchmarkCaseResult, BenchmarkRun, SessionContext
from ..telemetry import BrainTelemetryLogger


class BenchmarkHarness:
    def __init__(self, *, telemetry: BrainTelemetryLogger, memory: NeuralMemoryCortex, artifact_writer):
        self.telemetry = telemetry
        self.memory = memory
        self._artifact_writer = artifact_writer

    def run(self, *, suite_name: str, brain, cases: list[BenchmarkCase], model_hint: str | None = None) -> BenchmarkRun:
        results: list[BenchmarkCaseResult] = []
        run_model_id = "unknown"
        run_runtime = "unknown"
        for case in cases:
            session = SessionContext(
                session_id=f"bench-{case.case_id}",
                trace_id=new_id("braintrace"),
                expert=case.expert,
                task_type="benchmark",
                use_retrieval=case.use_retrieval,
                metadata={"benchmark_suite": suite_name, **case.metadata},
            )
            generated = brain.generate(session_context=session, prompt=case.prompt, model_hint=case.model_hint or model_hint)
            run_model_id = generated.model_id
            run_runtime = generated.runtime_name
            output_lower = generated.output.lower()
            matched = [token for token in case.expected_substrings if token.lower() in output_lower]
            failures = []
            if len(matched) != len(case.expected_substrings):
                failures.append("missing_expected_substrings")
            if case.max_latency_ms is not None and generated.inference_trace.latency_ms > case.max_latency_ms:
                failures.append("latency_budget_exceeded")
            expected_count = max(len(case.expected_substrings), 1)
            score = round((len(matched) / expected_count) - (0.2 if "latency_budget_exceeded" in failures else 0.0), 3)
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    passed=not failures,
                    score=max(0.0, score),
                    latency_ms=generated.inference_trace.latency_ms,
                    output_preview=generated.output[:240],
                    matched_substrings=matched,
                    failure_modes=failures,
                )
            )
        run = BenchmarkRun(
            suite_name=suite_name,
            model_id=run_model_id,
            runtime_name=run_runtime,
            case_count=len(cases),
            pass_rate=round(sum(1 for result in results if result.passed) / max(len(results), 1), 3),
            avg_latency_ms=round(mean([result.latency_ms for result in results]) if results else 0.0, 3),
            results=results,
        )
        artifact_path = self._artifact_writer(
            f"benchmarks/{run.run_id}.json",
            json.dumps(run.model_dump(mode="json"), ensure_ascii=True, indent=2),
        )
        run.artifact_path = artifact_path
        self.memory.record_benchmark_run(run)
        self.telemetry.log_benchmark(run.model_dump(mode="json"))
        return run
