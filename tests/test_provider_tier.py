"""test_provider_tier.py — T178–T185 (Q44/Q104/Q119). The serving path.

T185 requires the two corrections the research made to the chosen provider set to
be **tests, not comments**. They are:

  1. **Finnhub is quotes-only.** Its free tier covers the quote endpoint but US
     OHLC history is behind the paid plan, and its ToS restricts business use. The
     registry listed it as a general market source — that entry was misleading.
  2. **Alpaca was absent from the chosen set and should be adapter number one** —
     the only free tier clearing every constraint at once (200 req/min, no daily
     cap, true batching, bars to 2016, real-time IEX, free paper key, no card).

Plus T179's ordering, T180's SKIPPED≠FAIL, T181's negative control, T182's
agreement gate, and T183's egress scope — each asserted, because a comment does
not fail when it stops being true.

**Live HTTP is opt-in.** The reachability assertions need the network and are
skipped by default; run `pytest --run-live` to include them. Everything that can
be asserted about the REGISTRY and the DISPATCH LOGIC is asserted always.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data-tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import _envelope  # noqa: E402
import _sources  # noqa: E402
import source_probe as sp  # noqa: E402


def _market() -> dict[str, dict]:
    return {s["name"]: s for s in _sources.for_category("market")}


def _priority(name: str) -> int:
    return _market()[name]["priority"]


def _live(request) -> None:
    if not request.config.getoption("--run-live", default=False):
        pytest.skip("live test: pass --run-live (and set API-key secrets) to run")


# ── T185 correction 1: Finnhub is quotes-only ───────────────────────────────

def test_finnhub_free_tier_cannot_serve_history():
    """The correction, as an assertion. Finnhub's free tier covers the quote
    endpoint; US OHLC history is paid, and its ToS forbids business use even
    internally without written approval. Keeping the adapter is fine — treating
    it as a general history source is not."""
    fh = _market()["finnhub"]
    note = (fh.get("note") or "").lower()
    assert "quotes only" in note, (
        "finnhub's registry entry must state its quotes-only limitation; the "
        "entry that listed it as a general market source is what T185 corrects")
    assert "ohlc" in note or "history" in note


def test_finnhub_is_ranked_below_every_source_that_can_serve_history():
    """It is kept, and it is tried after the sources whose free tier actually
    covers history — otherwise a quotes-only source would answer history calls."""
    assert _priority("finnhub") > _priority("nasdaq")
    assert _priority("finnhub") > _priority("sina")
    assert _priority("finnhub") > _priority("alpaca")


# ── T185 correction 2: Alpaca is adapter number one ─────────────────────────

def test_alpaca_is_the_highest_priority_market_source():
    """Not in the original chosen set; measured as the strongest candidate."""
    top = min(_market().values(), key=lambda s: s["priority"])
    assert top["name"] == "alpaca", (
        f"adapter number one is {top['name']!r}, not alpaca — T185's second "
        f"correction has drifted")
    note = top["note"].lower()
    for claim in ("batch", "200 req/min", "paper"):
        assert claim in note, f"the alpaca entry must state {claim!r}"


# ── T179: Nasdaq is the keyless primary, Sina the fast secondary ────────────

def test_nasdaq_is_the_first_keyless_source():
    keyless = sorted((s for s in _market().values() if s["auth"] == "none"),
                     key=lambda s: s["priority"])
    assert keyless[0]["name"] == "nasdaq", [s["name"] for s in keyless[:3]]


def test_sina_is_the_second_keyless_source_and_the_chain_notes_are_factual():
    keyless = sorted((s for s in _market().values() if s["auth"] == "none"),
                     key=lambda s: s["priority"])
    assert keyless[1]["name"] == "sina"
    # the measured facts the ordering rests on
    assert "40x" in (keyless[1]["note"] or "") or "faster" in (keyless[1]["note"] or "")
    assert "GBK" in (keyless[1]["note"] or "")


def test_yahoo_is_last_and_marked_as_the_negative_control():
    """It was priority 10 — the DEFAULT — while being the one source measured as
    failing. That is the mis-ordering T179 corrects."""
    y = _market()["yfinance"]
    assert y["priority"] >= 90, y["priority"]
    assert "negative control" in (y["note"] or "").lower()


def test_tencent_is_after_sina_because_it_cannot_serve_history():
    assert _priority("tencent") > _priority("sina")
    assert "quote" in (_market()["tencent"].get("note") or "").lower()


# ── T180: SKIPPED is not FAIL ───────────────────────────────────────────────

def test_skipped_is_a_distinct_status_and_validates():
    env = _envelope.skipped("FINNHUB_API_KEY unset", source="finnhub")
    _envelope.validate(env)
    assert env["status"] == "skipped"
    assert env["data"] is None


def test_a_missing_key_skips_rather_than_failing(monkeypatch):
    """The zero-key path must always work: five of nine market sources take no
    key, so on a machine with no keys it is the whole path, not a fallback."""
    for var in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY", "TIINGO_API_KEY",
                "POLYGON_API_KEY", "FMP_API_KEY", "FINNHUB_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    available, reason = sp.source_available("alpaca")
    assert available is False
    assert "skipped" in reason.lower()
    assert "unset" in reason.lower()


def test_a_present_key_makes_the_source_available(monkeypatch):
    monkeypatch.setenv("TIINGO_API_KEY", "x")
    assert sp.source_available("tiingo") == (True, "")


def test_the_serving_chain_omits_unkeyed_sources_and_reports_them(monkeypatch):
    """Omitted from the chain (never tried, never failed) AND reportable — the
    two halves together are what keep 'no key' distinguishable from 'down'."""
    for var in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY", "TIINGO_API_KEY",
                "POLYGON_API_KEY", "FMP_API_KEY", "FINNHUB_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    import market_data

    chain = market_data._real_providers()
    for keyed in ("alpaca", "tiingo", "massive", "finnhub"):
        assert keyed not in chain, f"{keyed} needs a key and must not be tried"
    assert chain, "the keyless path must still have sources"
    skipped = market_data.skipped_sources()
    assert len(skipped) >= 4
    assert all("skipped" in s.lower() for s in skipped)


def test_the_offline_fixture_is_not_in_the_failover_chain():
    """It returns price 0.0. In the chain that would make get_quote return `ok`
    at a zero price — a silent degradation of the kind this spec exists to stop.
    It is reachable only via the explicit `--offline-fixture` flag, which wraps it
    in a `degraded` envelope."""
    import market_data

    assert "offline-fixture" not in market_data._real_providers()


# ── T181: Yahoo as a negative control ───────────────────────────────────────

def test_yahoo_is_a_registered_probe_source_whose_failure_is_structured():
    """Its ASSERTION is the refusal: a known-unreachable source must fail in
    shape, because an unstructured failure from it would corrupt the failover
    path for the sources that work."""
    env = sp.probe_source("yahoo", "AAPL") if _network_ok() else None
    if env is None:
        pytest.skip("no network — the structured-refusal assertion needs a reply")
    assert set(env) >= {"status", "data", "source", "error"}
    assert env["status"] in ("ok", "error", "degraded", "skipped")
    if env["status"] != "ok":
        _envelope.validate(env)
        assert env["error"], "a failure must carry a reason, not just a status"


def test_yahoo_is_tried_last_so_its_failure_costs_nothing():
    assert _priority("yfinance") > max(
        _priority(n) for n in _market() if n not in ("yfinance", "investpy"))


# ── T182: cross-source agreement ────────────────────────────────────────────

def test_agreement_gate_refuses_on_disagreement():
    """Measured baseline: 19/19 tickers, 3 sources each, agreed TO THE CENT. So
    any disagreement is signal, not noise — a parser that swaps close and high
    yields plausible-looking numbers and nothing else would flag it."""
    results = {
        "nasdaq": _envelope.ok({"price": 332.41}, source="nasdaq"),
        "sina": _envelope.ok({"price": 332.41}, source="sina"),
        "tencent": _envelope.ok({"price": 999.99}, source="tencent"),
    }
    verdict = sp.cross_source_agreement(results)
    assert verdict["agree"] is False
    assert verdict["divergent"], verdict          # the key is `divergent`
    assert "tencent" in verdict["divergent"]
    assert verdict["comparable"] == 3


def test_agreement_gate_passes_on_agreement():
    results = {n: _envelope.ok({"price": 332.41}, source=n)
               for n in ("nasdaq", "sina", "tencent")}
    assert sp.cross_source_agreement(results)["agree"] is True


def test_agreement_needs_two_sources_not_one():
    """One source agreeing with itself proves nothing. With a single reply there
    is no agreement to assert — and reporting `agree: True` from one source would
    be a gate that examined nothing and called it a pass (Q105)."""
    verdict = sp.cross_source_agreement({"nasdaq": _envelope.ok({"price": 1.0},
                                                                source="nasdaq")})
    assert verdict["agree"] is not True


# ── T183: the egress scope is recorded where a reader will meet it ──────────

def test_sources_md_records_the_egress_scope():
    doc = (ROOT / "contracts" / "SOURCES.md").read_text(encoding="utf-8")
    assert "OUT OF" in doc and "SCOPE" in doc
    assert "must not drive provider choice" in doc
    # the two failures must stay distinguished, or a reader concludes Yahoo is
    # broken for the actual users
    assert "not a geography problem" in doc
    assert "A proxy is not a fix" in doc
    assert "SKIPPED" in doc


# ── live reachability (opt-in) ──────────────────────────────────────────────

def _network_ok() -> bool:
    try:
        sp._http_get("https://api.nasdaq.com/api/quote/AAPL/info?assetclass=stocks")
        return True
    except Exception:  # noqa: BLE001
        return False


def test_live_keyless_sources_answer_and_agree(request):
    """`--run-live`. Measured 2026-09-17: nasdaq, sina and tencent all returned
    AAPL 332.41. Three independent sources agreeing to the cent is what makes the
    agreement gate's baseline trustworthy."""
    _live(request)
    results = {n: sp.probe_source(n, "AAPL") for n in ("nasdaq", "sina", "tencent")}
    ok = {n: e for n, e in results.items() if e["status"] == "ok"}
    assert len(ok) >= 2, {n: e.get("error") for n, e in results.items()}
    assert sp.cross_source_agreement(ok)["agree"] is True, ok
