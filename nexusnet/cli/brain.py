from __future__ import annotations

import argparse
import json

from nexus.services import build_services

from ..schemas import (
    BenchmarkCase,
    CurriculumAssessmentRequest,
    DistillationExportRequest,
    DreamCycleRequest,
    SessionContext,
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexusnet-brain")
    parser.add_argument("--project-root", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("wake", help="Boot the NexusNet brain and print startup telemetry.")

    generate = sub.add_parser("generate", help="Run one prompt through the NexusNet wrapper.")
    generate.add_argument("prompt")
    generate.add_argument("--model", default=None)
    generate.add_argument("--expert", default=None)
    generate.add_argument("--session-id", default="brain-cli-session")

    bench = sub.add_parser("benchmark-smoke", help="Run a deterministic smoke benchmark through NexusNet.")
    bench.add_argument("--model", default="mock/default")

    reflect = sub.add_parser("reflect", help="Summarize recent traces and critiques.")
    reflect.add_argument("--limit", type=int, default=25)

    dream = sub.add_parser("dream", help="Run one shadow dream cycle.")
    dream.add_argument("--trace-id", default=None)
    dream.add_argument("--seed", default=None)
    dream.add_argument("--model", default=None)
    dream.add_argument("--variants", type=int, default=3)

    assess = sub.add_parser("curriculum-assess", help="Run one curriculum assessment phase.")
    assess.add_argument("--phase", default="foundation", choices=["foundation", "graduate", "doctoral", "faculty"])
    assess.add_argument("--subject", default="general")
    assess.add_argument("--model", default="mock/default")

    transcript = sub.add_parser("curriculum-transcript", help="Print curriculum transcript records.")
    transcript.add_argument("--subject", default=None)
    transcript.add_argument("--limit", type=int, default=50)

    distill = sub.add_parser("distill-export", help="Export a distillation dataset from traces and dream artifacts.")
    distill.add_argument("name")
    distill.add_argument("--trace-limit", type=int, default=100)
    distill.add_argument("--no-dreams", action="store_true")
    distill.add_argument("--no-curriculum", action="store_true")

    args = parser.parse_args()
    services = build_services(args.project_root)

    if args.command == "wake":
        print(json.dumps(services.brain.wake(), indent=2))
        return

    if args.command == "generate":
        result = services.brain.generate(
            session_context=SessionContext(session_id=args.session_id, expert=args.expert, task_type="cli"),
            prompt=args.prompt,
            model_hint=args.model,
        )
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return

    if args.command == "benchmark-smoke":
        run = services.brain.run_benchmark(
            suite_name="smoke",
            model_hint=args.model,
            cases=[
                BenchmarkCase(
                    prompt="State that NexusNet is the neural wrapper/core.",
                    expected_substrings=["nexusnet", "wrapper"],
                    model_hint=args.model,
                )
            ],
        )
        print(json.dumps(run.model_dump(mode="json"), indent=2))
        return

    if args.command == "reflect":
        print(json.dumps(services.brain_reflection.summarize(limit=args.limit).model_dump(mode="json"), indent=2))
        return

    if args.command == "dream":
        episode = services.brain_dreaming.run_cycle(
            brain=services.brain,
            request=DreamCycleRequest(trace_id=args.trace_id, seed=args.seed, model_hint=args.model, variant_count=args.variants),
        )
        print(json.dumps(episode.model_dump(mode="json"), indent=2))
        return

    if args.command == "curriculum-assess":
        assessment = services.brain_curriculum.assess(
            brain=services.brain,
            request=CurriculumAssessmentRequest(phase=args.phase, subject=args.subject, model_hint=args.model),
        )
        print(json.dumps(assessment.model_dump(mode="json"), indent=2))
        return

    if args.command == "curriculum-transcript":
        print(json.dumps(services.brain_curriculum.transcript(subject=args.subject, limit=args.limit), indent=2))
        return

    if args.command == "distill-export":
        result = services.brain_distillation.export(
            DistillationExportRequest(
                name=args.name,
                trace_limit=args.trace_limit,
                include_dreams=not args.no_dreams,
                include_curriculum=not args.no_curriculum,
            )
        )
        print(json.dumps(result.model_dump(mode="json"), indent=2))
