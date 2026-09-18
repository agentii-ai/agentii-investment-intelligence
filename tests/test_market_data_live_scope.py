"""L7: the live path across the 19 thesis tickers (defect D3).

DELIBERATE DEPARTURE FROM `test_market_data_smoke.py`
-----------------------------------------------------
The existing smoke test calls `_skip_on_rate_limit()`, which converts a provider
429 into `pytest.skip`. That helper's effect is to make the suite green while the
capability is entirely down — it hides exactly the condition this plan exists to
find. Here, a 429 or a 403 is DATA: it is recorded and asserted on.

Two layers of assertion, deliberately separated:

1. `test_envelope_is_always_well_formed` — must pass even when the provider is
   down. A refusal is a valid outcome; a malformed refusal is a bug.
2. `test_*_delivers_a_pinnable_quote` — asserts what the contract PROMISES. These
   are `xfail(strict=False)` because whether they pass depends on an external
   service, not on this repo. When the provider recovers they report XPASS, which
   is the signal to remove the marker.

Run with:  pytest tests/test_market_data_live_scope.py -v --run-live -m live
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "data-tools"))

import market_data  # noqa: E402
import _envelope  # noqa: E402

pytestmark = [pytest.mark.live]

# The 19 tickers named in a thesis §2 universe table (see testing-plan.md §A).
THESIS_TICKERS = [
    "ADI", "AEVA", "AMBA", "AMZN", "CAT", "CGNX", "DE", "EMR", "ETN", "F",
    "GE", "HON", "ISRG", "NVDA", "ON", "PH", "QCOM", "SPCX", "TSLA",
]

# SPCX is the agentii-plane's synthetic ticker for SpaceX (constitution.md §P2).
# Yahoo has no such symbol, so failure is the documented, correct outcome.
SYNTHETIC_TICKERS = {"SPCX"}

REAL_TICKERS = [t for t in THESIS_TICKERS if t not in SYNTHETIC_TICKERS]


@pytest.fixture(scope="module")
def quotes(tmp_path_factory):
    """Fetch every ticker once; the assertions below read from this map."""
    root = tmp_path_factory.mktemp("live-quotes")
    return {t: market_data.get_quote(t, cache_root=root) for t in THESIS_TICKERS}


def _is_rate_limited(env: dict) -> bool:
    err = str(env.get("error") or "").lower()
    return "rate limit" in err or "too many requests" in err


# --- Layer 1: shape invariants that hold whether or not the provider is up ----

def test_envelope_is_always_well_formed(quotes):
    """Schema conformance must not depend on provider availability."""
    for ticker, env in quotes.items():
        _envelope.validate(env)
        assert env["status"] in ("ok", "degraded", "error"), ticker
        if env["status"] == "error":
            assert env["data"] is None
            assert env["error"], f"{ticker}: error status with no reason"
            assert ":" in env["error"].split(" ")[0], (
                f"{ticker}: error must carry a CODE: prefix from taxonomy.yaml, "
                f"got {env['error']!r}"
            )


def test_no_provider_failure_is_silent(quotes):
    """The failure mode that matters: a ticker that returns status=ok with no
    price would look like success to every downstream consumer."""
    for ticker, env in quotes.items():
        if env["status"] == "ok":
            assert env["data"].get("price") is not None, (
                f"{ticker}: status=ok but price is null — a silent failure"
            )


def test_observed_at_invariant_holds_wherever_a_price_is_served(quotes):
    """The Q71 rule, checked against reality: no price without a timestamp."""
    for ticker, env in quotes.items():
        if env["status"] == "ok":
            assert env["data"].get("observed_at"), (
                f"{ticker}: price served without observed_at (Q71 violation)"
            )


# --- Layer 2: what the contract promises -------------------------------------

@pytest.mark.xfail(strict=False, reason=(
    "D3: the live provider is returning 429 for every ticker from this machine, "
    "and the raw Yahoo v8 fallback returns HTTP 403 with an HTML body. External "
    "condition — XPASS here means the provider recovered."))
def test_quote_delivers_a_pinnable_price_for_every_real_ticker(quotes):
    failures = {}
    for ticker in REAL_TICKERS:
        env = quotes[ticker]
        if env["status"] != "ok":
            failures[ticker] = env.get("error")
    assert not failures, (
        f"{len(failures)}/{len(REAL_TICKERS)} tickers returned no usable quote: "
        f"{failures}"
    )


@pytest.mark.xfail(strict=False, reason=(
    "D3 (history half): get_price_history cannot return bars even when the network "
    "is healthy, because of the provider-selection bug D1."))
def test_history_delivers_bars_for_every_real_ticker(tmp_path):
    failures = {}
    for ticker in REAL_TICKERS:
        env = market_data.get_price_history(ticker, period="1y", interval="1d",
                                            cache_root=tmp_path / ticker)
        if env["status"] != "ok":
            failures[ticker] = env.get("error")
    assert not failures, (
        f"{len(failures)}/{len(REAL_TICKERS)} tickers returned no bar history: "
        f"{failures}"
    )


def test_synthetic_ticker_fails_cleanly_rather_than_substituting(quotes):
    """SPCX has no Yahoo symbol. The acceptable outcomes are a clean refusal or a
    clean success-by-substitution — never a wrong company's price served silently.
    The constitution's ALNT->ALNY note is the precedent this guards against."""
    env = quotes["SPCX"]
    _envelope.validate(env)
    if env["status"] == "ok":
        # If a price did come back, it must be attributed, not silently accepted.
        assert env["data"].get("observed_at"), "SPCX price served without provenance"


def test_rate_limit_is_reported_as_source_unavailable_not_missing_data(quotes):
    """A 429 is an environmental condition. Misreporting it as NOT_FOUND would send
    an operator hunting for a data problem that does not exist."""
    limited = {t: e for t, e in quotes.items() if _is_rate_limited(e)}
    if not limited:
        pytest.skip("provider is not currently rate-limiting")
    for ticker, env in limited.items():
        assert env["status"] == "error"
        assert env["error"].startswith("SOURCE_UNAVAILABLE"), (
            f"{ticker}: a rate limit was reported as {env['error']!r} — operators "
            f"will chase the wrong cause"
        )
