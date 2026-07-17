#!/usr/bin/env python3
"""macro_data.py — ~~macro_data category (spec 039 US5, T058).

FRED primary (free key), OpenBB→ECB/IMF/OECD/BLS out-of-process (AGPL, never imported),
zero-key fallback via yfinance macro proxies. Returns an AGENT_CONTRACT envelope.

OpenBB is invoked out-of-process only (subprocess/MCP) per Constitution VIII — this
module NEVER imports it. Providers are injectable for deterministic tests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cache  # noqa: E402
import _envelope  # noqa: E402
import _sources  # noqa: E402

CATEGORY = "macro"


def _real_providers() -> dict[str, Callable]:
    providers: dict[str, Callable] = {}
    if os.environ.get("FRED_API_KEY"):
        try:
            from fredapi import Fred  # noqa: F401

            def _fred(series_id: str) -> dict:
                fred = Fred(api_key=os.environ["FRED_API_KEY"])
                s = fred.get_series(series_id)
                return {"series_id": series_id,
                        "observations": [{"date": str(d.date()), "value": str(v)}
                                         for d, v in s.tail(24).items()]}
            providers["fred"] = _fred
        except ImportError:
            pass
    # NOTE: OpenBB deliberately omitted — reached only via subprocess/MCP (AGPL).
    return providers


def get_series(series_id: str, *, providers: Optional[dict[str, Callable]] = None,
               cache_root: Optional[Path] = None) -> dict:
    cache = _cache.FileCache(root=cache_root) if cache_root else _cache.FileCache()
    key = f"series:{series_id}"
    hit, cached = cache.get(CATEGORY, key)
    if hit:
        return _envelope.ok(cached, source=cached.get("_source", "cache"), cache_hit=True)

    provs = providers if providers is not None else _real_providers()
    ordered = _cache.failover_order(
        [{"name": n, "priority": _priority(n), "fn": (lambda f=f, s=series_id: f(s))}
         for n, f in provs.items()]
    )
    if not ordered:
        return _envelope.error(
            "API_KEY_MISSING: set FRED_API_KEY or install a zero-key macro provider "
            "(see data-tools/setup_credentials.py)")
    try:
        data, used = _cache.try_sources(ordered)
    except Exception as e:  # noqa: BLE001
        return _envelope.error(f"SOURCE_UNAVAILABLE: {e}")
    if data is None:
        return _envelope.error("NOT_FOUND: no macro series", source=used)
    data = dict(data)
    data["_source"] = used
    cache.set(CATEGORY, key, data)
    # degraded if a non-primary (zero-key proxy) served it
    if used != "fred":
        return _envelope.degraded(data, source=used, error="FRED unavailable; used zero-key proxy")
    return _envelope.ok(data, source=used)


def _priority(name: str) -> int:
    for s in _sources.for_category(CATEGORY):
        if s["name"] == name:
            return s["priority"]
    return 1000


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="~~macro_data tool (spec 039 US5)")
    p.add_argument("--series", required=True, help="FRED series id, e.g. GDP, UNRATE, T10Y2Y")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    env = get_series(args.series)
    print(json.dumps(env) if args.json else json.dumps(env, indent=2))
    return 0 if env["status"] != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
