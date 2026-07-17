"""T052 — tests for data-tools/market_data.py (~~market_data). Fixture-based, no live calls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "market_data.py"


def _load():
    spec = importlib.util.spec_from_file_location("market_data", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_zero_key_quote_via_injected_provider(tmp_path):
    m = _load()
    # inject a fake yfinance-like provider so no network/key needed
    def fake_yf(ticker):
        return {"symbol": ticker, "price": 150.2, "market_cap": 2.4e12}
    env = m.get_quote("AAPL", providers={"yfinance": fake_yf}, cache_root=tmp_path)
    assert env["status"] in ("ok", "degraded")
    assert env["source"] == "yfinance"
    assert env["data"]["symbol"] == "AAPL"
    m_env = _load_env_validator()
    m_env.validate(env)


def test_error_envelope_when_all_sources_fail(tmp_path):
    m = _load()
    def boom(ticker):
        raise RuntimeError("down")
    env = m.get_quote("AAPL", providers={"yfinance": boom}, cache_root=tmp_path)
    assert env["status"] == "error"
    assert env["data"] is None and env["error"]


def test_cache_hit_second_call(tmp_path):
    m = _load()
    calls = []
    def fake_yf(ticker):
        calls.append(ticker)
        return {"symbol": ticker, "price": 1.0}
    m.get_quote("AAPL", providers={"yfinance": fake_yf}, cache_root=tmp_path)
    env2 = m.get_quote("AAPL", providers={"yfinance": fake_yf}, cache_root=tmp_path)
    assert env2["cache_hit"] is True
    assert calls == ["AAPL"]  # provider called once


def test_cli_json(tmp_path):
    import subprocess, sys
    res = subprocess.run(
        [sys.executable, str(MOD), "--ticker", "AAPL", "--json", "--offline-fixture"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    payload = json.loads(res.stdout)
    for k in ("status", "data", "source", "cache_hit", "rate_limit_remaining", "error"):
        assert k in payload


def _load_env_validator():
    spec = importlib.util.spec_from_file_location("_envelope", REPO_ROOT / "data-tools" / "_envelope.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
