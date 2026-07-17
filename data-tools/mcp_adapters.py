#!/usr/bin/env python3
"""mcp_adapters.py — A6 MCP adapter surface (spec 039 US5, T063).

Maps the 4-tool base MCP surface to local data-tools logic so a hosted MCP server
(spec 019/022 owns hosting) and the local CLI return identical envelopes. This module
is hosting-agnostic: it only defines the adapter functions + a registration manifest.

  get_economic_indicator  -> macro_data.get_series
  get_economic_series     -> macro_data.get_series (alias; full series)
  get_market_data         -> market_data.get_quote
  search_economic_calendar-> economic_calendar (Phase 2; stub returns error envelope)

License: MIT-only imports.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _envelope  # noqa: E402
import macro_data  # noqa: E402
import market_data  # noqa: E402


def get_economic_indicator(series_id: str, *, providers=None, cache_root: Optional[Path] = None) -> dict:
    return macro_data.get_series(series_id, providers=providers, cache_root=cache_root)


def get_economic_series(series_id: str, *, providers=None, cache_root: Optional[Path] = None) -> dict:
    return macro_data.get_series(series_id, providers=providers, cache_root=cache_root)


def get_market_data(ticker: str, *, providers=None, cache_root: Optional[Path] = None) -> dict:
    return market_data.get_quote(ticker, providers=providers, cache_root=cache_root)


def search_economic_calendar(**kwargs) -> dict:
    # Phase 2 category — not yet implemented; return a well-formed error envelope.
    return _envelope.error("NOT_IMPLEMENTED: economic_calendar ships in Phase 2")


# Registration manifest mapping tool name -> adapter + category (consumed by the host).
REGISTRATION_MANIFEST = {
    "get_economic_indicator": {"fn": "get_economic_indicator", "category": "macro"},
    "get_economic_series": {"fn": "get_economic_series", "category": "macro"},
    "get_market_data": {"fn": "get_market_data", "category": "market"},
    "search_economic_calendar": {"fn": "search_economic_calendar", "category": "calendar"},
}


def dispatch(tool_name: str, /, **params) -> dict:
    """Route a tool call to its adapter (used by tests + host shims)."""
    entry = REGISTRATION_MANIFEST.get(tool_name)
    if entry is None:
        return _envelope.error(f"UNKNOWN_TOOL: {tool_name}")
    return globals()[entry["fn"]](**params)
