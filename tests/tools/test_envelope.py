"""T049 — tests for data-tools/_envelope.py (write FIRST)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "_envelope.py"
SCHEMA = REPO_ROOT / "contracts" / "envelope.schema.json"


def _load():
    spec = importlib.util.spec_from_file_location("_envelope", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_ok_envelope_valid():
    m = _load()
    env = m.ok({"price": 100}, source="yfinance", rate_limit_remaining=118)
    assert env["status"] == "ok"
    assert env["data"] == {"price": 100}
    m.validate(env)  # against schema, must not raise


def test_error_envelope_invariant():
    m = _load()
    env = m.error("RATE_LIMITED: too many calls", source="fred")
    assert env["status"] == "error"
    assert env["data"] is None
    assert env["error"]
    m.validate(env)


def test_degraded_requires_error_reason():
    m = _load()
    env = m.degraded({"partial": True}, source="yfinance", error="FRED key missing; used yfinance")
    assert env["status"] == "degraded"
    assert env["error"]
    m.validate(env)


def test_ok_with_null_data_rejected():
    m = _load()
    bad = {"status": "ok", "data": None, "source": "x", "cache_hit": False,
           "rate_limit_remaining": None, "error": None}
    with pytest.raises(Exception):
        m.validate(bad)


def test_roundtrip_json():
    m = _load()
    env = m.ok([1, 2, 3], source="secfin")
    s = json.dumps(env)
    assert json.loads(s)["data"] == [1, 2, 3]
