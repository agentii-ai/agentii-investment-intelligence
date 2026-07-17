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
from pathlib import Path
from typing import Any, Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cache  # noqa: E402
import _envelope  # noqa: E402
import _sources  # noqa: E402

CATEGORY = "market"


def _real_providers() -> dict[str, Callable]:
    """Lazy import-guarded real providers. Missing deps simply omit that provider."""
    providers: dict[str, Callable] = {}
    try:
        import yfinance as yf  # noqa: F401

        def _yf(ticker: str) -> dict:
            t = yf.Ticker(ticker)
            info = getattr(t, "fast_info", None) or {}
            return {"symbol": ticker,
                    "price": getattr(info, "last_price", None) if info else None,
                    "market_cap": getattr(info, "market_cap", None) if info else None}
        providers["yfinance"] = _yf
    except ImportError:
        pass
    return providers


def get_quote(ticker: str, *, providers: Optional[dict[str, Callable]] = None,
              cache_root: Optional[Path] = None) -> dict:
    cache = _cache.FileCache(root=cache_root) if cache_root else _cache.FileCache()
    key = f"quote:{ticker}"
    hit, cached = cache.get(CATEGORY, key)
    if hit:
        return _envelope.ok(cached, source=cached.get("_source", "cache"), cache_hit=True)

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
        return _envelope.error(f"SOURCE_UNAVAILABLE: {e}", source=None)
    if data is None:
        return _envelope.error("NOT_FOUND: no data for ticker", source=used)
    data = dict(data)
    data["_source"] = used
    cache.set(CATEGORY, key, data)
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
