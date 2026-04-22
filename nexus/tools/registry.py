from __future__ import annotations

from ..schemas import ToolManifest


class ToolRegistry:
    def __init__(self):
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

