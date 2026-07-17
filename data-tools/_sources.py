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
    {"name": "openbb", "category": "macro", "auth": "free_key", "env_vars": ["OPENBB_PAT"],
     "license": "AGPL-3.0", "invoke": "subprocess|mcp", "priority": 20},
    {"name": "yfinance", "category": "macro", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 30},
    # market
    {"name": "yfinance", "category": "market", "auth": "none", "env_vars": [],
     "license": "Apache-2.0", "invoke": "import", "priority": 10},
    {"name": "secfin", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 20},
    {"name": "investpy", "category": "market", "auth": "none", "env_vars": [],
     "license": "MIT", "invoke": "import", "priority": 30},
    {"name": "finnhub", "category": "market", "auth": "free_key", "env_vars": ["FINNHUB_API_KEY"],
     "license": "Apache-2.0", "invoke": "import", "priority": 40},
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
