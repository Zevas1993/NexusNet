from __future__ import annotations

import argparse
import json

from ..api.app import create_app
from ..services import build_services


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run the canonical Nexus API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    sub.add_parser("doctor", help="Run the Nexus preflight health check")
    sub.add_parser("models", help="List registered models")
    sub.add_parser("runtimes", help="List runtime profiles")
    sub.add_parser("manifest", help="Print the workspace manifest")

    args = parser.parse_args()
    if args.command == "serve":
        from uvicorn import run

        run(create_app(), host=args.host, port=args.port)
        return

    services = build_services()
    if args.command == "doctor":
        print(json.dumps(services.doctor_report(), indent=2))
    elif args.command == "models":
        print(json.dumps([model.model_dump(mode="json") for model in services.model_registry.list_models()], indent=2))
    elif args.command == "runtimes":
        print(json.dumps([profile.model_dump(mode="json") for profile in services.runtime_registry.list_profiles()], indent=2))
    elif args.command == "manifest":
        print(services.workspace_manifest())
