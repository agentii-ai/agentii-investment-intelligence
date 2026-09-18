#!/usr/bin/env python3
"""_sources.py — source registry driving ~~category resolution (spec 039 US5, T057).

Mirrors contracts/SOURCES.md. Each source: category, auth, env_vars, license, invoke
('import' in-process or 'subprocess|mcp' out-of-process for copyleft), priority.
Copyleft sources (openbb, wbdata) are 'subprocess|mcp' and MUST NOT be imported here.

License: MIT-only imports (stdlib).
"""
from __future__ import annotations

import os
from typing import Optional

# Phase A (MVP) source registry. Priority: lower = tried first.
SOURCES = [
    # macro
    {"name": "fred", "category": "macro", "auth": "free_key", "env_vars": ["FRED_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 10},
    # OpenBB is AGPL-3.0 and MUST NOT be imported (check.py Check 30b). It also
    # takes NO env var: `OPENBB_PAT` does not exist in openbb-core 1.6.0 — the
    # docs use it as a placeholder for a credential string passed as an argument.
    # Keys live in ~/.openbb_platform/user_settings.json.
    {"name": "openbb", "category": "macro", "auth": "none", "env_vars": [],
     "license": "AGPL-3.0", "invoke": "subprocess|mcp", "priority": 20},
    {"name": "yfinance", "category": "macro", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 30},
    # market
    # yfinance is Apache-2.0 and importable, but it is UNUSABLE from a mainland
    # China network: Yahoo geo-blocks CN IPs (policy 2021-11-01) and yfinance
    # mis-reports the 403 as YFRateLimitError. Kept for non-CN deployments only.
    {"name": "yfinance", "category": "market", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 10,
     "note": "geo-blocked from CN; see testing-plan.md E.3"},
    # Keyless and verified reachable from CN. See data-tools/source_probe.py.
    {"name": "nasdaq", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 20,
     "note": "keyless daily OHLCV; verified 2026-09-17"},
    {"name": "sina", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 25,
     "note": "GBK-encoded; requires Referer; quote + history to 1984"},
    {"name": "tencent", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 30,
     "note": "GBK-encoded; quote endpoint only — its kline is positional with close third"},
    {"name": "secfin", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 35},
    # investpy is effectIvely DEAD — Investing.com added Cloudflare and it returns
    # 403. Retained at the lowest import priority only to keep the registry honest
    # about what was once declared; do not rely on it.
    {"name": "investpy", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 60, "status": "dead"},
    # Finnhub's free tier covers the QUOTE endpoint only — US OHLC history is paid
    # — and its ToS forbids business use even internally. Not a history source.
    {"name": "finnhub", "category": "market", "auth": "free_key", "env_vars": ["FINNHUB_API_KEY"],
     "license": "Apache-2.0", "invoke": "import", "priority": 40,
     "note": "quotes only; free tier excludes OHLC history"},
    {"name": "alpaca", "category": "market", "auth": "free_key",
     "env_vars": ["ALPACA_API_KEY", "ALPACA_SECRET_KEY"],
     "license": "Apache-2.0", "invoke": "import", "priority": 15,
     "note": "200 req/min, true batch, free paper key, no card"},
    {"name": "tiingo", "category": "market", "auth": "free_key", "env_vars": ["TIINGO_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 45},
    {"name": "massive", "category": "market", "auth": "free_key",
     "env_vars": ["POLYGON_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 50,
     "note": "ex-Polygon.io; grouped_daily returns the whole US market in one call"},
    # earnings
    {"name": "defeatbeta-api", "category": "earnings", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 10},
    {"name": "fmp", "category": "earnings", "auth": "free_key", "env_vars": ["FMP_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 20},
    {"name": "earnings-whispers", "category": "earnings", "auth": "none", "env_vars": [],
     "license": "scraper", "invoke": "import", "priority": 90},
]

# Copyleft package roots that must never be imported into the MIT core (mirrors check.py).
COPYLEFT_DENYLIST = {"openbb", "openbb_terminal", "wbdata"}


def for_category(category: str) -> list[dict]:
    return [dict(s) for s in SOURCES if s["category"] == category]


def has_keys(source: dict) -> bool:
    """True if all env vars required by this source are set (zero-key sources → True)."""
    return all(os.environ.get(v) for v in source.get("env_vars", []))


def available(category: str, *, allow_out_of_process: bool = False) -> list[dict]:
    """Sources usable right now: zero-key ones always; keyed ones only if keys present;
    copyleft (out-of-process) excluded unless explicitly allowed."""
    out = []
    for s in for_category(category):
        if s["invoke"] != "import" and not allow_out_of_process:
            continue
        if s["auth"] == "free_key" and not has_keys(s):
            continue
        out.append(s)
    return out


def is_copyleft(name: str) -> bool:
    return name in COPYLEFT_DENYLIST
