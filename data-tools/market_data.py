#!/usr/bin/env python3
"""market_data.py — ~~market_data category (spec 039 US5, T059).

Zero-key-first: yfinance (Apache-2.0) is the default, no API key. secfin/investpy
zero-key; Finnhub/Polygon keyed. Returns an AGENT_CONTRACT envelope.

Providers are import-guarded and injectable (tests pass fakes; real runs lazy-import).
License: MIT/permissive only — no copyleft imports (check.py Check 30b).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cache  # noqa: E402
import _envelope  # noqa: E402
import _sources  # noqa: E402
import refusal  # noqa: E402 — shared data-layer refusal surface (Q6-A)

CATEGORY = "market"
NY_TZ = ZoneInfo("America/New_York")  # Q65: the system clock for market data


def _now_ny() -> str:
    return datetime.now(NY_TZ).isoformat()


def _real_providers() -> dict[str, Callable]:
    """The adapter chain (T178), in registry-priority order.

    TWO SOURCES OF ADAPTERS, and the split is deliberate:

      * **probe adapters** (`source_probe.py`) serve nasdaq / sina / tencent and
        the four keyed sources. That file MEASURES sources — its own docstring
        says so: *"source_probe.py (30 KB, built) MEASURES sources; today nothing
        SERVES from them."* Writing fresh fetchers here would be a second
        implementation of nine working adapters, which is the divergence Q12 rule
        3 forbids, and the measured one would win the argument anyway.
      * **the yfinance module adapter** below is retained as the NEGATIVE CONTROL
        (T181). It is tried LAST (registry priority 90), and its assertion is that
        it fails CLEANLY. `source_probe`'s own `yahoo` probe is deliberately NOT
        registered here: that is the measurement instrument, this is the serving
        path, and two adapters for one source is the same divergence.

    A source whose key is unset is **omitted, not failed** — T180: the zero-key
    path must always work, and reporting a missing key as a failure makes a
    working keyless deployment look like an outage. The omitted set is reportable
    via `skipped_sources()` so the two cases stay distinguishable.
    """
    import source_probe as sp

    providers: dict[str, Callable] = {}

    def _unwrap(name: str):
        def fn(t: str) -> dict:
            env = sp.probe_source(name, t)
            if env.get("status") == "ok" and isinstance(env.get("data"), dict):
                return env["data"]
            raise RuntimeError(env.get("error") or f"{name}: no data")
        return fn

    for name in sp.SOURCES:
        if name == "yahoo":
            continue                       # the measurement instrument, not serving
        available, _reason = sp.source_available(name)
        if not available:
            continue                       # SKIPPED: absent, not broken (T180)
        providers[name] = _unwrap(name)

    try:
        import yfinance as yf  # noqa: F401

        providers["yfinance"] = _yf
        providers["yfinance_history"] = _yf_history
    except ImportError:
        pass                               # absent dependency omits the source
    return providers


def _caps_of(name: str) -> list[str]:
    """What this provider can SERVE. `_real_providers` registers names, and a
    name alone cannot answer 'can you serve bars?' — which is D1/D-capability:
    `get_price_history` took the first provider that did not raise, so a
    quote-only source answered history calls with a quote-shaped payload and
    `data.get("bars")` was always []. Live symptom, measured 2026-09-18 after
    the chain was wired: `INSUFFICIENT_HISTORY: 0 bars < 20`."""
    if name == "yfinance_history":
        return ["bars"]
    if name == "yfinance":
        # QUOTE ONLY. D1's whole point is that `_yf` returns quote-shaped data and
        # `data.get("bars")` is always [] — declaring it bars-capable would let it
        # answer a history call with a quote, which is the defect, not the fix.
        return ["quote"]
    try:
        import source_probe as sp
        return list((sp.SOURCES.get(name) or {}).get("caps") or [])
    except ImportError:
        return []


def _capable(provs: dict[str, Callable], need: str) -> dict[str, Callable]:
    """Filter the chain to providers that can serve `need`, preserving order.

    An UNKNOWN capability is excluded rather than assumed: a provider that has
    not declared what it serves is exactly the one that will answer the wrong
    question. Injected test providers are the exception — a dict passed directly
    to `get_quote`/`get_price_history` is the caller's explicit choice, so
    `_capable` is only applied to the registry-derived chain."""
    out = {}
    for name, fn in provs.items():
        caps = _caps_of(name)
        if need in caps:
            out[name] = fn
    return out


def skipped_sources() -> list[str]:
    """The sources that are declared but not attempted, and why.

    T180: this exists so the SKIPPED set is REPORTABLE. Without it the difference
    between 'no key on this machine' and 'the data layer is down' is invisible,
    and the first — the normal case, since five of nine sources take no key —
    would read as the second."""
    import source_probe as sp

    out = []
    for name in sp.SOURCES:
        available, reason = sp.source_available(name)
        if not available:
            out.append(reason)
    return out


def _yf(ticker: str) -> dict:
    """The negative control's adapter (T181), restored VERBATIM from the original.

    Restored because my first rewrite silently changed behaviour: I renamed these
    `getattr` keys to snake_case, which made `test_adapter_extracts_supplementary_
    fields_from_fast_info` XPASS against its fake — and with `strict`, an XPASS is
    a failure. The test was right and my rewrite was wrong: D2's whole point is
    that these are the CAMELCASE names yfinance exposes, that `FastInfo` has no
    `__getattr__`, and that 6 of 9 quote fields are therefore permanently None in
    production. Touching them to make a test go green would have hidden D2."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    info = getattr(t, "fast_info", None) or {}
    # Q71/R3: the pinnable price is history()'s daily close — fast_info
    # exposes NO timestamp, so last_price is structurally unusable for
    # pinned artifacts. observed_at comes from history()'s tz-aware NY index.
    price = None
    observed_at = None
    try:
        hist = t.history(period="2d")
        if hist is not None and len(hist) > 0:
            price = float(hist.iloc[-1]["Close"])
            idx = hist.index[-1]
            observed_at = idx.isoformat() if hasattr(idx, "isoformat") else str(idx)
    except Exception:  # noqa: BLE001 — history failure degrades to refusal
        pass
    # T076: field-by-field growth — each supplementary field available in
    # fast_info today (contract rows flipped 🔜→✅ in get-realtime-quote-tool.md).
    market_cap = getattr(info, "market_cap", None) if info else None
    return {"symbol": ticker,
            "price": price,
            "market_cap": int(market_cap) if market_cap is not None else None,
            # verified fast_info key names (R3, live yfinance 1.4.1)
            "day_high": getattr(info, "dayHigh", None) if info else None,
            "day_low": getattr(info, "dayLow", None) if info else None,
            "open": getattr(info, "open", None) if info else None,
            "previous_close": getattr(info, "previousClose", None) if info else None,
            "volume": getattr(info, "lastVolume", None) if info else None,
            "ma_50": getattr(info, "fiftyDayAverage", None) if info else None,
            "observed_at": observed_at,
            "price_basis": "close",  # RISK-2: intraday needs a second source
            "data_class": "fast",
            "source": "yfinance"}


def _yf_history(ticker: str, period: str = "1y", interval: str = "1d") -> dict:
    """Q42: the history-capable provider — daily OHLCV bars from history()'s
    tz-aware NY index (the quote provider cannot serve bars)."""
    import yfinance as yf

    hist = yf.Ticker(ticker).history(period=period, interval=interval)
    bars = []
    if hist is not None:
        for idx, row in hist.iterrows():
            bars.append({"date": idx.isoformat() if hasattr(idx, "isoformat") else str(idx),
                         "open": float(row["Open"]), "high": float(row["High"]),
                         "low": float(row["Low"]), "close": float(row["Close"]),
                         "volume": float(row["Volume"])})
    return {"symbol": ticker, "bars": bars, "source": "yfinance_history"}


def get_price_history(ticker: str, *, period: str = "1y", interval: str = "1d",
                      providers: Optional[dict[str, Callable]] = None,
                      cache_root: Optional[Path] = None) -> dict:
    """Q42: daily OHLCV bars for `early`-class skills. Fewer than 20 bars ⇒
    INSUFFICIENT_HISTORY (SMA(20) is the minimum computable window)."""
    # CAPABILITY-FILTERED (2026-09-18). Without this the loop takes the first
    # provider that does not raise, and D1's TypeError branch re-invokes a
    # quote-shaped adapter with one positional arg — it succeeds, and the result
    # is `0 bars`. Measured live the moment the chain was wired:
    # `INSUFFICIENT_HISTORY: 0 bars < 20`.
    #
    # MEASURED CONSEQUENCE, recorded because it is a finding and not a detail:
    # this narrows the bars chain to ONE provider, `yfinance_history`, and its
    # upstream is the source measured as failing. Every probe adapter returns a
    # QUOTE payload — nasdaq and sina FETCH daily rows but expose only the last
    # close — so no keyless source can serve bars today. History is the thinner
    # half of the serving path and this says so.
    provs = providers if providers is not None else _capable(_real_providers(), "bars")
    data = None
    used = None
    last_err: str | None = None
    for name, fn in provs.items():
        try:
            data = fn(ticker, period=period, interval=interval)
            used = name
            break
        except TypeError:
            try:
                data = fn(ticker)
                used = name
                break
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
                continue
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            continue
    if data is None:
        reason = f" ({last_err})" if last_err else " (no providers installed)"
        return _envelope.error(f"SOURCE_UNAVAILABLE: all providers failed{reason}")
    bars = data.get("bars") or []
    if len(bars) < 20:
        return _envelope.error(
            f"INSUFFICIENT_HISTORY: {len(bars)} bars < 20 (SMA(20) minimum, Q42)",
            source=used)
    out = {"ticker": ticker, "period": period, "interval": interval,
           "bars": bars, "observed_at": data.get("observed_at"),
           "retrieved_at": _now_ny(), "source": used}
    cache = _cache.FileCache(root=cache_root) if cache_root else _cache.FileCache()
    cache.set(CATEGORY, f"history:{ticker}:{period}:{interval}", out,
              ttl=_cache.DATA_TYPE_TTL["history"])
    return _envelope.ok(out, source=used)


def get_quote(ticker: str, *, providers: Optional[dict[str, Callable]] = None,
              cache_root: Optional[Path] = None) -> dict:
    cache = _cache.FileCache(root=cache_root) if cache_root else _cache.FileCache()
    key = f"quote:{ticker}"
    hit, cached, meta = cache.get_meta(CATEGORY, key)
    if hit:
        # Q71: cache_age_seconds from the previously-discarded stored_at.
        age = cache.clock() - meta["stored_at"]
        data = dict(cached)
        data["cache_age_seconds"] = age
        return _envelope.ok(data, source=cached.get("_source", "cache"), cache_hit=True)

    provs = providers if providers is not None else _capable(_real_providers(), "quote")
    # order provider callables by registry priority
    ordered = _cache.failover_order(
        [{"name": n, "priority": _priority(n), "fn": (lambda f=f, t=ticker: f(t))}
         for n, f in provs.items()]
    )
    if not ordered:
        return _envelope.error("SOURCE_UNAVAILABLE: no market providers installed (pip install yfinance)")
    try:
        data, used = _cache.try_sources(ordered)
    except Exception as e:  # noqa: BLE001
        # Q44 fallback: provider unreachable → serve the newest stale entry with
        # stale: true (the consumer-side 24h gate decides usability, Q41).
        has_stale, stale_data, stale_meta = cache.get_stale(CATEGORY, key)
        if has_stale and stale_data:
            served = dict(stale_data)
            served["stale"] = True
            served["cache_age_seconds"] = cache.clock() - stale_meta["stored_at"]
            return _envelope.degraded(served, source=stale_data.get("_source", "cache"),
                                      error=f"SOURCE_UNAVAILABLE: {e}", cache_hit=True)
        return _envelope.error(f"SOURCE_UNAVAILABLE: {e}", source=None)
    if data is None:
        return _envelope.error("NOT_FOUND: no data for ticker", source=used)
    data = dict(data)
    # contract conformance at the envelope boundary: market_cap is int per
    # get-realtime-quote-tool.md (the provider returns a float with fractional cents)
    if isinstance(data.get("market_cap"), float):
        data["market_cap"] = int(data["market_cap"])
    # Q71 hard rule at the data layer: a quote lacking observed_at may not be used
    # in any pinned artifact — refuse it structurally rather than warn.
    refusal_env = refusal.require_observed_at(data)
    if refusal_env is not None:
        return refusal_env
    data["_source"] = used
    data["retrieved_at"] = _now_ny()
    cache.set(CATEGORY, key, data, ttl=_cache.DATA_TYPE_TTL["quote"])
    return _envelope.ok(data, source=used)


def _priority(name: str) -> int:
    for s in _sources.for_category(CATEGORY):
        if s["name"] == name:
            return s["priority"]
    return 1000


def _offline_fixture(ticker: str) -> dict:
    return {"symbol": ticker, "price": 0.0, "market_cap": None, "note": "offline fixture"}


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="~~market_data tool (spec 039 US5)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--offline-fixture", action="store_true", help="deterministic offline envelope (CI)")
    args = p.parse_args(argv)

    if args.offline_fixture:
        env = _envelope.degraded(_offline_fixture(args.ticker), source="yfinance",
                                 error="offline fixture mode")
    else:
        env = get_quote(args.ticker)
    print(json.dumps(env) if args.json else json.dumps(env, indent=2))
    return 0 if env["status"] != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
