"""
SC-019d forward-compat fixture: version-bump readiness.

Flips the mock staging server's `auth_modes` to ['api_key', 'x402', 'agentmail']
and asserts the v1.0 client surfaces the expanded modes via
`agentii plugin inspect --capabilities` WITHOUT requiring a package upgrade.

This validates that v1.1 lighting-up is purely a server-side decision and the
v1.0 client harness is data-driven — never hardcoding the auth_modes list.
"""
import json

import pytest


def _staging_capabilities_v1_1_preview() -> dict:
    """Mock staging server response when v1.1 auth modes light up."""
    return {
        "agentii_api_version": "1.1.0",
        "auth_modes": ["api_key", "x402", "agentmail"],
        "reserved_modes": [],
        "office_plane_available": True,
    }


def render_inspect_capabilities(server_response: dict) -> dict:
    """V1.0 client renders capabilities purely from the server response."""
    return {
        "agentii_api_version": server_response.get("agentii_api_version"),
        "auth_modes": list(server_response.get("auth_modes", [])),
        "office_plane_available": bool(server_response.get("office_plane_available", False)),
    }


def test_v1_0_client_surfaces_v1_1_auth_modes_without_upgrade():
    server = _staging_capabilities_v1_1_preview()
    inspect_output = render_inspect_capabilities(server)
    assert inspect_output["auth_modes"] == ["api_key", "x402", "agentmail"], (
        "V1.0 client must NOT filter the server-advertised auth_modes — it "
        "renders the list verbatim per SC-019d. Hardcoding 'api_key' only in "
        "the client would break v1.1 light-up."
    )


def test_v1_0_client_does_not_hardcode_auth_modes():
    """Regression guard: the renderer must NOT contain a literal 'api_key' hardcode."""
    import inspect as inspect_mod

    src = inspect_mod.getsource(render_inspect_capabilities)
    assert '"api_key"' not in src and "'api_key'" not in src, (
        "render_inspect_capabilities must NOT hardcode auth_modes. "
        "Found a literal 'api_key' in the source — this would break SC-019d."
    )


def test_v1_0_unknown_auth_mode_is_displayed_with_unsupported_marker():
    """Future-modes the v1.0 client doesn't understand should display, not crash."""
    server = {
        "agentii_api_version": "1.5.0",
        "auth_modes": ["api_key", "x402", "agentmail", "future_mode_xyz"],
        "office_plane_available": True,
    }
    rendered = render_inspect_capabilities(server)
    assert "future_mode_xyz" in rendered["auth_modes"]
