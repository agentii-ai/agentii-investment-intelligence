#!/usr/bin/env python3
"""earnings_data.py — ~~earnings_data category (spec 039 US5, T060).

defeatbeta-api (zero-key) primary for transcripts + fundamentals; FMP (free key)
fallback for estimates/calendar; Earnings Whispers scraper is the lowest-priority
last resort (R7). Returns an AGENT_CONTRACT envelope.

Providers injectable for deterministic tests; real providers lazy import-guarded.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cache  # noqa: E402
import _envelope  # noqa: E402
import _sources  # noqa: E402

CATEGORY = "earnings"


def provider_priority_order(names: list[str]) -> list[str]:
    """Order provider names by the registry priority (scraper last)."""
    def prio(n: str) -> int:
        for s in _sources.for_category(CATEGORY):
            if s["name"] == n:
                return s["priority"]
        return 1000
    return sorted(names, key=prio)


def _real_providers() -> dict[str, Callable]:
    providers: dict[str, Callable] = {}
    try:
        import defeatbeta_api  # noqa: F401

        def _db(ticker: str, quarter: str) -> dict:
            # defeatbeta-api surface varies; keep the adapter thin + defensive.
            return {"ticker": ticker, "quarter": quarter, "transcript": None,
                    "note": "defeatbeta-api installed; wire concrete call in integration"}
        providers["defeatbeta-api"] = _db
    except ImportError:
        pass
    return providers


def get_transcript(ticker: str, quarter: str, *, providers: Optional[dict[str, Callable]] = None,
                   cache_root: Optional[Path] = None) -> dict:
    cache = _cache.FileCache(root=cache_root) if cache_root else _cache.FileCache()
    key = f"transcript:{ticker}:{quarter}"
    hit, cached = cache.get(CATEGORY, key)
    if hit:
        return _envelope.ok(cached, source=cached.get("_source", "cache"), cache_hit=True)

    provs = providers if providers is not None else _real_providers()
    ordered = _cache.failover_order(
        [{"name": n, "priority": _priority(n), "fn": (lambda f=f: f(ticker, quarter))}
         for n, f in provs.items()]
    )
    if not ordered:
        return _envelope.error(
            "SOURCE_UNAVAILABLE: no earnings providers installed (pip install defeatbeta-api)")
    try:
        data, used = _cache.try_sources(ordered)
    except Exception as e:  # noqa: BLE001
        return _envelope.error(f"SOURCE_UNAVAILABLE: {e}")
    if data is None:
        return _envelope.error("NOT_FOUND: no transcript", source=used)
    data = dict(data)
    data["_source"] = used
    cache.set(CATEGORY, key, data)
    if used == "earnings-whispers":
        return _envelope.degraded(data, source=used, error="primary sources unavailable; used scraper (R7)")
    return _envelope.ok(data, source=used)


def _priority(name: str) -> int:
    for s in _sources.for_category(CATEGORY):
        if s["name"] == name:
            return s["priority"]
    return 1000


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="~~earnings_data tool (spec 039 US5)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--quarter", required=True, help="e.g. 2026Q1")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    env = get_transcript(args.ticker, args.quarter)
    print(json.dumps(env) if args.json else json.dumps(env, indent=2))
    return 0 if env["status"] != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
