from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path

import pytest


_NODE_ID_SANITIZER = re.compile(r"[^A-Za-z0-9_.-]+")
_MAX_NODE_LABEL_LENGTH = 64


def _bounded_node_label(nodeid: str) -> str:
    label = _NODE_ID_SANITIZER.sub("-", nodeid).strip("-") or "test"
    if len(label) <= _MAX_NODE_LABEL_LENGTH:
        return label
    digest = hashlib.sha256(nodeid.encode("utf-8")).hexdigest()[:8]
    prefix_length = _MAX_NODE_LABEL_LENGTH - len(digest) - 1
    return f"{label[:prefix_length]}-{digest}"


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Path:
    root = Path(__file__).resolve().parents[1] / "runtime" / "test-fixtures"
    root.mkdir(parents=True, exist_ok=True)
    label = _bounded_node_label(request.node.nodeid)
    path = root / f"{label}-{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path
