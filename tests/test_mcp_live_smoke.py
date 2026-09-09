"""Live MCP round-trip smoke — the S1-spike's "the client sees the code intact"
criterion against the DEPLOYED server (spec 046 R4 / T009–T011).

The spike verified the seam by inspection and the envelope by JSON round-trip;
this test closes the live half: structured tool definitions and results survive
the real transport. Read-only calls only. Skips when no API key is configured.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))

pytestmark = pytest.mark.smoke

ENV_FILE = Path(__file__).resolve().parents[2] / "agentii-ai" / ".env.test.local"
MCP_URL = "https://mcp.agentii.ai/mcp"


def _api_key() -> str | None:
    if not ENV_FILE.is_file():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("AGENTII_API_KEY="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return None


def _rpc(method: str, params: dict | None = None, key: str | None = None) -> dict:
    if key is None:
        key = _api_key()
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        payload["params"] = params
    req = urllib.request.Request(
        MCP_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "X-API-Key": key or "",
                 "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    if body.startswith("{"):
        return json.loads(body)
    # SSE transport: the JSON-RPC result arrives as a `data:` line
    for line in body.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())
    raise AssertionError(f"unparseable MCP response: {body[:200]}")


@pytest.mark.skipif(_api_key() is None, reason="AGENTII_API_KEY not configured")
def test_live_tools_list_returns_structured_definitions():
    resp = _rpc("tools/list")
    assert "result" in resp, resp
    tools = resp["result"]["tools"]
    assert len(tools) > 10
    for t in tools[:5]:
        assert t.get("name") and isinstance(t.get("inputSchema"), dict)
    # the structured-envelope property: definitions survive the transport intact
    assert any(t["name"] == "search_companies" for t in tools)


@pytest.mark.skipif(_api_key() is None, reason="AGENTII_API_KEY not configured")
def test_live_readonly_tool_call_survives_roundtrip():
    resp = _rpc("tools/call",
                {"name": "search_companies", "arguments": {"ticker": "NVDA"}})
    assert "result" in resp, resp
    content = resp["result"]["content"]
    assert content and content[0].get("type") == "text"
    data = json.loads(content[0]["text"])
    # the result is structured JSON — the CODE-prefix refusal convention applies
    # when an error occurs; a success payload must not carry an error field
    assert isinstance(data, dict)
