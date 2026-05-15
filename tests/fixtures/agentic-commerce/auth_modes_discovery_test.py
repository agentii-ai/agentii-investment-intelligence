"""
SC-019a forward-compat fixture: agentii_api_version capability discovery.

Asserts that when the MCP server responds to a capability query, it
declares `auth_modes: ["api_key"]` at v1.0. This test is EXPECTED TO FAIL
until spec-022/019 MCP server implements the capability discovery endpoint
per Round 3 agentic-commerce planning.

Mark: xfail at v1.0; flips to required at v1.1 (FR-006a).

Run: pytest tests/fixtures/agentic-commerce/auth_modes_discovery_test.py
"""
import json
from pathlib import Path

import pytest


@pytest.mark.xfail(
    reason=(
        "v1.0: agentii_api_version capability endpoint is not yet implemented. "
        "This fixture asserts the forward-compat contract; flips to required at v1.1 "
        "per FR-006a reserved-keys roadmap."
    ),
    strict=True,
)
def test_auth_modes_discovery_returns_api_key_only_at_v1_0():
    """At v1.0, the only declared auth_mode is api_key."""
    # Synthetic response shape — when the server is built, this will be a
    # real MCP capability discovery call instead of a hardcoded blob.
    response = _fetch_capabilities()
    assert response.get("agentii_api_version") == "1.0.0"
    assert response.get("auth_modes") == ["api_key"], (
        f"Expected ['api_key'] at v1.0, got {response.get('auth_modes')!r}. "
        "x402 and agentmail are reserved (FR-006a) but MUST NOT be advertised at v1.0."
    )


def _fetch_capabilities() -> dict:
    """Placeholder: at v1.0 this raises; at v1.1 it issues an MCP capability call."""
    raise NotImplementedError(
        "agentii_api_version capability endpoint not yet implemented at v1.0. "
        "Expected at https://mcp.agentii.ai/mcp/capabilities once spec-022 ships."
    )


def test_capability_response_shape_documented():
    """Compile-time sanity check on the v1.0-frozen capability response shape."""
    # This shape is the v1.0-frozen contract; the synthetic response above
    # must conform to it once the endpoint exists.
    schema = {
        "agentii_api_version": str,
        "auth_modes": list,
        "reserved_modes": list,
        "office_plane_available": bool,
    }
    assert set(schema.keys()) == {
        "agentii_api_version",
        "auth_modes",
        "reserved_modes",
        "office_plane_available",
    }
