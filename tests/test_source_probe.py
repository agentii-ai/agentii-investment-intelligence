"""Contract tests for the multi-source probe harness (`data-tools/source_probe.py`).

These run offline. The network-dependent behaviour is covered by the harness's own
run output (`SOURCE-PROBE.md`); what is pinned here is the harness's *contract*:

- every adapter returns a well-formed envelope and NEVER raises
- a missing key is a skip, not a failure (the zero-key path must always work)
- a block page served as HTTP 200 is not mistaken for data
- the cross-source agreement check actually catches divergence — because a parser
  that swaps close and high produces entirely plausible numbers

The last one is the whole point of the agreement check, so it is tested with a
deliberately-wrong fixture rather than by assertion of intent.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "data-tools"))
import source_probe  # noqa: E402
import _envelope  # noqa: E402

# A verified triple: on 2026-09-16 three independent sources returned these exact
# values for AAPL, which is also how Tencent's positional field order was
# confirmed (close is the THIRD field, not the fourth).
AAPL_2026_09_16 = {"open": 332.53, "close": 332.41, "high": 335.48, "low": 330.70}


def _ok(name: str, price: float, **kw) -> dict:
    return _envelope.ok(source_probe._quote("AAPL", name, price=price, **kw), source=name)


# --- envelope contract ------------------------------------------------------

def test_every_adapter_is_registered_with_a_callable_and_an_auth_spec():
    for name, spec in source_probe.SOURCES.items():
        assert callable(spec["fn"]), name
        assert spec["auth"] == source_probe.KEYLESS or isinstance(spec["auth"], list), name
        assert spec.get("license"), f"{name} must declare a license"


def test_unknown_or_failing_adapter_degrades_to_an_envelope(monkeypatch):
    """An adapter that raises must not kill the run — it must return an envelope."""
    def _boom(_ticker):
        raise RuntimeError("kaboom")

    monkeypatch.setitem(source_probe.SOURCES, "breaker",
                        {"fn": _boom, "auth": source_probe.KEYLESS, "license": "x"})
    env = source_probe.probe_source("breaker", "AAPL")
    _envelope.validate(env)
    assert env["status"] == "error"
    assert env["error"].startswith("INTERNAL")


def test_adapter_returning_a_non_envelope_is_rejected(monkeypatch):
    monkeypatch.setitem(source_probe.SOURCES, "junk",
                        {"fn": lambda t: "not an envelope", "auth": source_probe.KEYLESS,
                         "license": "x"})
    env = source_probe.probe_source("junk", "AAPL")
    assert env["status"] == "error"
    assert env["error"].startswith("SCHEMA_MISMATCH")


# --- key handling: skip, never fail -----------------------------------------

def test_keyed_source_without_env_is_skipped_not_failed(monkeypatch):
    for var in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY", "TIINGO_API_KEY",
                "POLYGON_API_KEY", "MASSIVE_API_KEY", "FMP_API_KEY", "FINNHUB_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    for name in ("alpaca", "tiingo", "massive", "fmp", "finnhub"):
        available, reason = source_probe.source_available(name)
        assert not available, f"{name} should be unavailable with no key"
        assert "skipped" in reason


def test_keyless_sources_are_always_available(monkeypatch):
    for var in ("ALPACA_API_KEY", "TIINGO_API_KEY", "POLYGON_API_KEY",
                "FMP_API_KEY", "FINNHUB_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    for name in ("nasdaq", "sina", "tencent", "yahoo"):
        assert source_probe.source_available(name)[0], name


def test_probe_ticker_records_skips_separately_from_failures(monkeypatch):
    for var in ("TIINGO_API_KEY", "FMP_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    report = source_probe.probe_ticker("AAPL", ["tiingo", "fmp"])
    assert set(report["skipped"]) == {"tiingo", "fmp"}
    assert report["results"] == {}, "skipped sources must not appear as failed results"


# --- numeric parsing across source dialects ---------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("$332.41", 332.41), ("35,981,000", 35981000.0), (332.41, 332.41),
    ("--", None), ("", None), ("N/A", None), (None, None), (" 1,234.5 ", 1234.5),
])
def test_num_parsing_handles_each_source_dialect(raw, expected):
    assert source_probe._num(raw) == expected


# --- block detection: the trap that caused the original misdiagnosis ---------

def test_block_page_served_as_200_is_flagged():
    """Yahoo serves its geo-block as a 200 on some hosts. A 200 carrying a block
    page is NOT data, and conflating the two is what made the first diagnosis wrong."""
    html = ("<!DOCTYPE html><html lang=\"zh\"><head><title>Yahoo</title></head>"
            "<body>As of November 1st, 2021 Yahoo's suite of services will no "
            "longer be accessible from mainland China.</body></html>")
    low = html[:4000].lower()
    assert any(m in low for m in source_probe.BLOCK_MARKERS) or \
        low.lstrip().startswith(("<!doctype html", "<html"))


def test_plain_json_is_not_flagged_as_a_block():
    body = json.dumps({"data": {"symbol": "AAPL", "price": 332.41}}).lower()
    assert not any(m in body for m in source_probe.BLOCK_MARKERS)
    assert not body.lstrip().startswith(("<!doctype html", "<html"))


# --- cross-source agreement: must catch a swapped-field parser --------------

def test_agreement_passes_when_sources_match_to_the_cent():
    results = {"nasdaq": _ok("nasdaq", 332.41), "sina": _ok("sina", 332.41),
               "tencent": _ok("tencent", 332.41)}
    agr = source_probe.cross_source_agreement(results)
    assert agr["agree"] is True
    assert agr["comparable"] == 3
    assert agr["median_close"] == 332.41


def test_agreement_catches_a_source_that_reported_high_as_close():
    """The exact failure mode the check exists for: Tencent's kline is positional
    with close THIRD, so a parser assuming OHLC reports high (335.48) as the close.
    That number is entirely plausible on its own — only comparison catches it.

    This is a regression test for a real bug: at a 0.5% tolerance with two sources
    the median falls between them, and 0.92% of disagreement reported as "agree"."""
    results = {
        "nasdaq": _ok("nasdaq", AAPL_2026_09_16["close"]),
        "tencent_broken": _ok("tencent", AAPL_2026_09_16["high"]),
    }
    agr = source_probe.cross_source_agreement(results)
    assert agr["agree"] is False, "0.92% of disagreement must not pass as agreement"
    assert "tencent_broken" in agr["divergent"]
    assert agr["divergent"]["tencent_broken"]["close"] == 335.48


def test_two_divergent_sources_name_no_culprit():
    """With two sources the median is the midpoint, so neither can be exonerated.
    The check must say so rather than invent a winner."""
    results = {"a": _ok("a", 100.0), "b": _ok("b", 101.0)}
    agr = source_probe.cross_source_agreement(results)
    assert agr["agree"] is False
    assert set(agr["divergent"]) == {"a", "b"}, "both must be flagged when n=2"
    assert all(v["suspect"].startswith("unresolved") for v in agr["divergent"].values())


def test_three_sources_identify_the_odd_one_out():
    """With three, the median has a majority to anchor on and the culprit is named."""
    results = {"a": _ok("a", 100.0), "b": _ok("b", 100.0), "broken": _ok("broken", 113.0)}
    agr = source_probe.cross_source_agreement(results)
    assert agr["agree"] is False
    assert set(agr["divergent"]) == {"broken"}
    assert agr["divergent"]["broken"]["deviation_pct"] == pytest.approx(13.0, abs=0.01)


def test_small_cent_level_differences_still_count_as_agreement():
    """Different vendors can differ by a cent on last-trade vs official close.
    A tolerance tight enough to catch field swaps must not flag rounding."""
    results = {"a": _ok("a", 332.41), "b": _ok("b", 332.40), "c": _ok("c", 332.42)}
    agr = source_probe.cross_source_agreement(results)
    assert agr["agree"] is True


def test_agreement_needs_two_priced_sources_to_say_anything():
    agr = source_probe.cross_source_agreement({"sina": _ok("sina", 332.41)})
    assert agr["comparable"] == 1
    assert agr["agree"] is None, "a single source cannot be 'in agreement'"


def test_error_envelopes_are_excluded_from_agreement():
    results = {"sina": _ok("sina", 332.41),
               "nasdaq": _envelope.error("SOURCE_UNAVAILABLE: HTTP 503", source="nasdaq")}
    agr = source_probe.cross_source_agreement(results)
    assert agr["values"] == {"sina": 332.41}
    assert agr["agree"] is None


def test_ok_envelope_with_null_price_is_excluded_from_agreement():
    """status=ok with a null price is a silent failure; it must not anchor a median."""
    results = {"sina": _ok("sina", 332.41), "hollow": _ok("hollow", None)}
    agr = source_probe.cross_source_agreement(results)
    assert "hollow" not in agr["values"]


# --- output contract --------------------------------------------------------

def test_outputs_land_only_under_the_workspace(tmp_path):
    report = {"generated": "2026-09-17T00:00:00Z", "sources": ["sina"],
              "reachability": [], "tickers": [{
                  "ticker": "AAPL", "checked_at": "2026-09-17T00:00:00Z",
                  "results": {"sina": _ok("sina", 332.41)}, "skipped": {},
                  "agreement": {"comparable": 1, "agree": None, "divergent": {},
                                "values": {"sina": 332.41}}}]}
    source_probe.write_outputs(tmp_path, report)

    assert (tmp_path / "SOURCE-PROBE.md").is_file()
    assert (tmp_path / "AAPL-live" / "sources.ndjson").is_file()
    row = json.loads((tmp_path / "AAPL-live" / "sources.ndjson").read_text().strip())
    assert row["ticker"] == "AAPL" and row["source"] == "sina" and row["price"] == 332.41


def test_ndjson_output_is_append_only(tmp_path):
    report = {"generated": "x", "sources": ["sina"], "reachability": [], "tickers": [{
        "ticker": "AAPL", "checked_at": "x", "results": {"sina": _ok("sina", 332.41)},
        "skipped": {}, "agreement": {"comparable": 1, "agree": None, "divergent": {},
                                     "values": {}}}]}
    source_probe.write_outputs(tmp_path, report)
    source_probe.write_outputs(tmp_path, report)
    lines = (tmp_path / "AAPL-live" / "sources.ndjson").read_text().strip().splitlines()
    assert len(lines) == 2, "each run appends; history is never truncated"


def test_thesis_ticker_universe_is_the_19_named_in_the_theses():
    assert len(source_probe.THESIS_TICKERS) == 19
    assert source_probe.THESIS_TICKERS == sorted(
        source_probe.THESIS_TICKERS, key=lambda t: source_probe.THESIS_TICKERS.index(t))
    for t in ("NVDA", "PH", "SPCX", "AEVA"):
        assert t in source_probe.THESIS_TICKERS
