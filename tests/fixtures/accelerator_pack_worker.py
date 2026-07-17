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


def spawn_child(pid_path):
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    Path(pid_path).write_text(str(child.pid), encoding="ascii")
    return child


if "--no-read" in sys.argv:
    time.sleep(2)
    raise SystemExit(0)

if "--spawn-immediately" in sys.argv:
    argument_index = sys.argv.index("--spawn-immediately")
    spawn_child(sys.argv[argument_index + 1])

if "--spawn-and-exit" in sys.argv:
    argument_index = sys.argv.index("--spawn-and-exit")
    spawn_child(sys.argv[argument_index + 1])
    raise SystemExit(0)


active_request_id = None
for line in sys.stdin:
    request = json.loads(line)
    request_id = request["request_id"]
    operation = request["operation"]
    payload = request.get("payload", {})

    if payload.get("spawn_child"):
        spawn_child(payload["child_pid_path"])
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
    elif payload.get("aggregate_frames"):
        frame_size = payload.get("frame_size", 3000)
        frame_count = payload.get("frame_count", 8)
        for sequence in range(frame_count):
            emit(request_id, "chunk", sequence, False, {"data": "x" * frame_size})
        emit(request_id, "result", frame_count, True, {"complete": True})
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
    elif operation == "infer" and payload.get("await_cancel"):
        active_request_id = request_id
        emit(request_id, "accepted", 0, False)
    elif operation == "infer":
        emit(request_id, "accepted", 0, False)
        emit(request_id, "chunk", 1, False, {"text": "worker:"})
        emit(request_id, "result", 2, True, {"text": "worker:" + payload.get("prompt", "")})
    elif operation == "benchmark" and payload.get("hang"):
        time.sleep(5)
    elif operation == "self_test" and payload.get("malformed"):
        sys.stdout.write("not-json-private-output\n")
        sys.stdout.flush()
    elif operation == "cancel" and active_request_id is not None:
        target_request_id = payload.get("target_request_id")
        if target_request_id == active_request_id:
            emit(active_request_id, "error", 1, True, reason_code="worker-cancelled")
            active_request_id = None
        else:
            emit(request_id, "error", 0, True, reason_code="cancel-target-mismatch")
    elif operation == "shutdown":
        emit(request_id, "result", 0, True, {"stopped": True})
        break
    else:
        emit(request_id, "error", 0, True, reason_code="operation-unsupported")
