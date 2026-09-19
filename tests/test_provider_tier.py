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
import re
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


# ── T201: the egress scope is a CONSTRAINT, not a comment ───────────────────

# T183 corrected `_sources.py` and `contracts/SOURCES.md` to say the Chinese
# firewall is out of scope. Three files kept asserting the opposite, and the one a
# reader trusts is whichever they open: `source_probe.py`'s `probe_yahoo` docstring
# read "Yahoo geo-blocks this network", its registry entry labelled the licence
# "Apache-2.0 (geo-blocked)", and its module docstring stated the failure "is in
# fact a geographic block". Each is true of one measured network (Shenzhen, egress
# 113.84.64.112) and false of the product.
_SCOPE_FILES = [
    ROOT / "data-tools" / "source_probe.py",
    ROOT / "data-tools" / "_sources.py",
    ROOT / "data-tools" / "market_data.py",
    ROOT / "contracts" / "SOURCES.md",
]

# An ASSERTION of the retired premise: a present-tense claim that the block occurs,
# or a region baked into a non-region field. A correction note that QUOTES the old
# wording is correct and must keep passing, so each pattern is anchored on the
# asserting form rather than on the words.
_RETIRED_ASSERTIONS = [
    (re.compile(r"geo-blocks this network", re.I), "asserts the block as a current fact"),
    (re.compile(r'"license"\s*:\s*"[^"]*geo[- ]?block', re.I), "geo-block in a licence field"),
    (re.compile(r"is in fact a geographic block", re.I), "states the block as the diagnosis"),
    (re.compile(r"\bmust fail\b.*geo-?block", re.I), "expects a geo-block"),
]


def test_no_shipped_file_asserts_the_retired_cn_premise():
    """The scope is a product constraint, so violating it is a defect, not a wording
    preference.

    Asserted across the data-layer files rather than against the one docstring that
    was noticed, because the correction only landed in two of five places the first
    time. A grep-shaped test is the right instrument here: the failure mode is a
    sentence, and it comes back by being copied.

    **A correction note must be allowed to quote what it corrects** — Check 39 hit
    exactly this and named it: *a pattern that matches its own definition is not a
    finding*. `source_probe.probe_yahoo`'s docstring now reads *"This docstring used
    to read `Yahoo geo-blocks this network`"*, and the first version of this test
    failed on it. So a line carrying a retrospective marker is excluded: the record
    of a correction is the one place the corrected wording has to appear.
    """
    retro = re.compile(r"used to read|previously|formerly|was changed|no longer|"
                       r"out of scope|retired|T201", re.I)
    offenders: list[str] = []
    for path in _SCOPE_FILES:
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if retro.search(line):
                continue
            for rx, why in _RETIRED_ASSERTIONS:
                if rx.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{n} ({why}): {line.strip()[:90]}")

    assert not offenders, (
        "the Chinese firewall is OUT OF SCOPE (the user's stated constraint: our users "
        "are in the US and the EU). These lines assert it as a product behaviour:\n  "
        + "\n  ".join(offenders))


def test_the_probe_classifies_what_it_sees_rather_than_what_it_expects():
    """`GEO_BLOCK` and `RATE_LIMITED` are separate outcomes, and 429 is not a block.

    Before T201 the classifier was `GEO_BLOCK if blocked and status == 403 else
    SOURCE_UNAVAILABLE` — so the in-scope failure (a US-datacenter 429) was reported
    under a name that says "geography", which is how a scope decision gets silently
    reversed by a status-code branch. The kind now names the mechanism observed.
    """
    import inspect
    src = inspect.getsource(sp.probe_yahoo)
    assert "RATE_LIMITED" in src, (
        "a 429 must be reported as a throttle, not folded into the geo-block branch")
    assert '"GEO_BLOCK"' in src
