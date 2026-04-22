from __future__ import annotations

from typing import Any


def validate_function_call(*, catalog: list[str], payload: dict[str, Any]) -> dict[str, Any]:
    function_name = payload.get("function")
    return {
        "valid": bool(function_name) and function_name in set(catalog),
        "function": function_name,
        "catalog": list(catalog),
    }
