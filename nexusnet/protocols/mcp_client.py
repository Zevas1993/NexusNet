"""Canon Aspect 10: a REAL MCP client (JSON-RPC 2.0), not just the trust registry.

`protocols/trust.py` GOVERNS protocol adapters (identity/consent/permissions/sandbox) but nothing
actually SPEAKS the protocol. This is a real Model Context Protocol client: correct JSON-RPC 2.0
framing (id matching, result/error envelopes), the MCP handshake (`initialize`), and `tools/list` /
`tools/call`. The transport is pluggable - a `Callable[[dict], dict]` - so it runs in-process for
tests (and a stdio/HTTP transport can be supplied for real servers). No network by default; tool calls
are gated by a consent/trust callable so they honor the ProtocolTrustRegistry decision.
"""
from __future__ import annotations

from typing import Any, Callable

Transport = Callable[[dict], dict]
PROTOCOL_VERSION = "2025-06-18"


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.data = data


class MCPClient:
    """Minimal, correct MCP client over a pluggable JSON-RPC transport."""

    def __init__(self, transport: Transport, *, client_name: str = "nexusnet",
                 consent_gate: Callable[[str], bool] | None = None) -> None:
        self.transport = transport
        self.client_name = client_name
        self.consent_gate = consent_gate          # (tool_name) -> bool; None = governed elsewhere
        self._id = 0
        self.initialized = False
        self.server_capabilities: dict[str, Any] = {}
        self.server_info: dict[str, Any] = {}

    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self._id += 1
        request = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        response = self.transport(request)
        if response.get("jsonrpc") != "2.0":
            raise JsonRpcError(-32603, "invalid jsonrpc version in response")
        if response.get("id") != request["id"]:
            raise JsonRpcError(-32603, f"response id {response.get('id')} != request id {request['id']}")
        if "error" in response:
            err = response["error"]
            raise JsonRpcError(err.get("code", -32603), err.get("message", "error"), err.get("data"))
        return response.get("result")

    def initialize(self) -> dict[str, Any]:
        """MCP handshake: negotiate protocol version + exchange capabilities."""
        result = self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "clientInfo": {"name": self.client_name},
        })
        self.server_capabilities = result.get("capabilities", {})
        self.server_info = result.get("serverInfo", {})
        self.initialized = True
        return result

    def _require_init(self) -> None:
        if not self.initialized:
            raise RuntimeError("MCP client not initialized; call initialize() first")

    def list_tools(self) -> list[dict[str, Any]]:
        self._require_init()
        return self._rpc("tools/list").get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call a tool. Blocked if the consent/trust gate denies it (honors ProtocolTrustRegistry)."""
        self._require_init()
        if self.consent_gate is not None and not self.consent_gate(name):
            raise PermissionError(f"tool '{name}' blocked by protocol trust/consent gate")
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})


def consent_gate_from_trust(trust_record: dict[str, Any], *, tool_permission_prefix: str = "tools:"
                            ) -> Callable[[str], bool]:
    """Build an MCPClient consent gate from a ProtocolTrustRegistry record: a tool is allowed only if
    the adapter is trusted+enabled and the tool's scoped permission is present in the trust envelope."""
    trusted = str(trust_record.get("status", "")).startswith("trusted")
    permissions = set((trust_record.get("trust_envelope") or {}).get("permissions") or [])

    def _gate(tool_name: str) -> bool:
        return trusted and f"{tool_permission_prefix}{tool_name}" in permissions

    return _gate


class InProcessMCPServer:
    """A real in-process MCP server (transport) for tests/local use: registers tools, speaks JSON-RPC."""

    def __init__(self, *, name: str = "nexusnet-mock") -> None:
        self.name = name
        self._tools: dict[str, tuple[Callable[[dict], Any], dict]] = {}

    def register_tool(self, name: str, fn: Callable[[dict], Any], *, input_schema: dict | None = None) -> None:
        self._tools[name] = (fn, input_schema or {"type": "object"})

    def __call__(self, request: dict) -> dict:
        rid = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        def ok(result: Any) -> dict:
            return {"jsonrpc": "2.0", "id": rid, "result": result}

        def err(code: int, message: str) -> dict:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}

        if method == "initialize":
            return ok({"protocolVersion": PROTOCOL_VERSION,
                       "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": self.name}})
        if method == "tools/list":
            return ok({"tools": [{"name": n, "inputSchema": schema}
                                 for n, (_, schema) in sorted(self._tools.items())]})
        if method == "tools/call":
            name = params.get("name")
            if name not in self._tools:
                return err(-32602, f"unknown tool: {name}")
            try:
                out = self._tools[name][0](params.get("arguments", {}))
            except Exception as exc:                       # tool error -> JSON-RPC error envelope
                return err(-32603, f"tool execution error: {exc}")
            return ok({"content": [{"type": "text", "text": str(out)}], "isError": False})
        return err(-32601, f"method not found: {method}")
