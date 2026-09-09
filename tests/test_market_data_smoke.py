"""T077 — live smoke against the real provider (spec 046 Q43).

Deterministic assertions on the real pipeline: envelope ok, observed_at/retrieved_at
parseable ISO-8601, 1y bars ≥ 250 ascending with no None close, last_close > 0.
Skipped when MARKET_DATA_SKIP_LIVE=1 or the deps/network are unavailable —
a missing environment must never masquerade as a pipeline failure (importorskip).
Ships WITH the field completion, never after (Q71 red-from-day-one rule).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import market_data  # noqa: E402

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(os.environ.get("MARKET_DATA_SKIP_LIVE") == "1",
                       reason="MARKET_DATA_SKIP_LIVE=1"),
]

pytest.importorskip("yfinance")


def test_live_quote_envelope():
    env = market_data.get_quote("AAPL")
    _skip_on_rate_limit(env)
    assert env["status"] == "ok"
    d = env["data"]
    assert d["price"] > 0
    _iso(d["observed_at"])
    _iso(d["retrieved_at"])
    assert d["price_basis"] == "close"
    assert d["data_class"] == "fast"


def test_live_history_bars():
    env = market_data.get_price_history("AAPL", period="1y", interval="1d")
    _skip_on_rate_limit(env)
    assert env["status"] == "ok", env.get("error")
    bars = env["data"]["bars"]
    assert len(bars) >= 250
    dates = [b["date"] for b in bars]
    assert dates == sorted(dates)  # ascending
    assert all(b["close"] is not None for b in bars)  # None-vs-0 semantics


def _iso(value):
    import datetime

    assert datetime.datetime.fromisoformat(value)


def _skip_on_rate_limit(env):
    """Q43's environment rule: a provider-side 429 is an external condition, not a
    pipeline defect — skip, never fail. (Shape violations still fail: that's the
    smoke's whole purpose.)"""
    error = str(env.get("error") or "")
    if "rate limit" in error.lower() or "too many requests" in error.lower() \
            or "RATE_LIMITED" in error:
        pytest.skip(f"provider rate-limited (environmental): {error}")
