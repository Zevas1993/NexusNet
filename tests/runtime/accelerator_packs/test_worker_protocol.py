from types import MappingProxyType

import pytest
from pydantic import BaseModel, ValidationError

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import (
    JsonLineCodec,
    ProtocolError,
    WorkerFrame,
    WorkerOperation,
    WorkerRequest,
)


def _request(**overrides) -> WorkerRequest:
    payload = {
        "request_id": "request-1",
        "operation": WorkerOperation.HEALTH,
        "deadline_unix_ms": 4_000_000_000_000,
        "sanitized_model_ref": "model::none",
        "workload_profile": {"batch_size": 1},
        "execution_mode": ExecutionMode.AUTO,
        "policy_receipt_ref": "receipt::test",
        "payload": {},
    }
    payload.update(overrides)
    return WorkerRequest.model_validate(payload)


def test_protocol_round_trips_a_versioned_request_and_terminal_result():
    codec = JsonLineCodec(max_frame_bytes=4096)
    request = _request()
    decoded = codec.decode_request(codec.encode(request))
    assert decoded == request

    frame = WorkerFrame(
        request_id=request.request_id,
        event="result",
        sequence=0,
        terminal=True,
        payload={"available": True},
    )
    assert codec.decode_frame(codec.encode(frame)) == frame


def test_protocol_accepts_windows_crlf_and_reencodes_canonical_lf():
    codec = JsonLineCodec(max_frame_bytes=4096)
    encoded = codec.encode(_request())

    decoded = codec.decode_request(encoded[:-1] + b"\r\n")

    assert decoded == _request()
    assert codec.encode(decoded).endswith(b"\n")
    assert not codec.encode(decoded).endswith(b"\r\n")


def test_protocol_rejects_invalid_or_oversized_frames_without_echoing_content():
    codec = JsonLineCodec(max_frame_bytes=32)
    secret = b'{"prompt":"private prompt that must not escape"}\n'
    with pytest.raises(ProtocolError, match="worker-frame-too-large") as oversized:
        codec.decode_frame(secret)
    assert "private prompt" not in str(oversized.value)

    with pytest.raises(ProtocolError, match="worker-frame-invalid") as malformed:
        JsonLineCodec().decode_frame(b"not-json-and-private\n")
    assert "private" not in str(malformed.value)

    with pytest.raises(ValidationError, match="terminal"):
        WorkerFrame(request_id="request-1", event="result", sequence=0, terminal=False, payload={})


@pytest.mark.parametrize(
    "raw",
    [
        b"{}",
        b"{}\r{}\n",
        b"{}\n{}\n",
        b'\xef\xbb\xbf{"request_id":"private"}\n',
        (
            b'{"protocol_version":"1.0","request_id":"request-1","request_id":"request-2",'
            b'"operation":"health","deadline_unix_ms":1,"sanitized_model_ref":"model::none",'
            b'"workload_profile":{},"execution_mode":"auto","policy_receipt_ref":"receipt::test",'
            b'"payload":{}}\n'
        ),
    ],
)
def test_protocol_requires_exactly_one_line_terminated_object_without_duplicate_keys(raw):
    with pytest.raises(ProtocolError, match="worker-frame-invalid"):
        JsonLineCodec().decode_request(raw)


def test_protocol_models_are_deeply_immutable_and_json_bounded():
    request = _request(
        workload_profile={"batch_size": 1, "stream": True},
        payload={"sampling": {"stops": ["one", "two"]}},
    )
    assert isinstance(request.workload_profile, MappingProxyType)
    assert isinstance(request.payload, MappingProxyType)
    assert isinstance(request.payload["sampling"], MappingProxyType)
    assert request.payload["sampling"]["stops"] == ("one", "two")

    with pytest.raises(TypeError):
        request.workload_profile["batch_size"] = 2
    with pytest.raises(TypeError):
        request.payload["sampling"]["temperature"] = 0.5
    with pytest.raises(AttributeError):
        request.payload["sampling"]["stops"].append("tampered")

    nested = "leaf"
    for _ in range(20):
        nested = {"next": nested}
    with pytest.raises(ValidationError, match="payload"):
        _request(payload=nested)


@pytest.mark.parametrize(
    ("marker", "replacement"),
    [
        (b'"payload":{}', b'"payload":{"value":"\\ud800"}'),
        (b'"payload":{}', b'"payload":{"\\udfff":"value"}'),
        (b'"workload_profile":{"batch_size":1}', b'"workload_profile":{"label":"\\ud800"}'),
    ],
)
def test_protocol_rejects_unpaired_unicode_surrogates(marker, replacement):
    codec = JsonLineCodec()
    encoded = codec.encode(_request())

    with pytest.raises(ProtocolError, match="worker-frame-invalid"):
        codec.decode_request(encoded.replace(marker, replacement))


def test_protocol_round_trips_valid_unicode_surrogate_pairs():
    codec = JsonLineCodec()
    encoded = codec.encode(_request())
    encoded = encoded.replace(b'"payload":{}', b'"payload":{"emoji":"\\ud83d\\ude00"}')

    decoded = codec.decode_request(encoded)

    assert decoded.payload["emoji"] == chr(0x1F600)
    assert codec.decode_request(codec.encode(decoded)) == decoded


@pytest.mark.parametrize(
    "override",
    [
        {"operation": b"health"},
        {"execution_mode": b"auto"},
    ],
)
def test_protocol_request_rejects_byte_enum_inputs(override):
    with pytest.raises(ValidationError):
        _request(**override)


@pytest.mark.parametrize(
    "override",
    [
        {"deadline_unix_ms": True},
        {"deadline_unix_ms": "4000000000000"},
        {"request_id": "request\nprivate"},
        {"sanitized_model_ref": "C:/Users/Private/model.gguf"},
        {"policy_receipt_ref": "receipt::private\\path"},
        {"workload_profile": {"batch_size": [1]}},
        {"payload": {"unsupported": {1, 2}}},
        {"payload": {"not_finite": float("nan")}},
    ],
)
def test_protocol_request_rejects_coercive_or_unsanitized_values(override):
    with pytest.raises(ValidationError):
        _request(**override)


@pytest.mark.parametrize(
    "payload",
    [
        {"request_id": "request-1", "event": "error", "sequence": 0, "terminal": True, "payload": {}},
        {
            "request_id": "request-1",
            "event": "error",
            "sequence": 0,
            "terminal": True,
            "reason_code": "C:/Users/Private",
            "payload": {},
        },
        {
            "request_id": "request-1",
            "event": "chunk",
            "sequence": 0,
            "terminal": False,
            "reason_code": "unexpected-reason",
            "payload": {},
        },
        {"request_id": "request-1", "event": "chunk", "sequence": True, "terminal": False, "payload": {}},
    ],
)
def test_protocol_frame_enforces_terminal_reason_and_strict_sequence_semantics(payload):
    with pytest.raises(ValidationError):
        WorkerFrame.model_validate(payload)


def test_codec_rejects_boolean_limits_non_protocol_models_and_mutated_raw_types():
    with pytest.raises(ValueError, match="max_frame_bytes"):
        JsonLineCodec(max_frame_bytes=True)

    class OtherModel(BaseModel):
        private: str

    with pytest.raises(ProtocolError, match="worker-message-type-invalid") as unsupported:
        JsonLineCodec().encode(OtherModel(private="C:/Users/Private"))
    assert "Private" not in str(unsupported.value)

    with pytest.raises(ProtocolError, match="worker-frame-invalid"):
        JsonLineCodec().decode_frame("not-bytes\n")
