"""Canon Aspect 10: real MCP JSON-RPC client (handshake, tools/list, tools/call, trust gate)."""
from __future__ import annotations

import pytest

from nexusnet.protocols import MCPClient, InProcessMCPServer, JsonRpcError, PROTOCOL_VERSION


def _server():
    s = InProcessMCPServer()
    s.register_tool("echo", lambda args: args.get("text", ""))
    s.register_tool("add", lambda args: args["a"] + args["b"],
                    input_schema={"type": "object", "properties": {"a": {}, "b": {}}})
    s.register_tool("boom", lambda args: 1 / 0)        # raises -> JSON-RPC error envelope
    return s


def test_initialize_handshake_negotiates_version():
    c = MCPClient(_server())
    res = c.initialize()
    assert res["protocolVersion"] == PROTOCOL_VERSION
    assert c.initialized is True
    assert c.server_info["name"] == "nexusnet-mock"
    assert "tools" in c.server_capabilities


def test_list_tools_returns_registered_tools():
    c = MCPClient(_server()); c.initialize()
    names = {t["name"] for t in c.list_tools()}
    assert {"echo", "add", "boom"} <= names
    assert all("inputSchema" in t for t in c.list_tools())


def test_call_tool_executes_for_real():
    c = MCPClient(_server()); c.initialize()
    out = c.call_tool("add", {"a": 2, "b": 5})
    assert out["isError"] is False
    assert out["content"][0]["text"] == "7"            # the tool actually ran


def test_unknown_tool_raises_jsonrpc_error():
    c = MCPClient(_server()); c.initialize()
    with pytest.raises(JsonRpcError) as ei:
        c.call_tool("nope")
    assert ei.value.code == -32602


def test_tool_exception_propagates_as_jsonrpc_error():
    c = MCPClient(_server()); c.initialize()
    with pytest.raises(JsonRpcError) as ei:
        c.call_tool("boom")
    assert ei.value.code == -32603


def test_consent_gate_blocks_untrusted_tool():
    # only 'echo' is consented; 'add' is blocked by the trust/consent gate
    c = MCPClient(_server(), consent_gate=lambda name: name == "echo")
    c.initialize()
    assert c.call_tool("echo", {"text": "hi"})["content"][0]["text"] == "hi"
    with pytest.raises(PermissionError):
        c.call_tool("add", {"a": 1, "b": 2})


def test_requires_initialize_before_calls():
    c = MCPClient(_server())
    with pytest.raises(RuntimeError):
        c.list_tools()


def test_response_id_mismatch_is_detected():
    # a broken transport that always returns id=999 must be caught (JSON-RPC correlation)
    bad_transport = lambda req: {"jsonrpc": "2.0", "id": 999, "result": {}}
    c = MCPClient(bad_transport)
    with pytest.raises(JsonRpcError):
        c.initialize()


def test_trust_registry_decision_can_drive_the_gate():
    # wire a ProtocolTrustRegistry decision into the client's consent gate (governed protocol calls)
    from nexusnet.protocols import ProtocolTrustRegistry, ProtocolAdapterRequest
    reg = ProtocolTrustRegistry()
    rec = reg.register(ProtocolAdapterRequest(
        adapter_id="mcp1", protocol="MCP", endpoint="inproc://x", enabled=True,
        identity_ref="id://1", consent_ref="consent://1", permissions=["tools:echo"],
        revocation_ref="rev://1", sandboxed=True))
    trusted = str(rec["status"]).startswith("trusted")
    c = MCPClient(_server(), consent_gate=lambda name: trusted and "tools:echo" in rec["trust_envelope"]["permissions"])
    c.initialize()
    assert c.call_tool("echo", {"text": "ok"})["content"][0]["text"] == "ok"
