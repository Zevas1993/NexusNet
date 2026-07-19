from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


APP_TARGET = "nexus.api.app:app"
BOOT_MANIFEST_SCHEMA = "nexusnet-release-wrapper-boot-manifest-v1"
BOOT_SURFACE_ID = "release-wrapper-boot-supervisor"
DEFAULT_BOOT_MANIFEST = "artifacts/release-wrapper-runtime/boot-manifest.json"
DEFAULT_BOOT_READINESS_COMMAND = (
    "pytest tests/test_release_wrapper_cli.py::test_release_wrapper_cli_is_registered_as_console_script -q"
)
BOOT_SMOKE_PROMPT = (
    "Release wrapper boot smoke: verify live wrapper path, forward-pass coverage, "
    "federation packet, and readiness runner without raw content in evidence."
)


def _add_server_args(parser: argparse.ArgumentParser, *, default_port: int) -> None:
    parser.add_argument("--host", default="127.0.0.1", help="Host interface for the release wrapper server.")
    parser.add_argument("--port", type=int, default=default_port, help="Port for the release wrapper server; 0 selects an available port.")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload for local development.")
    parser.add_argument("--log-level", default="warning", help="Uvicorn log level.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexusnet-wrapper",
        description="Boot the NexusNet release wrapper product surface.",
    )
    _add_server_args(parser, default_port=8765)
    subparsers = parser.add_subparsers(dest="command")
    boot = subparsers.add_parser(
        "boot",
        help="Start the API, smoke the release wrapper, and write boot evidence.",
    )
    _add_server_args(boot, default_port=0)
    boot.add_argument("--project-root", default=".", help="Project root used as the uvicorn subprocess cwd.")
    boot.add_argument("--manifest", default=DEFAULT_BOOT_MANIFEST, help="Path for the sanitized boot manifest.")
    boot.add_argument("--timeout-seconds", type=int, default=90, help="Total boot/smoke timeout.")
    boot.add_argument("--request-timeout-seconds", type=int, default=15, help="Per-request timeout.")
    boot.add_argument("--session-id", default="", help="Optional wrapper session id for the boot smoke.")
    boot.add_argument("--model", default="nexusnet-offline", help="Model id used for the wrapper smoke chat.")
    boot.add_argument(
        "--readiness-command",
        default=DEFAULT_BOOT_READINESS_COMMAND,
        help="Allowlisted pytest command passed to the release-readiness runner.",
    )
    boot.add_argument("--exit-after-smoke", action="store_true", help="Stop the API after boot evidence is written.")
    return parser


def main(
    argv: list[str] | None = None,
    *,
    uvicorn_run: Callable[..., Any] | None = None,
    process_factory: Callable[..., Any] | None = None,
    http_client: Any | None = None,
    sleep: Callable[[float], None] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "boot":
        return _run_boot_supervisor(
            args,
            process_factory=process_factory,
            http_client=http_client,
            sleep=sleep,
        )
    if uvicorn_run is None:
        import uvicorn

        uvicorn_run = uvicorn.run
    base_url = f"http://{args.host}:{args.port}"
    print("NexusNet release wrapper")
    print(f"Wrapper: {base_url}/ui/wrapper/")
    print(f"Release runtime: {base_url}/ops/wrapper/release-runtime")
    print(f"Control panel: {base_url}/ui/control-panel/")
    uvicorn_run(
        APP_TARGET,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
    return 0


def _run_boot_supervisor(
    args: argparse.Namespace,
    *,
    process_factory: Callable[..., Any] | None,
    http_client: Any | None,
    sleep: Callable[[float], None] | None,
) -> int:
    project_root = Path(args.project_root).resolve()
    port = _resolve_port(args.host, int(args.port))
    base_url = f"http://{args.host}:{port}"
    session_id = str(args.session_id or f"release-wrapper-boot-{uuid.uuid4().hex[:12]}")
    request_timeout = max(1, int(args.request_timeout_seconds or 15))
    timeout_seconds = max(1, int(args.timeout_seconds or 90))
    sleep_fn = sleep or time.sleep
    client = http_client or _requests_client()
    process = _start_api_process(
        host=args.host,
        port=port,
        reload=bool(args.reload),
        log_level=str(args.log_level),
        project_root=project_root,
        process_factory=process_factory,
    )
    checks: list[dict[str, Any]] = []
    try:
        _wait_for_api(
            base_url=base_url,
            process=process,
            http_client=client,
            request_timeout=request_timeout,
            timeout_seconds=timeout_seconds,
            sleep=sleep_fn,
            checks=checks,
        )
        evidence = _run_release_wrapper_smoke(
            base_url=base_url,
            session_id=session_id,
            model=str(args.model),
            readiness_command=str(args.readiness_command),
            http_client=client,
            request_timeout=request_timeout,
            readiness_timeout=timeout_seconds,
            checks=checks,
        )
        manifest = _boot_manifest(
            status="boot-smoke-passed",
            base_url=base_url,
            host=args.host,
            port=port,
            process=process,
            session_id=session_id,
            readiness_command=str(args.readiness_command),
            checks=checks,
            evidence=evidence,
        )
        manifest_path = _write_manifest(args.manifest, project_root=project_root, manifest=manifest)
        print("NexusNet release wrapper boot supervisor")
        print(f"Wrapper: {base_url}/ui/wrapper/")
        print(f"Release runtime: {base_url}/ops/wrapper/release-runtime")
        print(f"Boot manifest: {manifest_path}")
        if args.exit_after_smoke:
            _terminate_process(process)
            return 0
        return _wait_for_process(process)
    except Exception as exc:
        manifest = _boot_manifest(
            status="boot-smoke-blocked",
            base_url=base_url,
            host=args.host,
            port=port,
            process=process,
            session_id=session_id,
            readiness_command=str(args.readiness_command),
            checks=checks,
            evidence={"error": type(exc).__name__, "error_digest": _digest_ref(str(exc))},
        )
        _write_manifest(args.manifest, project_root=project_root, manifest=manifest)
        _terminate_process(process)
        print(f"Release wrapper boot smoke blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


def _start_api_process(
    *,
    host: str,
    port: int,
    reload: bool,
    log_level: str,
    project_root: Path,
    process_factory: Callable[..., Any] | None,
) -> Any:
    command = [
        _python_executable(),
        "-m",
        "uvicorn",
        APP_TARGET,
        "--host",
        host,
        "--port",
        str(port),
        "--log-level",
        log_level,
    ]
    if reload:
        command.append("--reload")
    factory = process_factory or subprocess.Popen
    env = os.environ.copy()
    env["NEXUSNET_PROJECT_ROOT"] = str(project_root)
    source_root = str(Path(__file__).resolve().parents[2])
    pythonpath_parts = [part for part in env.get("PYTHONPATH", "").split(os.pathsep) if part]
    if source_root not in pythonpath_parts:
        env["PYTHONPATH"] = os.pathsep.join([source_root, *pythonpath_parts])
    return factory(
        command,
        cwd=str(project_root),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_api(
    *,
    base_url: str,
    process: Any,
    http_client: Any,
    request_timeout: int,
    timeout_seconds: int,
    sleep: Callable[[float], None],
    checks: list[dict[str, Any]],
) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        if _process_returncode(process) is not None:
            raise RuntimeError(f"release wrapper API exited during boot with code {_process_returncode(process)}")
        try:
            response = _http_get(http_client, f"{base_url}/health", timeout=request_timeout)
            payload = response.json()
            if response.status_code < 400 and bool(payload.get("ok", True)):
                checks.append(_check("api-health", "pass", "/health", "API health endpoint responded"))
                return
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        sleep(0.25)
    checks.append(_check("api-health", "fail", "/health", "API health endpoint did not respond", blocker=last_error))
    raise TimeoutError(f"release wrapper API did not become healthy within {timeout_seconds}s")


def _run_release_wrapper_smoke(
    *,
    base_url: str,
    session_id: str,
    model: str,
    readiness_command: str,
    http_client: Any,
    request_timeout: int,
    readiness_timeout: int,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    wrapper_response = _http_get(http_client, f"{base_url}/ui/wrapper/", timeout=request_timeout)
    if wrapper_response.status_code >= 400 or "NexusNet" not in str(wrapper_response.text):
        checks.append(_check("wrapper-ui", "fail", "/ui/wrapper/", "Wrapper UI did not render"))
        raise RuntimeError("wrapper UI smoke failed")
    checks.append(_check("wrapper-ui", "pass", "/ui/wrapper/", "Wrapper UI rendered"))

    models = _json_get(http_client, f"{base_url}/v1/models", timeout=request_timeout)
    model_ids = [str(item.get("id")) for item in models.get("data", []) if isinstance(item, dict)]
    if model not in model_ids:
        checks.append(_check("models", "fail", "/v1/models", "Requested smoke model was not advertised"))
        raise RuntimeError(f"smoke model {model!r} not present in /v1/models")
    checks.append(_check("models", "pass", "/v1/models", "Model registry advertised the smoke model"))

    chat_payload = _json_post(
        http_client,
        f"{base_url}/v1/chat/completions",
        timeout=request_timeout,
        json={
            "session_id": session_id,
            "model": model,
            "messages": [{"role": "user", "content": BOOT_SMOKE_PROMPT}],
        },
    )
    nexusnet_meta = chat_payload.get("nexusnet") if isinstance(chat_payload.get("nexusnet"), dict) else {}
    if nexusnet_meta.get("status") != "ok":
        checks.append(_check("wrapper-chat", "fail", "/v1/chat/completions", "Wrapper chat did not return ok status"))
        raise RuntimeError("wrapper chat smoke failed")
    checks.append(_check("wrapper-chat", "pass", "/v1/chat/completions", "Wrapper chat returned ok status"))

    runtime = _json_get(http_client, _session_url(base_url, "/ops/wrapper/release-runtime", session_id), timeout=request_timeout)
    coverage = runtime.get("forward_pass_coverage") if isinstance(runtime.get("forward_pass_coverage"), dict) else {}
    latest_receipt = coverage.get("latest_receipt") if isinstance(coverage.get("latest_receipt"), dict) else {}
    if coverage.get("latest_status") != "covered" or latest_receipt.get("raw_content_included") is not False:
        checks.append(_check("forward-pass-coverage", "fail", "/ops/wrapper/release-runtime", "Forward-pass coverage was not covered and sanitized"))
        raise RuntimeError("forward-pass coverage smoke failed")
    checks.append(_check("forward-pass-coverage", "pass", "/ops/wrapper/release-runtime", "Forward-pass coverage receipt is covered and sanitized"))

    peer_federation = _run_peer_federation_import_smoke(
        base_url=base_url,
        session_id=session_id,
        runtime=runtime,
        http_client=http_client,
        request_timeout=request_timeout,
        checks=checks,
    )
    runtime = _json_get(http_client, _session_url(base_url, "/ops/wrapper/release-runtime", session_id), timeout=request_timeout)

    approval_status_card = _json_get(
        http_client,
        _session_url(base_url, "/ops/wrapper/status-card", session_id),
        timeout=request_timeout,
    )
    operator_action_lane = (
        approval_status_card.get("operator_action_lane")
        if isinstance(approval_status_card.get("operator_action_lane"), dict)
        else {}
    )
    proposal_update_id = str(operator_action_lane.get("proposal_update_id") or "").strip()
    if not proposal_update_id:
        checks.append(
            _check(
                "readiness-approval",
                "fail",
                "/ops/wrapper/status-card",
                "Readiness proposal did not expose an update id for stored approval",
            )
        )
        raise RuntimeError("release readiness proposal update id is unavailable")
    approval = _json_post(
        http_client,
        f"{base_url}/ops/approvals",
        timeout=request_timeout,
        json={
            "subject": "release-wrapper-autonomous-update",
            "decision": "approved",
            "approver": "release-wrapper-boot-supervisor@example.invalid",
            "rationale": "Approve the operator-invoked boot smoke sandbox lifecycle.",
            "metadata": {"update_id": proposal_update_id},
        },
    )
    approval_decision_id = str(approval.get("decision_id") or "").strip()
    if not approval_decision_id:
        checks.append(
            _check(
                "readiness-approval",
                "fail",
                "/ops/approvals",
                "Stored readiness approval did not return a decision id",
            )
        )
        raise RuntimeError("release readiness stored approval was not created")
    checks.append(
        _check(
            "readiness-approval",
            "pass",
            "/ops/approvals",
            "Stored approval is bound to the readiness proposal update id",
        )
    )

    runner = _json_post(
        http_client,
        f"{base_url}/ops/wrapper/release-readiness/run",
        timeout=max(request_timeout, readiness_timeout),
        json={
            "session_id": session_id,
            "update_id": proposal_update_id,
            "command": readiness_command,
            "timeout_seconds": readiness_timeout,
            "approval_decision_id": approval_decision_id,
        },
    )
    if runner.get("status") != "completed" or runner.get("active_production_mutated") is not False:
        checks.append(_check("readiness-runner", "fail", "/ops/wrapper/release-readiness/run", "Readiness runner did not complete inside the safe boundary"))
        raise RuntimeError("release readiness runner smoke failed")
    checks.append(_check("readiness-runner", "pass", "/ops/wrapper/release-readiness/run", "Readiness runner completed with rollback evidence"))

    readiness = _json_get(http_client, _session_url(base_url, "/ops/wrapper/release-readiness", session_id), timeout=request_timeout)
    if readiness.get("go_no_go") != "go":
        checks.append(_check("release-readiness", "fail", "/ops/wrapper/release-readiness", "Release readiness did not report go"))
        raise RuntimeError("release readiness smoke failed")
    checks.append(_check("release-readiness", "pass", "/ops/wrapper/release-readiness", "Release readiness reports go"))

    status_card = _json_get(http_client, _session_url(base_url, "/ops/wrapper/status-card", session_id), timeout=request_timeout)
    checks.append(_check("status-card", "pass", "/ops/wrapper/status-card", "Status card fetched after boot smoke"))
    production_approval = _json_post(
        http_client,
        f"{base_url}/ops/approvals",
        timeout=request_timeout,
        json={
            "subject": "release-wrapper-production-spine-release-lifecycle",
            "decision": "approved",
            "approver": "release-wrapper-boot-supervisor@example.invalid",
            "rationale": "Approve the operator-invoked product smoke shadow lifecycle.",
            "metadata": {"session_id": session_id},
        },
    )
    production_approval_decision_id = str(production_approval.get("decision_id") or "").strip()
    if not production_approval_decision_id:
        checks.append(
            _check(
                "product-smoke-approval",
                "fail",
                "/ops/approvals",
                "Stored product smoke shadow-lifecycle approval did not return a decision id",
            )
        )
        raise RuntimeError("release product smoke stored approval was not created")
    checks.append(
        _check(
            "product-smoke-approval",
            "pass",
            "/ops/approvals",
            "Stored approval is bound to the product smoke shadow lifecycle",
        )
    )
    product_smoke = _json_post(
        http_client,
        f"{base_url}/ops/wrapper/release-product-smoke/run",
        timeout=max(request_timeout, readiness_timeout * 3),
        json={
            "session_id": session_id,
            "base_url": base_url,
            "readiness_command": readiness_command,
            "timeout_seconds": readiness_timeout,
            "update_id": proposal_update_id,
            "approval_decision_id": approval_decision_id,
            "production_approval_decision_id": production_approval_decision_id,
        },
    )
    successful_product_smoke_statuses = {
        "release-product-smoke-passed",
        "release-product-smoke-governed-update-completed",
        "release-product-smoke-governed-shadow-lifecycle-completed",
    }
    if (
        product_smoke.get("status") not in successful_product_smoke_statuses
        or int(product_smoke.get("failed_count") or 0) != 0
        or product_smoke.get("raw_content_included") is not False
        or product_smoke.get("active_production_mutated") is not False
    ):
        checks.append(
            _check(
                "release-product-smoke",
                "fail",
                "/ops/wrapper/release-product-smoke/run",
                "Live release product smoke did not produce sanitized pass evidence",
            )
        )
        raise RuntimeError("release product smoke failed")
    checks.append(
        _check(
            "release-product-smoke",
            "pass",
            "/ops/wrapper/release-product-smoke/run",
            "Live release product smoke produced sanitized whole-system gate evidence",
        )
    )
    runtime = _json_get(http_client, _session_url(base_url, "/ops/wrapper/release-runtime", session_id), timeout=request_timeout)
    readiness = _json_get(http_client, _session_url(base_url, "/ops/wrapper/release-readiness", session_id), timeout=request_timeout)
    status_card = _json_get(http_client, _session_url(base_url, "/ops/wrapper/status-card", session_id), timeout=request_timeout)
    product_path = _release_product_path_evidence(
        runtime=runtime,
        status_card=status_card,
        product_smoke=product_smoke,
    )
    if not _release_product_path_is_evidenced(product_path):
        checks.append(
            _check(
                "release-product-path",
                "fail",
                "/ops/wrapper/status-card",
                "Release wrapper boot evidence did not include the full product path",
            )
        )
        raise RuntimeError("release wrapper product path evidence smoke failed")
    checks.append(
        _check(
            "release-product-path",
            "pass",
            "/ops/wrapper/status-card",
            "Release wrapper boot evidence covers growth, federation, dream/research, admin apply, rollback, and failure-learning status",
        )
    )

    runner_summary = (
        readiness.get("evidence", {}).get("release_readiness_evidence_runner")
        if isinstance(readiness.get("evidence"), dict)
        else {}
    )
    if not isinstance(runner_summary, dict):
        runner_summary = {}
    return {
        "models": {"count": len(model_ids), "smoke_model_ref": _digest_ref(model)},
        "chat": {
            "status": "ok",
            "release_runtime_ref": nexusnet_meta.get("release_runtime_ref") or "/ops/wrapper/release-runtime",
        },
        "forward_pass_coverage": {
            "latest_status": coverage.get("latest_status"),
            "receipt_count": int(coverage.get("receipt_count") or 0),
            "latest_receipt_id": latest_receipt.get("receipt_id"),
            "raw_content_included": False,
        },
        "release_readiness_evidence_runner": {
            "latest_status": runner_summary.get("latest_status") or runner.get("status"),
            "latest_run_id": (runner_summary.get("latest_run") or {}).get("run_id") if isinstance(runner_summary.get("latest_run"), dict) else runner.get("run_id"),
            "active_production_mutated": bool(runner.get("active_production_mutated")),
            "artifact_ref": _digest_ref(str(runner.get("artifact_path") or "")),
        },
        "release_readiness": {
            "go_no_go": readiness.get("go_no_go"),
            "blocker_count": len(readiness.get("blockers") or []),
        },
        "release_product_smoke": _release_product_smoke_evidence(product_smoke),
        "peer_federation_reject": _peer_federation_import_evidence(peer_federation.get("reject")),
        "peer_federation_import": _peer_federation_import_evidence(peer_federation.get("import")),
        "status_card": {
            "surface_id": status_card.get("surface_id"),
            "honest_status_label": status_card.get("honest_status_label"),
        },
        "release_product_path": product_path,
    }


def _boot_manifest(
    *,
    status: str,
    base_url: str,
    host: str,
    port: int,
    process: Any,
    session_id: str,
    readiness_command: str,
    checks: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": BOOT_MANIFEST_SCHEMA,
        "surface_id": BOOT_SURFACE_ID,
        "manifest_id": f"release-wrapper-boot::{_digest_ref(base_url + str(time.time())).split(':', 1)[1]}",
        "generated_at": _iso_now(),
        "authority": "NexusBrain",
        "status_label": "LOCKED CANON",
        "status": status,
        "product_surface": "wrapper",
        "base_url": base_url,
        "server": {
            "host": host,
            "port": port,
            "pid": int(getattr(process, "pid", 0) or 0),
            "app_target": APP_TARGET,
        },
        "session_ref_digest": _digest_ref(session_id),
        "readiness_command_ref": _digest_ref(readiness_command),
        "endpoints": {
            "wrapper": f"{base_url}/ui/wrapper/",
            "control_panel": f"{base_url}/ui/control-panel/",
            "visualizer": f"{base_url}/ui/visualizer/",
            "models": f"{base_url}/v1/models",
            "chat_completions": f"{base_url}/v1/chat/completions",
            "release_runtime": f"{base_url}/ops/wrapper/release-runtime",
            "release_readiness": f"{base_url}/ops/wrapper/release-readiness",
            "release_readiness_runner": f"{base_url}/ops/wrapper/release-readiness/run",
            "release_product_smoke_run": f"{base_url}/ops/wrapper/release-product-smoke/run",
            "status_card": f"{base_url}/ops/wrapper/status-card",
            "federated_packet_import": f"{base_url}/ops/wrapper/federated-packets/import",
            "federated_packet_imports": f"{base_url}/ops/wrapper/federated-packets/imports",
        },
        "checks": list(checks),
        "evidence": evidence,
        "raw_content_included": False,
        "privacy_boundary": "sanitized-boot-refs-status-counts-digests-only-no-raw-prompts-outputs-session-ids",
    }


def _write_manifest(path_value: str, *, project_root: Path, manifest: dict[str, Any]) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = project_root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _run_peer_federation_import_smoke(
    *,
    base_url: str,
    session_id: str,
    runtime: dict[str, Any],
    http_client: Any,
    request_timeout: int,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    packet = runtime.get("latest_federated_packet") if isinstance(runtime.get("latest_federated_packet"), dict) else {}
    if not packet:
        checks.append(
            _check(
                "federated-peer-import",
                "fail",
                "/ops/wrapper/federated-packets/import",
                "No sanitized federated packet was available for peer import smoke",
            )
        )
        raise RuntimeError("peer federation import smoke missing packet")
    if packet.get("raw_content_included") is not False or packet.get("contains_personal_data") is not False:
        checks.append(
            _check(
                "federated-peer-import",
                "fail",
                "/ops/wrapper/federated-packets/import",
                "Latest federated packet was not sanitized before peer import smoke",
            )
        )
        raise RuntimeError("peer federation import smoke found unsanitized packet")

    rejected = _json_post(
        http_client,
        f"{base_url}/ops/wrapper/federated-packets/import",
        timeout=request_timeout,
        json={
            "session_id": session_id,
            "peer_node_id": f"release-wrapper-boot-peer-reject::{_digest_ref(session_id)}",
            "packet": _rejected_peer_federation_probe_packet(packet),
        },
    )
    if not _peer_federation_import_is_rejected(rejected):
        checks.append(
            _check(
                "federated-peer-reject",
                "fail",
                "/ops/wrapper/federated-packets/import",
                "Unsafe peer federated packet was not rejected before shadow learning",
            )
        )
        raise RuntimeError("peer federation reject smoke failed")
    checks.append(
        _check(
            "federated-peer-reject",
            "pass",
            "/ops/wrapper/federated-packets/import",
            "Unsafe peer federated packet rejected without learning side effects",
        )
    )

    imported = _json_post(
        http_client,
        f"{base_url}/ops/wrapper/federated-packets/import",
        timeout=request_timeout,
        json={
            "session_id": session_id,
            "peer_node_id": f"release-wrapper-boot-peer::{_digest_ref(session_id)}",
            "packet": packet,
        },
    )
    if not _peer_federation_import_is_accepted(imported):
        checks.append(
            _check(
                "federated-peer-import",
                "fail",
                "/ops/wrapper/federated-packets/import",
                "Peer federated packet import was not accepted into shadow quarantine",
            )
        )
        raise RuntimeError("peer federation import smoke failed")
    checks.append(
        _check(
            "federated-peer-import",
            "pass",
            "/ops/wrapper/federated-packets/import",
            "Peer federated packet accepted into sanitized shadow quarantine",
        )
    )

    inbox = _json_get(
        http_client,
        _session_url(base_url, "/ops/wrapper/federated-packets/imports", session_id),
        timeout=request_timeout,
    )
    latest_import = inbox.get("latest_import") if isinstance(inbox.get("latest_import"), dict) else {}
    if (
        inbox.get("raw_content_included") is not False
        or inbox.get("contains_personal_data") is not False
        or inbox.get("active_production_mutation_allowed") is not False
        or _int_value(inbox.get("accepted_import_count")) < 1
        or _int_value(inbox.get("rejected_import_count")) < 1
        or latest_import.get("import_id") != imported.get("import_id")
    ):
        checks.append(
            _check(
                "federated-peer-inbox",
                "fail",
                "/ops/wrapper/federated-packets/imports",
                "Federated packet inbox did not expose sanitized accepted peer-import evidence",
            )
        )
        raise RuntimeError("peer federation inbox smoke failed")
    checks.append(
        _check(
            "federated-peer-inbox",
            "pass",
            "/ops/wrapper/federated-packets/imports",
            "Federated packet inbox exposed sanitized accepted/rejected counters",
        )
    )
    return {"reject": rejected, "import": imported, "inbox": inbox}


def _peer_federation_import_is_accepted(imported: dict[str, Any]) -> bool:
    return (
        imported.get("status") == "quarantined-shadow-accepted"
        and imported.get("security_envelope_verified") is True
        and imported.get("assimilation_shadow_captured") is True
        and imported.get("global_growth_shadow_captured") is True
        and imported.get("active_production_mutation_allowed") is False
        and imported.get("raw_content_included") is False
        and imported.get("contains_personal_data") is False
    )


def _peer_federation_import_is_rejected(imported: dict[str, Any]) -> bool:
    return (
        imported.get("status") == "quarantined-rejected"
        and imported.get("security_envelope_verified") is False
        and imported.get("assimilation_shadow_captured") is False
        and imported.get("global_growth_shadow_captured") is False
        and imported.get("active_production_mutation_allowed") is False
        and imported.get("raw_content_included") is False
        and imported.get("contains_personal_data") is False
    )


def _rejected_peer_federation_probe_packet(packet: dict[str, Any]) -> dict[str, Any]:
    probe = dict(packet)
    probe["packet_id"] = f"{packet.get('packet_id') or 'boot-peer'}::rejection-probe"
    probe["raw_content_included"] = True
    probe["contains_personal_data"] = False
    return probe


def _peer_federation_import_evidence(imported: Any) -> dict[str, Any]:
    payload = imported if isinstance(imported, dict) else {}
    return {
        "status": str(payload.get("status") or "not-run"),
        "import_id": payload.get("import_id") if isinstance(payload.get("import_id"), str) else None,
        "security_envelope_verified": payload.get("security_envelope_verified") is True,
        "assimilation_shadow_captured": payload.get("assimilation_shadow_captured") is True,
        "global_growth_shadow_captured": payload.get("global_growth_shadow_captured") is True,
        "active_production_mutation_allowed": False,
        "raw_content_included": False,
        "contains_personal_data": False,
    }


def _release_product_smoke_evidence(smoke: Any) -> dict[str, Any]:
    payload = smoke if isinstance(smoke, dict) else {}
    failed_count = _int_value(payload.get("failed_count"))
    latest_status = str(payload.get("status") or "not-run")
    successful_statuses = {
        "release-product-smoke-passed",
        "release-product-smoke-governed-update-completed",
        "release-product-smoke-governed-shadow-lifecycle-completed",
    }
    runtime_state = "live-evidence" if latest_status in successful_statuses and failed_count == 0 else "degraded-evidence"
    return {
        "surface_id": str(payload.get("surface_id") or "release-wrapper-product-smoke"),
        "latest_status": latest_status,
        "runtime_state": runtime_state,
        "manifest_id": payload.get("manifest_id") if isinstance(payload.get("manifest_id"), str) else None,
        "manifest_ref": str(payload.get("artifact_ref") or "artifacts/release-wrapper-runtime/release-product-smoke.json"),
        "check_count": _int_value(payload.get("check_count")),
        "pass_count": _int_value(payload.get("pass_count")),
        "failed_count": failed_count,
        "product_surface": str(payload.get("product_surface") or "wrapper"),
        "product_scope": str(payload.get("product_scope") or "whole-system"),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": bool(payload.get("active_production_mutated")),
    }


def _check(check_id: str, status: str, endpoint: str, detail: str, *, blocker: str = "") -> dict[str, Any]:
    record = {
        "check_id": check_id,
        "status": status,
        "endpoint": endpoint,
        "detail": detail,
        "raw_content_included": False,
    }
    if blocker:
        record["blocker_digest"] = _digest_ref(blocker)
    return record


def _release_product_path_evidence(
    *,
    runtime: dict[str, Any],
    status_card: dict[str, Any],
    product_smoke: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entrypoint = _dict_value(runtime, "entrypoint")
    global_growth = _dict_value(runtime, "global_growth")
    federated_packet_inbox = _dict_value(runtime, "federated_packet_inbox")
    production_spine = _dict_value(runtime, "production_spine")
    dream_research = _dict_value(runtime, "dream_research_queue")
    autonomous_updates = _dict_value(runtime, "autonomous_updates")
    runtime_live_telemetry = _dict_value(runtime, "live_wrapper_telemetry")
    status_runtime = _dict_value(status_card, "runtime")
    status_live_telemetry = _dict_value(status_runtime, "live_wrapper_telemetry")
    failure_learning = _dict_value(runtime_live_telemetry, "failure_learning") or _dict_value(
        status_live_telemetry,
        "failure_learning",
    )
    self_repair = (
        _dict_value(status_card, "self_repair_ledger")
        or _dict_value(status_runtime, "self_repair_ledger")
        or _dict_value(runtime, "self_repair_ledger")
    )
    action_lane = (
        _dict_value(status_card, "operator_action_lane")
        or _dict_value(status_card, "admin_action_lane")
        or _dict_value(status_runtime, "operator_action_lane")
        or _dict_value(status_runtime, "admin_action_lane")
    )
    action_statuses = _dict_value(action_lane, "latest_action_statuses")
    governed_lifecycle = _dict_value(product_smoke or {}, "governed_update_lifecycle")
    governed_actions = _dict_value(governed_lifecycle, "actions")
    governed_action_statuses = {
        action: str(_dict_value(governed_actions, action).get("status") or "")
        for action in ("admin_approval", "sandbox_tests", "apply", "rollback")
    }
    if all(governed_action_statuses.values()):
        action_statuses = governed_action_statuses
    return {
        "entrypoint_runtime_state": str(entrypoint.get("runtime_state") or "unknown"),
        "global_growth_users": _int_value(global_growth.get("users")),
        "training_ready_node_count": len(global_growth.get("training_ready_nodes") or []),
        "federated_packet_count": _int_value(runtime.get("federated_packet_count")),
        "federated_import_count": _int_value(federated_packet_inbox.get("import_count")),
        "federated_import_accepted_count": _int_value(federated_packet_inbox.get("accepted_import_count")),
        "federated_import_rejected_count": _int_value(federated_packet_inbox.get("rejected_import_count")),
        "federated_import_degraded_count": _int_value(federated_packet_inbox.get("degraded_import_count")),
        "peer_shadow_proposal_count": _peer_shadow_proposal_count(
            autonomous_updates=autonomous_updates,
            dream_research=dream_research,
        ),
        "production_spine_packet_count": _int_value(production_spine.get("packet_count")),
        "dream_research_item_count": _int_value(dream_research.get("item_count")),
        "dream_research_episode_count": _int_value(dream_research.get("episode_count")),
        "autonomous_update_proposal_count": _int_value(autonomous_updates.get("proposal_count")),
        "self_repair_action_count": _int_value(self_repair.get("repair_count")),
        "latest_self_repair_action": str(self_repair.get("latest_action") or "none"),
        "admin_action_statuses": {
            "admin_approval": str(action_statuses.get("admin_approval") or "pending-admin-approval"),
            "sandbox_tests": str(action_statuses.get("sandbox_tests") or "not-run"),
            "apply": str(action_statuses.get("apply") or "not-applied"),
            "rollback": str(action_statuses.get("rollback") or "not-rolled-back"),
        },
        "failure_learning": {
            "captured_count": _int_value(failure_learning.get("captured_count")),
            "degraded_count": _int_value(failure_learning.get("degraded_count")),
            "latest_status": str(failure_learning.get("latest_status") or "not-run"),
        },
        "active_production_mutation_allowed": False,
        "raw_content_included": False,
    }


def _release_product_path_is_evidenced(product_path: dict[str, Any]) -> bool:
    statuses = product_path.get("admin_action_statuses") if isinstance(product_path.get("admin_action_statuses"), dict) else {}
    return (
        product_path.get("entrypoint_runtime_state") == "live-bound"
        and _int_value(product_path.get("global_growth_users")) >= 1
        and _int_value(product_path.get("federated_packet_count")) >= 1
        and _int_value(product_path.get("federated_import_count")) >= 1
        and _int_value(product_path.get("federated_import_accepted_count")) >= 1
        and _int_value(product_path.get("peer_shadow_proposal_count")) >= 1
        and _int_value(product_path.get("production_spine_packet_count")) >= 1
        and _int_value(product_path.get("dream_research_item_count")) >= 1
        and _int_value(product_path.get("autonomous_update_proposal_count")) >= 1
        and _int_value(product_path.get("self_repair_action_count")) >= 1
        and statuses.get("admin_approval") == "admin-approved"
        and statuses.get("sandbox_tests") == "passed"
        and statuses.get("apply") == "applied-shadow-safe-file"
        and statuses.get("rollback") == "rolled-back"
        and product_path.get("active_production_mutation_allowed") is False
        and product_path.get("raw_content_included") is False
    )


def _peer_shadow_proposal_count(*, autonomous_updates: dict[str, Any], dream_research: dict[str, Any]) -> int:
    count = 0
    proposals = autonomous_updates.get("proposals") if isinstance(autonomous_updates.get("proposals"), list) else []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        metadata = proposal.get("metadata") if isinstance(proposal.get("metadata"), dict) else {}
        safe_payload = metadata.get("safe_payload") if isinstance(metadata.get("safe_payload"), dict) else {}
        if safe_payload.get("peer_shadow_import") is True:
            count += 1
    latest_item = dream_research.get("latest_item") if isinstance(dream_research.get("latest_item"), dict) else {}
    latest_metadata = latest_item.get("metadata") if isinstance(latest_item.get("metadata"), dict) else {}
    if count == 0 and latest_metadata.get("federated_import_shadow") is True:
        return 1
    return count


def _dict_value(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key) if isinstance(mapping, dict) else {}
    return value if isinstance(value, dict) else {}


def _int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _http_get(http_client: Any, url: str, *, timeout: int) -> Any:
    response = http_client.get(url, timeout=timeout)
    response.raise_for_status()
    return response


def _json_get(http_client: Any, url: str, *, timeout: int) -> dict[str, Any]:
    response = _http_get(http_client, url, timeout=timeout)
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def _json_post(http_client: Any, url: str, *, timeout: int, json: dict[str, Any]) -> dict[str, Any]:
    response = http_client.post(url, json=json, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def _session_url(base_url: str, path: str, session_id: str) -> str:
    return f"{base_url}{path}?session_id={quote_plus(session_id)}"


def _resolve_port(host: str, requested_port: int) -> int:
    if requested_port > 0:
        return requested_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _requests_client() -> Any:
    import requests

    return requests


def _process_returncode(process: Any) -> int | None:
    poll = getattr(process, "poll", None)
    if callable(poll):
        return poll()
    return None


def _wait_for_process(process: Any) -> int:
    try:
        wait = getattr(process, "wait", None)
        if callable(wait):
            result = wait()
            return int(result or 0)
        return 0
    except KeyboardInterrupt:
        _terminate_process(process)
        return 130


def _terminate_process(process: Any) -> None:
    if _process_returncode(process) is not None:
        return
    terminate = getattr(process, "terminate", None)
    if callable(terminate):
        terminate()
    wait = getattr(process, "wait", None)
    if callable(wait):
        try:
            wait(timeout=10)
            return
        except TypeError:
            wait()
            return
        except Exception:
            pass
    kill = getattr(process, "kill", None)
    if callable(kill):
        kill()


def _digest_ref(value: str) -> str:
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _python_executable() -> str:
    return sys.executable


if __name__ == "__main__":
    raise SystemExit(main())
