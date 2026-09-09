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
    """Lazy import-guarded real providers. Missing deps simply omit that provider."""
    providers: dict[str, Callable] = {}
    try:
        import yfinance as yf  # noqa: F401

        def _yf(ticker: str) -> dict:
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
                    "data_class": "fast"}
        providers["yfinance"] = _yf

        def _yf_history(ticker: str, *, period: str = "1y", interval: str = "1d") -> dict:
            """Q42: the history-capable provider — daily OHLCV bars from
            history()'s tz-aware NY index (the quote provider cannot serve bars)."""
            t = yf.Ticker(ticker)
            hist = t.history(period=period, interval=interval)
            bars = []
            observed_at = None
            for idx, row in hist.iterrows():
                close = row.get("Close")
                if close is None:
                    continue  # None-vs-0 semantics: missing rows dropped, never zeroed
                bars.append({"date": str(idx.date()), "open": float(row["Open"]),
                             "high": float(row["High"]), "low": float(row["Low"]),
                             "close": float(close), "volume": int(row.get("Volume") or 0)})
                observed_at = idx.isoformat() if hasattr(idx, "isoformat") else str(idx)
            return {"symbol": ticker, "bars": bars, "observed_at": observed_at}
        providers["yfinance_history"] = _yf_history
    except ImportError:
        pass
    return providers


def get_price_history(ticker: str, *, period: str = "1y", interval: str = "1d",
                      providers: Optional[dict[str, Callable]] = None,
                      cache_root: Optional[Path] = None) -> dict:
    """Q42: daily OHLCV bars for `early`-class skills. Fewer than 20 bars ⇒
    INSUFFICIENT_HISTORY (SMA(20) is the minimum computable window)."""
    provs = providers if providers is not None else _real_providers()
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

    provs = providers if providers is not None else _real_providers()
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
