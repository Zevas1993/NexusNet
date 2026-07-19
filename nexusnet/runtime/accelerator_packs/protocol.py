from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
import json
import math
import re
from types import MappingProxyType
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    PlainSerializer,
    StrictBool,
    StrictInt,
    StrictStr,
    ValidationError,
    Field,
    field_validator,
    model_validator,
)

from .contracts import ExecutionMode


_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SANITIZED_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
_REASON_CODE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_PROFILE_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
_MAX_JSON_DEPTH = 16
_MAX_JSON_ITEMS = 4096
_MAX_JSON_STRING = 1024 * 1024
_MAX_PROFILE_ITEMS = 128
_MAX_FRAME_LIMIT = 64 * 1024 * 1024
_MAX_INTEGER = 2**63 - 1


class ProtocolError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class WorkerOperation(str, Enum):
    DESCRIBE = "describe"
    HEALTH = "health"
    SELF_TEST = "self_test"
    BENCHMARK = "benchmark"
    LOAD_MODEL = "load_model"
    INFER = "infer"
    UNLOAD_MODEL = "unload_model"
    CANCEL = "cancel"
    SHUTDOWN = "shutdown"


def _contains_unicode_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _freeze_json(value: object, *, depth: int, item_count: list[int]) -> object:
    if depth > _MAX_JSON_DEPTH:
        raise ValueError("JSON value exceeds nesting limit")
    if value is None or type(value) in {bool, int, float, str}:
        if type(value) is int and abs(value) > _MAX_INTEGER:
            raise ValueError("JSON integer exceeds range")
        if type(value) is float and not math.isfinite(value):
            raise ValueError("JSON number must be finite")
        if type(value) is str:
            if len(value) > _MAX_JSON_STRING:
                raise ValueError("JSON string exceeds length limit")
            if _contains_unicode_surrogate(value):
                raise ValueError("JSON string contains an unpaired Unicode surrogate")
        return value
    if isinstance(value, Mapping):
        item_count[0] += len(value)
        if item_count[0] > _MAX_JSON_ITEMS:
            raise ValueError("JSON object exceeds item limit")
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if (type(key) is not str or not key or len(key) > 256
                    or any(character in "\r\n\x00" for character in key)
                    or _contains_unicode_surrogate(key)):
                raise ValueError("JSON object key is invalid")
            frozen[key] = _freeze_json(item, depth=depth + 1, item_count=item_count)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        item_count[0] += len(value)
        if item_count[0] > _MAX_JSON_ITEMS:
            raise ValueError("JSON array exceeds item limit")
        return tuple(_freeze_json(item, depth=depth + 1, item_count=item_count) for item in value)
    raise ValueError("payload must contain only JSON-compatible values")


def _freeze_json_object(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("payload must be a JSON object")
    frozen = _freeze_json(value, depth=0, item_count=[0])
    if not isinstance(frozen, Mapping):
        raise ValueError("payload must be a JSON object")
    return frozen


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


def _thaw_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _freeze_workload_profile(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or len(value) > _MAX_PROFILE_ITEMS:
        raise ValueError("workload profile is invalid")
    frozen: dict[str, object] = {}
    for key, item in value.items():
        if type(key) is not str or not _PROFILE_KEY.fullmatch(key):
            raise ValueError("workload profile key is invalid")
        if type(item) not in {bool, int, float, str}:
            raise ValueError("workload profile values must be scalar")
        if type(item) is int and abs(item) > _MAX_INTEGER:
            raise ValueError("workload profile integer exceeds range")
        if type(item) is float and not math.isfinite(item):
            raise ValueError("workload profile number must be finite")
        if type(item) is str:
            if len(item) > 256:
                raise ValueError("workload profile string exceeds length limit")
            if _contains_unicode_surrogate(item):
                raise ValueError("workload profile string contains an unpaired Unicode surrogate")
        frozen[key] = item
    return MappingProxyType(frozen)


FrozenJsonObject = Annotated[
    Mapping[StrictStr, Any],
    BeforeValidator(_freeze_json_object),
    AfterValidator(_freeze_mapping),
    PlainSerializer(_thaw_json, return_type=dict),
]
FrozenWorkloadProfile = Annotated[
    Mapping[StrictStr, Any],
    BeforeValidator(_freeze_workload_profile),
    AfterValidator(_freeze_mapping),
    PlainSerializer(_thaw_json, return_type=dict),
]


class WorkerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = "1.0"
    request_id: StrictStr
    operation: WorkerOperation
    deadline_unix_ms: StrictInt = Field(gt=0, le=_MAX_INTEGER)
    sanitized_model_ref: StrictStr
    workload_profile: FrozenWorkloadProfile = Field(default_factory=dict, validate_default=True)
    execution_mode: ExecutionMode
    policy_receipt_ref: StrictStr
    payload: FrozenJsonObject = Field(default_factory=dict, validate_default=True)

    @field_validator("operation", mode="before")
    @classmethod
    def validate_operation_type(cls, value: object) -> object:
        if type(value) is not str and not isinstance(value, WorkerOperation):
            raise ValueError("operation must be a string enum value")
        return value

    @field_validator("execution_mode", mode="before")
    @classmethod
    def validate_execution_mode_type(cls, value: object) -> object:
        if type(value) is not str and not isinstance(value, ExecutionMode):
            raise ValueError("execution_mode must be a string enum value")
        return value

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        if not _REQUEST_ID.fullmatch(value):
            raise ValueError("request_id must be sanitized")
        return value

    @field_validator("sanitized_model_ref", "policy_receipt_ref")
    @classmethod
    def validate_reference(cls, value: str) -> str:
        if not _SANITIZED_REF.fullmatch(value):
            raise ValueError("reference must be sanitized")
        return value


class WorkerFrame(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = "1.0"
    request_id: StrictStr
    event: Literal["accepted", "chunk", "result", "error"]
    sequence: StrictInt = Field(ge=0, le=_MAX_INTEGER)
    terminal: StrictBool = False
    payload: FrozenJsonObject = Field(default_factory=dict, validate_default=True)
    reason_code: StrictStr | None = None

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        if not _REQUEST_ID.fullmatch(value):
            raise ValueError("request_id must be sanitized")
        return value

    @field_validator("reason_code")
    @classmethod
    def validate_reason_code(cls, value: str | None) -> str | None:
        if value is not None and not _REASON_CODE.fullmatch(value):
            raise ValueError("reason_code must be sanitized")
        return value

    @model_validator(mode="after")
    def validate_terminal_semantics(self) -> "WorkerFrame":
        if self.event in {"result", "error"} and not self.terminal:
            raise ValueError("result and error frames must be terminal")
        if self.event in {"accepted", "chunk"} and self.terminal:
            raise ValueError("accepted and chunk frames cannot be terminal")
        if self.event == "error" and not self.reason_code:
            raise ValueError("error frames require a reason_code")
        if self.event != "error" and self.reason_code is not None:
            raise ValueError("only error frames can carry a reason_code")
        return self


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    decoded: dict[str, object] = {}
    for key, value in pairs:
        if key in decoded:
            raise ValueError("duplicate JSON key")
        decoded[key] = value
    return decoded


def _reject_json_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant")


class JsonLineCodec:
    def __init__(self, *, max_frame_bytes: int = 4 * 1024 * 1024):
        if type(max_frame_bytes) is not int or not 0 < max_frame_bytes <= _MAX_FRAME_LIMIT:
            raise ValueError("max_frame_bytes must be a bounded positive integer")
        self.max_frame_bytes = max_frame_bytes

    def encode(self, message: WorkerRequest | WorkerFrame) -> bytes:
        if type(message) not in {WorkerRequest, WorkerFrame}:
            raise ProtocolError("worker-message-type-invalid")
        try:
            encoded = (message.model_dump_json() + "\n").encode("utf-8")
        except (UnicodeError, ValueError, TypeError):
            raise ProtocolError("worker-frame-invalid") from None
        if len(encoded) > self.max_frame_bytes:
            raise ProtocolError("worker-frame-too-large")
        return encoded

    def decode_request(self, raw: bytes) -> WorkerRequest:
        return self._decode(raw, WorkerRequest)

    def decode_frame(self, raw: bytes) -> WorkerFrame:
        return self._decode(raw, WorkerFrame)

    def _decode(self, raw: bytes, model_type):
        if type(raw) is not bytes:
            raise ProtocolError("worker-frame-invalid")
        if len(raw) > self.max_frame_bytes:
            raise ProtocolError("worker-frame-too-large")
        try:
            if not raw or not raw.endswith(b"\n") or raw.count(b"\n") != 1:
                raise ValueError("invalid JSON-lines framing")
            body = raw[:-1]
            if body.endswith(b"\r"):
                body = body[:-1]
            if not body or b"\r" in body:
                raise ValueError("invalid JSON-lines framing")
            text = body.decode("utf-8")
            decoded = json.loads(
                text,
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_json_constant,
            )
            if not isinstance(decoded, dict):
                raise ValueError("worker frame must be an object")
            return model_type.model_validate(decoded)
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            ValidationError,
            RecursionError,
            OverflowError,
            ValueError,
            TypeError,
        ):
            raise ProtocolError("worker-frame-invalid") from None
