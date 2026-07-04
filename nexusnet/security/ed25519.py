from __future__ import annotations

import hashlib
from dataclasses import dataclass

P = 2**255 - 19
Q = 2**252 + 27742317777372353535851937790883648493
D = (-121665 * pow(121666, P - 2, P)) % P
I = pow(2, (P - 1) // 4, P)
IDENTITY = (0, 1)
BASE_POINT = (
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _clamp_scalar(seed_hash_prefix: bytes) -> int:
    value = bytearray(seed_hash_prefix[:32])
    value[0] &= 248
    value[31] &= 63
    value[31] |= 64
    return int.from_bytes(value, "little")


def _point_add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = left
    x2, y2 = right
    xyxy = x1 * x2 * y1 * y2
    x3 = (x1 * y2 + x2 * y1) * pow(1 + D * xyxy, P - 2, P)
    y3 = (y1 * y2 + x1 * x2) * pow(1 - D * xyxy, P - 2, P)
    return x3 % P, y3 % P


def _point_mul(scalar: int, point: tuple[int, int] = BASE_POINT) -> tuple[int, int]:
    result = IDENTITY
    addend = point
    while scalar:
        if scalar & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        scalar >>= 1
    return result


def _encode_point(point: tuple[int, int]) -> bytes:
    x, y = point
    encoded = bytearray(y.to_bytes(32, "little"))
    encoded[31] |= (x & 1) << 7
    return bytes(encoded)


def _recover_x(y: int, sign: int) -> int | None:
    if y >= P:
        return None
    x2 = ((y * y - 1) * pow(D * y * y + 1, P - 2, P)) % P
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = (x * I) % P
    if (x * x - x2) % P != 0:
        return None
    if (x & 1) != sign:
        x = P - x
    return x


def _decode_point(encoded: bytes) -> tuple[int, int] | None:
    if len(encoded) != 32:
        return None
    y_bytes = bytearray(encoded)
    sign = y_bytes[31] >> 7
    y_bytes[31] &= 127
    y = int.from_bytes(y_bytes, "little")
    x = _recover_x(y, sign)
    if x is None:
        return None
    if (-x * x + y * y - 1 - D * x * x * y * y) % P != 0:
        return None
    return x, y


@dataclass(frozen=True)
class Ed25519Keypair:
    seed: bytes
    public_key: bytes

    @classmethod
    def from_seed(cls, seed: bytes) -> "Ed25519Keypair":
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes")
        seed_hash = _sha512(seed)
        public_key = _encode_point(_point_mul(_clamp_scalar(seed_hash)))
        return cls(seed=seed, public_key=public_key)

    @property
    def public_key_hex(self) -> str:
        return self.public_key.hex()

    def sign(self, message: bytes) -> bytes:
        seed_hash = _sha512(self.seed)
        scalar = _clamp_scalar(seed_hash)
        prefix = seed_hash[32:]
        r = int.from_bytes(_sha512(prefix + message), "little") % Q
        encoded_r = _encode_point(_point_mul(r))
        k = int.from_bytes(_sha512(encoded_r + self.public_key + message), "little") % Q
        s = (r + k * scalar) % Q
        return encoded_r + s.to_bytes(32, "little")

    @staticmethod
    def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
        if len(public_key) != 32 or len(signature) != 64:
            return False
        encoded_r = signature[:32]
        s = int.from_bytes(signature[32:], "little")
        if s >= Q:
            return False
        a = _decode_point(public_key)
        r = _decode_point(encoded_r)
        if a is None or r is None:
            return False
        k = int.from_bytes(_sha512(encoded_r + public_key + message), "little") % Q
        return _point_mul(s) == _point_add(r, _point_mul(k, a))
