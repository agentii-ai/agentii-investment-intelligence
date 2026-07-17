"""T050 — tests for data-tools/_cache.py (write FIRST): TTL, backoff, failover order."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "_cache.py"


def _load():
    spec = importlib.util.spec_from_file_location("_cache", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_set_get_roundtrip(tmp_path):
    m = _load()
    c = m.FileCache(root=tmp_path)
    c.set("macro", "GDP", {"v": 1}, ttl=100)
    hit, val = c.get("macro", "GDP")
    assert hit is True and val == {"v": 1}


def test_ttl_expiry(tmp_path):
    m = _load()
    c = m.FileCache(root=tmp_path, clock=lambda: 1000.0)
    c.set("macro", "GDP", {"v": 1}, ttl=10)
    c2 = m.FileCache(root=tmp_path, clock=lambda: 1005.0)  # within TTL
    assert c2.get("macro", "GDP")[0] is True
    c3 = m.FileCache(root=tmp_path, clock=lambda: 1020.0)  # expired
    assert c3.get("macro", "GDP")[0] is False


def test_backoff_schedule():
    m = _load()
    # exponential: base * 2**attempt, capped
    delays = [m.backoff_delay(a, base=0.5, cap=10) for a in range(6)]
    assert delays[0] == 0.5 and delays[1] == 1.0 and delays[2] == 2.0
    assert delays[-1] <= 10  # capped
    assert delays == sorted(delays)  # monotonic


def test_failover_order_by_priority():
    m = _load()
    sources = [
        {"name": "scraper", "priority": 90},
        {"name": "fred", "priority": 10},
        {"name": "openbb", "priority": 20},
    ]
    ordered = m.failover_order(sources)
    assert [s["name"] for s in ordered] == ["fred", "openbb", "scraper"]


def test_try_sources_uses_first_success():
    m = _load()
    calls = []

    def make(name, fail):
        def fn():
            calls.append(name)
            if fail:
                raise RuntimeError(f"{name} down")
            return {"ok": name}
        return fn

    sources = [
        {"name": "fred", "priority": 10, "fn": make("fred", True)},
        {"name": "openbb", "priority": 20, "fn": make("openbb", False)},
        {"name": "scraper", "priority": 90, "fn": make("scraper", False)},
    ]
    result, used = m.try_sources(sources)
    assert result == {"ok": "openbb"}
    assert used == "openbb"
    assert calls == ["fred", "openbb"]  # scraper never reached
