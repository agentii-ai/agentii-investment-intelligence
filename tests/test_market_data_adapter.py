"""L1–L3: the provider adapter seam (`_real_providers()`) — defects D1, D2, D5.

WHY THIS FILE EXISTS
--------------------
Every pre-existing market-data test injects a *fake provider dict* whose callables
already return correctly-shaped data. That proves the pass-through works. It never
exercises `_real_providers()` — the closures that actually read `yfinance` objects,
and therefore the only code in the package that touches reality.

The tests below close that gap. They install a faithful `yfinance` stub into
`sys.modules` and then call the REAL `_real_providers()`. The stub matters: it
replicates `yfinance.scrapers.quote.FastInfo`'s actual access protocol, which is
the crux of D2 —

    FastInfo exposes snake_case names as real properties (`day_high`,
    `last_volume`, `fifty_day_average`, ...) and accepts camelCase names ONLY
    through `__getitem__`, which maps camel -> snake before delegating to
    getattr. FastInfo defines NO `__getattr__`.

So `info["dayHigh"]` works and `getattr(info, "dayHigh", None)` silently returns
None. `market_data.py` lines 63-68 use the getattr form. Six of nine quote fields
are therefore always None in production, while the contract marks them delivered.

These are deterministic and network-free, so they run in CI on any machine.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import market_data  # noqa: E402
import _sources  # noqa: E402


# --- a faithful yfinance stub -------------------------------------------------

def _snake_to_camel(name: str) -> str:
    head, *tail = name.split("_")
    return head + "".join(w.capitalize() for w in tail)


def _make_fast_info(values: dict):
    """Replica of yfinance's FastInfo.

    Snake_case names are real class properties; camelCase names resolve only
    through __getitem__. There is deliberately NO __getattr__ — that absence is
    exactly what D2 turns on, so the stub must preserve it.
    """
    cls = type("FastInfo", (), {})
    for key in values:
        setattr(cls, key, property(lambda self, _k=key: self._v[_k]))

    def __init__(self, v):
        self._v = v
        self._cc = {_snake_to_camel(k): k for k in v if "_" in k}
        self._keys = sorted(list(v) + list(self._cc))

    def __getitem__(self, k):
        if k not in self._keys:
            raise KeyError(f"'{k}' not valid key. Examine 'FastInfo.keys()'")
        return getattr(self, self._cc.get(k, k))

    def keys(self):
        return self._keys

    cls.__init__ = __init__
    cls.__getitem__ = __getitem__
    cls.keys = keys
    return cls(values)


# The canonical values the contract's own example response documents
# (contracts/get-realtime-quote-tool.md — the LLY sample).
FAST_INFO_VALUES = {
    "last_price": 850.25,
    "market_cap": 810500000000,
    "day_high": 855.50,
    "day_low": 845.00,
    "open": 847.10,
    "previous_close": 849.00,
    "last_volume": 3200000,
    "fifty_day_average": 820.30,
}

# A tz-aware NY daily index, as yfinance's history() returns (2 rows => period="2d").
HIST_INDEX = pd.DatetimeIndex(
    pd.to_datetime(["2026-09-07 00:00", "2026-09-08 00:00", "2026-09-09 00:00"])
).tz_localize("America/New_York")
HIST_ROWS = [
    {"Open": 128.5, "High": 131.2, "Low": 127.1, "Close": 130.4, "Volume": 52_000_000},
    {"Open": 131.0, "High": 133.4, "Low": 130.2, "Close": 132.8, "Volume": 48_000_000},
]
LAST_CLOSE = HIST_ROWS[-1]["Close"]


def _install_fake_yfinance(monkeypatch, *, n_hist_rows: int = 2, hist: pd.DataFrame | None = None):
    """Install a module that satisfies `import yfinance as yf` inside _real_providers()."""
    frame = hist if hist is not None else pd.DataFrame(HIST_ROWS[:n_hist_rows], index=HIST_INDEX[:n_hist_rows])

    class Ticker:
        def __init__(self, symbol):
            self.symbol = symbol
            self.fast_info = _make_fast_info(FAST_INFO_VALUES)

        def history(self, period=None, interval=None, **kwargs):
            if interval in ("1d", None) and period not in ("2d", None):
                # A real longer-period request returns more rows; the stub returns
                # the same frame so bar-count assertions stay deterministic.
                return frame
            return frame

    fake = types.ModuleType("yfinance")
    fake.Ticker = Ticker
    fake.__version__ = "0.0.0-stub"
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    return fake


# --- L1: the adapter produces the fields the contract declares ---------------

@pytest.mark.xfail(strict=True, reason=(
    "D2: market_data.py:63-68 reads fast_info via getattr(info, 'dayHigh') etc., "
    "but FastInfo has no __getattr__ — only camel->snake __getitem__. 6 of 9 "
    "quote fields are permanently None in production."))
def test_adapter_extracts_supplementary_fields_from_fast_info(monkeypatch, tmp_path):
    """Every field the contract marks delivered must carry a real value."""
    _install_fake_yfinance(monkeypatch)
    # UPDATED 2026-09-18 (T178/T179). These tests exercise the YFINANCE adapter
    # specifically, and used to reach it by calling `_real_providers()` and
    # relying on it returning nothing else — i.e. they depended on D5 ("the
    # failover chain has exactly one real source"). Wiring the chain to the
    # measured adapters put nasdaq at priority 30 and yfinance at 90, so the real
    # HTTP adapter ran first and the injected fake was never reached. Requesting
    # the adapter by name is both correct and order-independent.
    providers = {"yfinance": market_data._yf,
                 "yfinance_history": market_data._yf_history}
    assert providers, "expected at least one real provider to be constructed"

    env = market_data.get_quote("LLY", providers=providers, cache_root=tmp_path)
    assert env["status"] == "ok", env.get("error")
    d = env["data"]

    assert d["day_high"] == pytest.approx(FAST_INFO_VALUES["day_high"])
    assert d["day_low"] == pytest.approx(FAST_INFO_VALUES["day_low"])
    assert d["previous_close"] == pytest.approx(FAST_INFO_VALUES["previous_close"])
    assert d["volume"] == FAST_INFO_VALUES["last_volume"]
    assert d["ma_50"] == pytest.approx(FAST_INFO_VALUES["fifty_day_average"])


def test_adapter_extracts_the_fields_that_do_work_today(monkeypatch, tmp_path):
    """Guard against a fix that breaks what already resolves.

    `market_cap` (snake_case property) and `open` (no underscore, so a real
    property) are the two that work today. They must keep working."""
    _install_fake_yfinance(monkeypatch)
    # UPDATED 2026-09-18 (T178/T179). These tests exercise the YFINANCE adapter
    # specifically, and used to reach it by calling `_real_providers()` and
    # relying on it returning nothing else — i.e. they depended on D5 ("the
    # failover chain has exactly one real source"). Wiring the chain to the
    # measured adapters put nasdaq at priority 30 and yfinance at 90, so the real
    # HTTP adapter ran first and the injected fake was never reached. Requesting
    # the adapter by name is both correct and order-independent.
    providers = {"yfinance": market_data._yf,
                 "yfinance_history": market_data._yf_history}
    env = market_data.get_quote("LLY", providers=providers, cache_root=tmp_path)
    d = env["data"]
    assert d["market_cap"] == FAST_INFO_VALUES["market_cap"]
    assert d["open"] == pytest.approx(FAST_INFO_VALUES["open"])


def test_real_adapter_emits_every_documented_key(monkeypatch, tmp_path):
    """The real adapter always emits the full key set (values may be None). This is
    the contract-conformance property that a provider-agnostic normalization step
    would need to reproduce for injected providers — see D-contract in
    test_market_data_gates.py."""
    _install_fake_yfinance(monkeypatch)
    # UPDATED 2026-09-18 (T178/T179). These tests exercise the YFINANCE adapter
    # specifically, and used to reach it by calling `_real_providers()` and
    # relying on it returning nothing else — i.e. they depended on D5 ("the
    # failover chain has exactly one real source"). Wiring the chain to the
    # measured adapters put nasdaq at priority 30 and yfinance at 90, so the real
    # HTTP adapter ran first and the injected fake was never reached. Requesting
    # the adapter by name is both correct and order-independent.
    providers = {"yfinance": market_data._yf,
                 "yfinance_history": market_data._yf_history}
    env = market_data.get_quote("LLY", providers=providers, cache_root=tmp_path)
    d = env["data"]
    for key in ("symbol", "price", "market_cap", "day_high", "day_low", "open",
                "previous_close", "volume", "ma_50", "observed_at", "price_basis",
                "data_class"):
        assert key in d, f"real adapter omitted contract field {key!r}"
    assert d["data_class"] == "fast"
    assert d["price_basis"] == "close"


def test_pinnable_price_comes_from_history_not_fast_info(monkeypatch, tmp_path):
    """Q71/R3: `last_price` is structurally unusable (no timestamp). The pinnable
    value must be history()'s daily close, so this is a binding constraint on any
    fix for D2 — do not 'fix' it by adopting fast_info.last_price."""
    _install_fake_yfinance(monkeypatch)
    # UPDATED 2026-09-18 (T178/T179). These tests exercise the YFINANCE adapter
    # specifically, and used to reach it by calling `_real_providers()` and
    # relying on it returning nothing else — i.e. they depended on D5 ("the
    # failover chain has exactly one real source"). Wiring the chain to the
    # measured adapters put nasdaq at priority 30 and yfinance at 90, so the real
    # HTTP adapter ran first and the injected fake was never reached. Requesting
    # the adapter by name is both correct and order-independent.
    providers = {"yfinance": market_data._yf,
                 "yfinance_history": market_data._yf_history}
    env = market_data.get_quote("LLY", providers=providers, cache_root=tmp_path)
    d = env["data"]
    assert d["price"] == pytest.approx(LAST_CLOSE)
    assert d["price"] != pytest.approx(FAST_INFO_VALUES["last_price"])
    assert d["observed_at"]
    assert str(HIST_INDEX[-1].year) in d["observed_at"]


# --- L2: provider selection and failover -------------------------------------

@pytest.mark.xfail(strict=True, reason=(
    "D1: get_price_history iterates the provider dict in insertion order, so the "
    "QUOTE provider (signature `_yf(ticker)`) is tried first; the TypeError branch "
    "re-invokes it with one positional arg, it succeeds returning quote-shaped "
    "data, and `data.get('bars')` is always []. The tool can never return bars."))
def test_price_history_returns_bars_with_real_providers(monkeypatch, tmp_path):
    """The headline defect: with the real provider dict, get_price_history is dead."""
    _install_fake_yfinance(monkeypatch)
    # UPDATED 2026-09-18 (T178/T179). These tests exercise the YFINANCE adapter
    # specifically, and used to reach it by calling `_real_providers()` and
    # relying on it returning nothing else — i.e. they depended on D5 ("the
    # failover chain has exactly one real source"). Wiring the chain to the
    # measured adapters put nasdaq at priority 30 and yfinance at 90, so the real
    # HTTP adapter ran first and the injected fake was never reached. Requesting
    # the adapter by name is both correct and order-independent.
    providers = {"yfinance": market_data._yf,
                 "yfinance_history": market_data._yf_history}

    env = market_data.get_price_history("LLY", period="1y", interval="1d",
                                        providers=providers, cache_root=tmp_path)
    assert env["status"] == "ok", (
        f"get_price_history must return bars with the real provider set; got "
        f"{env.get('error')!r}"
    )
    assert env["data"]["bars"], "bars must be non-empty"


def test_price_history_rejects_a_quote_shaped_provider(monkeypatch, tmp_path):
    """The inverse guard: if a provider cannot serve bars, that must surface as an
    error, not be silently accepted as an empty history."""
    quote_only = {"quote_only": lambda t: {"symbol": t, "price": 1.0,
                                           "observed_at": "2026-09-09T16:00:00-04:00"}}
    env = market_data.get_price_history("LLY", providers=quote_only, cache_root=tmp_path)
    assert env["status"] == "error"
    assert env["error"].startswith("INSUFFICIENT_HISTORY")


@pytest.mark.xfail(strict=True, reason=(
    "D-capability: the mirror of D1. get_quote also selects providers by priority "
    "and insertion order, never by capability, so a bars-shaped provider listed "
    "first is accepted as a quote. Selection is argument-blind in both directions."))
def test_quote_rejects_a_bars_shaped_provider(tmp_path):
    """A provider that cannot serve a quote must not be accepted as one.

    Downstream this is worse than D1: a bars payload carries no `price`, so the
    consumer either KeyErrors or treats a missing price as null."""
    bars_only = {"bars_only": lambda t, period="1y", interval="1d": {
        "symbol": t, "bars": [{"date": "2026-09-09", "open": 1.0, "high": 2.0,
                               "low": 0.5, "close": 1.5, "volume": 1}],
        "observed_at": "2026-09-09T16:00:00-04:00"}}

    env = market_data.get_quote("LLY", providers=bars_only, cache_root=tmp_path)

    if env["status"] == "ok":
        # If it is accepted, the payload must still satisfy the quote contract.
        assert "price" in env["data"], (
            "a bars-shaped provider was accepted as a quote and the payload has no "
            "'price' key — the consumer cannot tell this from a data outage"
        )
    else:
        assert env["error"].startswith(("SOURCE_UNAVAILABLE", "NOT_FOUND"))


@pytest.mark.xfail(strict=True, reason=(
    "D5: _sources.py declares secfin/investpy/finnhub for category 'market' "
    "(plus Polygon in contracts/SOURCES.md) but _real_providers() implements "
    "only yfinance. The failover chain has exactly one real source."))
def test_every_declared_market_source_is_implemented(monkeypatch):
    """A registry that over-declares turns single-provider outages into total
    outages, because the failover the design promises cannot occur."""
    _install_fake_yfinance(monkeypatch)
    implemented = set(market_data._real_providers())
    # `yfinance_history` is the history-capable closure for the yfinance source.
    implemented = {n.replace("_history", "") for n in implemented}

    declared = {s["name"] for s in _sources.for_category("market")}
    missing = declared - implemented
    assert not missing, (
        f"registry declares market sources with no implementation: {sorted(missing)}"
    )


# --- L3: bar invariants ------------------------------------------------------

def test_history_bars_are_ascending_without_none_closes(monkeypatch, tmp_path):
    """The contract's None-vs-0 rule: rows with a missing close are dropped, never
    zero-filled. A zero is a price; a None is an absence."""
    frame = pd.DataFrame(
        [
            {"Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5, "Volume": 100},
            {"Open": 10.5, "High": 12.0, "Low": 10.0, "Close": None, "Volume": 200},
            {"Open": 11.0, "High": 12.5, "Low": 10.5, "Close": 12.0, "Volume": 300},
        ],
        index=HIST_INDEX[:3],
    )
    _install_fake_yfinance(monkeypatch, hist=frame)

    # Call the history closure directly: this asserts the bar-shaping contract
    # independently of the D1 selection bug.
    bar_provider = market_data._real_providers().get("yfinance_history")
    assert bar_provider is not None, "the history-capable provider must exist"
    out = bar_provider("LLY", period="1y", interval="1d")

    bars = out["bars"]
    assert all(b["close"] is not None for b in bars)
    assert 0.0 not in [b["close"] for b in bars]
    assert [b["date"] for b in bars] == sorted(b["date"] for b in bars)
