"""T051 — tests for data-tools/macro_data.py (~~macro_data). FRED keyed + zero-key fallback."""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "macro_data.py"


def _load():
    spec = importlib.util.spec_from_file_location("macro_data", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _envval():
    spec = importlib.util.spec_from_file_location("_envelope", REPO_ROOT / "data-tools" / "_envelope.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_fred_keyed_path(tmp_path):
    m = _load()
    def fake_fred(series_id):
        return {"series_id": series_id, "observations": [{"date": "2026-01-01", "value": "3.1"}]}
    env = m.get_series("GDP", providers={"fred": fake_fred}, cache_root=tmp_path)
    assert env["status"] in ("ok", "degraded")
    assert env["source"] == "fred"
    _envval().validate(env)


def test_zero_key_fallback_when_no_fred(tmp_path):
    m = _load()
    # only a zero-key provider available
    def fake_zero(series_id):
        return {"series_id": series_id, "observations": [{"date": "2026-01-01", "value": "3.0"}]}
    env = m.get_series("GDP", providers={"yfinance": fake_zero}, cache_root=tmp_path)
    assert env["status"] in ("ok", "degraded")
    assert env["source"] == "yfinance"


def test_error_when_all_fail(tmp_path):
    m = _load()
    def boom(s):
        raise RuntimeError("no data")
    env = m.get_series("GDP", providers={"yfinance": boom}, cache_root=tmp_path)
    assert env["status"] == "error"
