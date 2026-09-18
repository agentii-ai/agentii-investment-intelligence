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
    # market — REORDERED 2026-09-18 (T179), from measurement not documentation.
    #
    # EGRESS SCOPE (T183, Q104): our users are in the US and the EU. The Chinese
    # firewall is EXPLICITLY OUT OF SCOPE and must not drive provider choice — the
    # user said so directly. The comments this replaced justified the ordering by
    # CN reachability ("verified reachable from CN", "geo-blocked from CN"), which
    # is the wrong axis: it is why Yahoo sat at priority 10 while being the one
    # source measured as failing.
    #
    # MEASURED 2026-09-17 (live-data-provider.md §2, AAPL):
    #   nasdaq  OK      332.41  3656 ms  keyless daily OHLCV
    #   sina    OK      332.41    88 ms  keyless, GBK, needs Referer
    #   tencent OK      332.41   119 ms  keyless, GBK, quote only
    #   yahoo   FAIL        —    616 ms  GEO_BLOCK: HTTP 403
    #   alpaca/tiingo/massive/fmp/finnhub  SKIPPED — no key (never a failure)
    #
    # Two corrections the research made to the chosen set, both asserted as tests
    # (T185): Finnhub's free tier is QUOTES ONLY — US OHLC history is paid and its
    # ToS forbids business use even internally, so listing it as a general market
    # source was misleading; and Alpaca, absent from the original set, clears
    # every constraint at once and is adapter number one.
    {"name": "alpaca", "category": "market", "auth": "free_key",
     "env_vars": ["ALPACA_API_KEY", "ALPACA_SECRET_KEY"],
     "license": "Apache-2.0", "invoke": "import", "priority": 10,
     "note": "ADAPTER NUMBER ONE (T185). 200 req/min with no daily cap, true "
             "batching (?symbols=A,B,C), daily→1min bars to 2016, real-time IEX, "
             "free paper key, no card. Not in the original chosen set."},
    {"name": "tiingo", "category": "market", "auth": "free_key", "env_vars": ["TIINGO_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 15},
    {"name": "massive", "category": "market", "auth": "free_key",
     "env_vars": ["POLYGON_API_KEY"],
     "license": "MIT", "invoke": "import", "priority": 20,
     "note": "ex-Polygon.io (api.polygon.io serves the same API with the same "
             "keys); grouped_daily(date) returns OHLC for the ENTIRE US market "
             "in one call — the most request-efficient daily backfill available"},
    # ── keyless: these are the ones that answer with no key at all ──────────
    {"name": "nasdaq", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 30,
     "note": "KEYLESS PRIMARY (T179). Daily OHLCV + company data, no key and no "
             "signup. Measured OK, AAPL 332.41, 3656 ms."},
    {"name": "sina", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 32,
     "note": "KEYLESS SECONDARY (T179) and 40x faster than Nasdaq (88 ms vs "
             "3656 ms). GBK-encoded — decode explicitly, never the default codec "
             "— and it requires a Referer header."},
    {"name": "tencent", "category": "market", "auth": "none", "env_vars": [],
     "license": "unofficial", "invoke": "import", "priority": 35,
     "note": "GBK-encoded; quote endpoint only — its kline is positional with "
             "close third, so it cannot serve history"},
    {"name": "secfin", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 50},
    # investpy is effectIvely DEAD — Investing.com added Cloudflare and it returns
    # 403. Retained at the lowest import priority only to keep the registry honest
    # about what was once declared; do not rely on it.
    {"name": "investpy", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 95, "status": "dead"},
    # Finnhub's free tier covers the QUOTE endpoint only — US OHLC history is paid
    # — and its ToS forbids business use even internally. Not a history source.
    {"name": "finnhub", "category": "market", "auth": "free_key", "env_vars": ["FINNHUB_API_KEY"],
     "license": "Apache-2.0", "invoke": "import", "priority": 40,
     "note": "QUOTES ONLY (T185 correction). Its free tier covers the quote "
             "endpoint but US OHLC history sits behind the paid plan, and its ToS "
             "states the personal plan 'can't be used by any business even "
             "internally without a written approval'. Listing it as a general "
             "market source was misleading; the adapter is kept and the "
             "limitation is ASSERTED rather than discovered in production."},
    # ── negative control ────────────────────────────────────────────────────
    {"name": "yfinance", "category": "market", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 90,
     "note": "NEGATIVE CONTROL (T181), formerly priority 10 — i.e. the DEFAULT, "
             "while being the one source measured as failing. It is not broken for "
             "our users: the CN 403 is Yahoo policy (withdrew from mainland China "
             "2021-11-01, edge geo-block) and OUT OF SCOPE per the user. The "
             "US-datacenter 429 is a separate, real problem. Kept LAST so its "
             "assertion — a clean structured refusal, not a traceback — runs on "
             "every failover."},
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
