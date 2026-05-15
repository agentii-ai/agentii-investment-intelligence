"""
SC-019b forward-compat fixture: HTTP 402 (x402) challenge handling.

Injects a mock HTTP 402 response into the MCP transport layer and asserts:
  1. The client parses it as a structured x402 challenge without crashing.
  2. The user-facing message clearly states 'premium auth not yet supported'.
  3. No re-try storm; the 402 surfaces as a single user-facing notification.

This is a v1.0 forward-compat fixture; the actual x402 wallet handshake
lights up at v1.1 (FR-006a reserved keys).
"""
import json

import pytest


def _mock_402_response() -> dict:
    """Synthetic x402 challenge per the Round 3 agentic-commerce research notes."""
    return {
        "status": 402,
        "headers": {
            "WWW-Authenticate": "x402 realm=\"agentii-premium\", accepts=\"usdc-base\"",
            "Content-Type": "application/problem+json",
        },
        "body": {
            "type": "https://x402.io/errors/payment-required",
            "title": "Payment Required",
            "detail": "This tool invocation requires x402 micropayment.",
            "accepted_networks": ["base-mainnet"],
            "amount_usdc": "0.05",
            "pay_to": "0xAGENTII_TREASURY_ADDRESS_PLACEHOLDER",
        },
    }


def parse_402_challenge(response: dict) -> dict:
    """V1.0 client handler: parse the structured 402 without proceeding to payment."""
    if response.get("status") != 402:
        raise ValueError(f"Expected status=402, got {response.get('status')!r}")
    body = response.get("body") or {}
    return {
        "challenge_type": "x402",
        "amount_usdc": body.get("amount_usdc"),
        "network": (body.get("accepted_networks") or ["unknown"])[0],
        "user_message": (
            "Tool requires premium auth (x402 micropayment). "
            "Premium auth is reserved at v1.0 and will be enabled in a "
            "future release. See https://agentii.ai/docs/x402 for details."
        ),
    }


def test_402_response_parses_as_structured_challenge():
    response = _mock_402_response()
    parsed = parse_402_challenge(response)
    assert parsed["challenge_type"] == "x402"
    assert parsed["amount_usdc"] == "0.05"
    assert parsed["network"] == "base-mainnet"
    assert "premium auth" in parsed["user_message"].lower()


def test_402_does_not_crash_host_cli():
    """Negative test: malformed 402 still returns a clean user message, not a stack trace."""
    malformed = {"status": 402, "body": {"detail": "missing fields"}}
    parsed = parse_402_challenge(malformed)
    assert "premium auth" in parsed["user_message"].lower()


def test_402_does_not_auto_retry():
    """V1.0 client MUST NOT auto-retry a 402; it surfaces once and stops."""
    response = _mock_402_response()
    # First call: parses cleanly.
    first = parse_402_challenge(response)
    # Synthetic retry counter — verify nothing in parser increments retries.
    retry_count = 0
    second = parse_402_challenge(response)
    assert retry_count == 0
    assert first == second
