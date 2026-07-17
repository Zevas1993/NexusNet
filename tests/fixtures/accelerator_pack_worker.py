import json
import os
from pathlib import Path
import subprocess
import sys
import time


def emit(request_id, event, sequence, terminal, payload=None, reason_code=None):
    frame = {
        "protocol_version": "1.0",
        "request_id": request_id,
        "event": event,
        "sequence": sequence,
        "terminal": terminal,
        "payload": payload or {},
        "reason_code": reason_code,
    }
    sys.stdout.write(json.dumps(frame, separators=(",", ":")) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    request = json.loads(line)
    request_id = request["request_id"]
    operation = request["operation"]
    payload = request.get("payload", {})

    if payload.get("spawn_child"):
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        Path(payload["child_pid_path"]).write_text(str(child.pid), encoding="ascii")
        time.sleep(5)
    elif payload.get("wrong_request_id"):
        emit("request-mismatch", "result", 0, True, {"available": True})
    elif payload.get("bad_sequence"):
        emit(request_id, "accepted", 0, False)
        emit(request_id, "result", 2, True, {"available": True})
    elif payload.get("oversized"):
        sys.stdout.buffer.write(b"private-oversized-output" * 4096)
        sys.stdout.buffer.flush()
        time.sleep(5)
    elif operation == "health":
        emit(request_id, "result", 0, True, {"available": True, "capabilities": {"streaming": True}})
    elif operation == "describe":
        emit(
            request_id,
            "result",
            0,
            True,
            {
                "worker": "fixture",
                "protocol_version": "1.0",
                "private_environment_seen": "NEXUSNET_PRIVATE_TEST" in os.environ,
                "pack_setting": os.environ.get("PACK_SETTING"),
            },
        )
    elif operation == "infer":
        emit(request_id, "accepted", 0, False)
        emit(request_id, "chunk", 1, False, {"text": "worker:"})
        emit(request_id, "result", 2, True, {"text": "worker:" + payload.get("prompt", "")})
    elif operation == "benchmark" and payload.get("hang"):
        time.sleep(5)
    elif operation == "self_test" and payload.get("malformed"):
        sys.stdout.write("not-json-private-output\n")
        sys.stdout.flush()
    elif operation == "shutdown":
        emit(request_id, "result", 0, True, {"stopped": True})
        break
    else:
        emit(request_id, "error", 0, True, reason_code="operation-unsupported")
