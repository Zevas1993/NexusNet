"""Byte-level tokenizer for the NexusNet language model.

Dependency-free and lossless: every UTF-8 byte (0-255) is a token, plus reserved specials. Any string
round-trips exactly (encode -> decode == identity). This is the input contract the birthed model
trains and generates against; a learned BPE can replace it later behind the same interface.
"""
from __future__ import annotations

PAD, BOS, EOS = 256, 257, 258
SPECIALS = {"<pad>": PAD, "<bos>": BOS, "<eos>": EOS}
VOCAB_SIZE = 259


class ByteTokenizer:
    vocab_size = VOCAB_SIZE
    pad_id = PAD
    bos_id = BOS
    eos_id = EOS

    def encode(self, text: str, *, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        ids = list(text.encode("utf-8"))
        if add_bos:
            ids = [BOS] + ids
        if add_eos:
            ids = ids + [EOS]
        return ids

    def decode(self, ids: list[int]) -> str:
        body = bytes(i for i in ids if i < 256)
        return body.decode("utf-8", errors="replace")
