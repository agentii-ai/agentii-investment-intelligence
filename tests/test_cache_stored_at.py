"""T012/T014: FileCache.get_meta exposes stored_at → cache_age_seconds; Q44 dual TTL.

The information already exists (set() writes stored_at); get() currently discards it
(spec 046 Q71 divergence class — the cheapest high-value fix in the plan).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import _cache  # noqa: E402


def test_get_meta_returns_stored_at(tmp_path):
    cache = _cache.FileCache(root=tmp_path, clock=lambda: 1000.0)
    cache.set("market", "quote:NVDA", {"symbol": "NVDA"}, ttl=900)
    hit, value, meta = cache.get_meta("market", "quote:NVDA")
    assert hit is True
    assert value == {"symbol": "NVDA"}
    assert meta["stored_at"] == 1000.0
    assert meta["expires_at"] == 1900.0
    # cache_age_seconds derivation: now - stored_at
    assert 1100.0 - meta["stored_at"] == 100.0


def test_get_meta_miss_returns_none_meta(tmp_path):
    cache = _cache.FileCache(root=tmp_path, clock=lambda: 1000.0)
    hit, value, meta = cache.get_meta("market", "quote:MSFT")
    assert hit is False
    assert value is None
    assert meta is None


def test_market_quote_ttl_is_15_minutes():
    # Q44: quote 15 min / history 24 h — the quote half lands with T014.
    assert _cache.CATEGORY_TTL["market"] == 900
