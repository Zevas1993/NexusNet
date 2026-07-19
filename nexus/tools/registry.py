from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable

from ..schemas import ToolManifest


class ToolRegistry:
    def __init__(self):
        self._execution_count = 0
        self._execution_lock = Lock()
        self._concurrent_safe = {"filesystem.readonly"}
        self._manifests = {
            "filesystem.readonly": ToolManifest(
                tool_name="filesystem.readonly",
                permission_class="readonly",
                input_schema={"path": "string"},
                output_schema={"content": "string"},
                timeout_seconds=10,
                sandbox_policy="workspace-read",
                healthcheck={"status": "declared"},
            ),
            "filesystem.write": ToolManifest(
                tool_name="filesystem.write",
                permission_class="write",
                input_schema={"path": "string", "content": "string", "mode": "string"},
                output_schema={"path": "string", "bytes_written": "integer"},
                timeout_seconds=10,
                sandbox_policy="plan-artifact-or-runtime-sandbox-write",
                healthcheck={"status": "declared"},
            ),
            "retrieval.query": ToolManifest(
                tool_name="retrieval.query",
                permission_class="internal",
                input_schema={"query": "string", "top_k": "integer"},
                output_schema={"hits": "array"},
                timeout_seconds=5,
                sandbox_policy="internal-service",
                healthcheck={"status": "declared"},
            ),
            "governance.audit": ToolManifest(
                tool_name="governance.audit",
                permission_class="internal",
                input_schema={"action": "string", "detail": "object"},
                output_schema={"event_id": "string"},
                timeout_seconds=5,
                sandbox_policy="internal-service",
                healthcheck={"status": "declared"},
            ),
        }

    def list(self) -> list[ToolManifest]:
        return list(self._manifests.values())

    def execute(
        self,
        tool_name: str,
        payload: dict[str, Any],
        *,
        executor: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        manifest = self._manifests.get(tool_name)
        if manifest is None:
            raise KeyError(f"unknown tool: {tool_name}")
        undeclared = sorted(set(payload) - set(manifest.input_schema))
        if undeclared:
            raise ValueError(f"undeclared input fields: {', '.join(undeclared)}")
        if manifest.permission_class != "readonly":
            raise PermissionError(f"tool requires a governed execution lane: {tool_name}")
        output = dict(executor(dict(payload)))
        bounded_output, output_truncated = _truncate_output(output, limit=16_000)
        execution_id = self._next_execution_id()
        return {
            "ok": True,
            "tool_name": tool_name,
            "output": bounded_output,
            "receipt": {
                "execution_id": execution_id,
                "permission_class": manifest.permission_class,
                "sandbox_policy": manifest.sandbox_policy,
                "output_truncated": output_truncated,
                "cache_invalidation_required": False,
            },
        }

    def execute_governed_write(
        self,
        tool_name: str,
        payload: dict[str, Any],
        *,
        executor: Callable[[dict[str, Any]], dict[str, Any]],
        pre_write_checkpoint: dict[str, Any],
        invalidated_cache_keys: list[str],
    ) -> dict[str, Any]:
        manifest = self._manifests.get(tool_name)
        if manifest is None:
            raise KeyError(f"unknown tool: {tool_name}")
        if manifest.permission_class != "write":
            raise PermissionError(f"tool is not a governed write tool: {tool_name}")
        undeclared = sorted(set(payload) - set(manifest.input_schema))
        if undeclared:
            raise ValueError(f"undeclared input fields: {', '.join(undeclared)}")
        output = dict(executor(dict(payload)))
        bounded_output, output_truncated = _truncate_output(output, limit=16_000)
        execution_id = self._next_execution_id()
        return {
            "ok": True,
            "tool_name": tool_name,
            "output": bounded_output,
            "receipt": {
                "execution_id": execution_id,
                "permission_class": manifest.permission_class,
                "sandbox_policy": manifest.sandbox_policy,
                "output_truncated": output_truncated,
                "cache_invalidation_required": True,
                "invalidated_cache_keys": list(invalidated_cache_keys),
                "pre_write_checkpoint": pre_write_checkpoint,
            },
        }

    def execute_batch(
        self,
        requests: list[dict[str, Any]],
        *,
        executor: Callable[[str, dict[str, Any]], dict[str, Any]],
        max_workers: int = 4,
    ) -> dict[str, Any]:
        if not requests:
            raise ValueError("batch requests are required")
        if max_workers < 1 or max_workers > 16:
            raise ValueError("max_workers must be between 1 and 16")
        normalized: list[tuple[str, dict[str, Any]]] = []
        for request in requests:
            tool_name = str(request.get("tool_name") or "")
            manifest = self._manifests.get(tool_name)
            if manifest is None:
                raise KeyError(f"unknown tool: {tool_name}")
            if manifest.permission_class != "readonly" or tool_name not in self._concurrent_safe:
                raise PermissionError(f"tool is not parallel-safe readonly: {tool_name}")
            item_payload = request.get("payload")
            if not isinstance(item_payload, dict):
                raise ValueError("batch payload must be an object")
            normalized.append((tool_name, item_payload))

        def run(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
            tool_name, item_payload = item
            return self.execute(
                tool_name,
                item_payload,
                executor=lambda payload: executor(tool_name, payload),
            )

        with ThreadPoolExecutor(max_workers=min(max_workers, len(normalized))) as pool:
            results = list(pool.map(run, normalized))
        return {
            "parallelized": len(normalized) > 1,
            "request_count": len(normalized),
            "results": results,
        }

    def _next_execution_id(self) -> str:
        with self._execution_lock:
            self._execution_count += 1
            return f"tool-execution:{self._execution_count:06d}"


def _truncate_output(value: Any, *, limit: int) -> tuple[Any, bool]:
    if isinstance(value, str):
        return value[:limit], len(value) > limit
    if isinstance(value, dict):
        truncated = False
        bounded: dict[str, Any] = {}
        for key, item in value.items():
            bounded_item, item_truncated = _truncate_output(item, limit=limit)
            bounded[str(key)] = bounded_item
            truncated = truncated or item_truncated
        return bounded, truncated
    if isinstance(value, list):
        bounded_items = []
        truncated = False
        for item in value:
            bounded_item, item_truncated = _truncate_output(item, limit=limit)
            bounded_items.append(bounded_item)
            truncated = truncated or item_truncated
        return bounded_items, truncated
    return value, False

