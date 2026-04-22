from __future__ import annotations

import re
import uuid
from pathlib import Path

import pytest


_NODE_ID_SANITIZER = re.compile(r"[^A-Za-z0-9_.-]+")


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Path:
    root = Path(__file__).resolve().parents[1] / "runtime" / "test-fixtures"
    root.mkdir(parents=True, exist_ok=True)
    label = _NODE_ID_SANITIZER.sub("-", request.node.nodeid).strip("-") or "test"
    path = root / f"{label}-{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path
