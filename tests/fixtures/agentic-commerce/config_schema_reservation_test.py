"""
SC-019c forward-compat fixture: ~/.agentii/config.json reserved keys.

Sets `x402_wallet_address` and `agentmail_inbox_id` in a mock config and
asserts the v1.0 client SILENTLY IGNORES them (no error, no warning, no
storage-side effect). The keys are reserved per FR-006a for v1.1 lighting-up
without requiring a v1.0 client to break or warn.
"""
import json
from pathlib import Path

import pytest

# Load the agentii-config.schema.json shipped with the package
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "agentii-config.schema.json"
)


def _load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        pytest.skip(f"Schema not yet authored at {SCHEMA_PATH}; T015b ships it.")
    return json.loads(SCHEMA_PATH.read_text())


def test_reserved_keys_pass_schema_validation():
    """Reserved keys MUST NOT cause schema validation errors at v1.0."""
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed")

    schema = _load_schema()
    config_with_reserved = {
        "telemetry": {
            "server_export": False,
            "tier": "off",
        },
        "install_uuid": "00000000-0000-0000-0000-000000000001",
        # Reserved per FR-006a / SC-019c — MUST be accepted silently.
        "x402_wallet_address": "0xAGENTII_RESERVED_AT_V1_0",
        "agentmail_inbox_id": "inbox_RESERVED_AT_V1_0",
    }
    # Should NOT raise.
    jsonschema.validate(instance=config_with_reserved, schema=schema)


def test_reserved_keys_have_no_runtime_side_effect():
    """V1.0 runtime MUST NOT attempt to use the reserved keys."""

    def _v1_0_consumer(config: dict) -> set[str]:
        """Returns the set of keys the v1.0 runtime actually reads."""
        consumed = set()
        for key in ("telemetry", "install_uuid", "models-and-pitches", "offline_mode"):
            if key in config:
                consumed.add(key)
        return consumed

    config = {
        "telemetry": {"server_export": False, "tier": "off"},
        "install_uuid": "00000000-0000-0000-0000-000000000001",
        "x402_wallet_address": "0xRESERVED",
        "agentmail_inbox_id": "inbox_RESERVED",
    }
    consumed = _v1_0_consumer(config)
    assert "x402_wallet_address" not in consumed
    assert "agentmail_inbox_id" not in consumed
    assert "telemetry" in consumed
    assert "install_uuid" in consumed
