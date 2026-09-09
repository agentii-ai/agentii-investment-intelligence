"""S1-spike (T011): the _envelope.py error shape must survive JSON transport intact.

MCP tool results are JSON-text content — serialization round-trip integrity IS the
transport property. The S1-thin refusal convention: the envelope `error` string
carries a `CODE:` prefix from contracts/taxonomy.yaml (e.g. "DATA_STALE: <remediation>").
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import _envelope  # noqa: E402


def test_error_envelope_survives_json_roundtrip():
    env = _envelope.error("DATA_STALE: source data predates the artifact as_of")
    assert env["status"] == "error"
    assert env["data"] is None
    out = json.loads(json.dumps(env))
    assert out == env
    assert out["error"] == "DATA_STALE: source data predates the artifact as_of"


def test_error_code_prefix_is_stable_and_parseable():
    env = _envelope.error("DATA_STALE: re-run after refresh")
    code = env["error"].split(":", 1)[0]
    assert code == "DATA_STALE"


def test_ok_envelope_carries_spec046_fields():
    env = _envelope.ok(
        {"symbol": "NVDA", "price": 230.0},
        source="yfinance",
        cache_hit=False,
    )
    # spec 046 additions (data_class/observed_at) ride inside `data` — they must
    # survive the round-trip just like every other payload key.
    env["data"]["data_class"] = "fast"
    env["data"]["observed_at"] = "2026-09-08T16:00:00-04:00"
    out = json.loads(json.dumps(env))
    assert out["data"]["data_class"] == "fast"
    assert out["data"]["observed_at"] == "2026-09-08T16:00:00-04:00"
    assert out["status"] == "ok"
    assert out["error"] is None


def test_envelope_validates_against_schema():
    # _envelope.validate raises on structural violation — proving the error
    # envelope is schema-conformant (AGENT_CONTRACT invariant).
    env = _envelope.error("DATA_STALE: re-run after refresh")
    _envelope.validate(env)  # must not raise


def test_error_requires_reason_invariant():
    try:
        _envelope.error("")
        raised = False
    except ValueError:
        raised = True
    assert raised, "error() with an empty reason must raise (AGENT_CONTRACT invariant 2)"
