"""L4–L6: governance gates, cache semantics, contract conformance.

Covers defect D4 — the Q71 refusal gate is enforced on the network path but NOT on
the cache-hit path. Since the quote TTL is 15 minutes and cache hits are the common
case in a multi-thesis run, the gate is bypassed on the dominant path.

Also asserts two cache properties the design depends on but nothing currently
guards: that an explicit `cache_root` is authoritative (test isolation), and that
the shared user cache holds no fixture data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import market_data  # noqa: E402
import _cache  # noqa: E402
import _envelope  # noqa: E402

PINNABLE = {"symbol": "NVDA", "price": 230.0,
            "observed_at": "2026-09-09T16:00:00-04:00",
            "price_basis": "close", "data_class": "fast"}
UNPINNABLE = {"symbol": "NVDA", "price": 230.0}  # no observed_at

# Symbols that exist only in test fixtures. None may ever reach the shared cache.
FIXTURE_TICKER_DENYLIST = {"CK35", "FAKE", "TEST", "XXXX"}


def _provider(payload: dict):
    return {"fake": lambda t, _p=payload: dict(_p, symbol=t)}


def _boom(_ticker):
    raise RuntimeError("Too Many Requests")


# Every provider raises — reproduces a provider outage, which is what drives
# get_quote onto the stale-fallback path.
FAILING = {"fake": _boom}


# --- L4: the Q71 gate on both paths ------------------------------------------

def test_q71_gate_refuses_on_the_network_path(tmp_path):
    """Baseline — this half already works, and the fix for D4 must not break it."""
    env = market_data.get_quote("NVDA", providers=_provider(UNPINNABLE), cache_root=tmp_path)
    assert env["status"] == "error"
    assert env["error"].startswith("DATA_STALE")


@pytest.mark.xfail(strict=True, reason=(
    "D4: get_quote() returns early on a cache hit without re-running "
    "refusal.require_observed_at, so a cached quote lacking observed_at is served "
    "as status=ok. The Q71 hard rule — 'refuse it structurally rather than warn' — "
    "is bypassed on the dominant path."))
def test_q71_gate_refuses_on_the_cache_hit_path(tmp_path):
    """The same unpinnable payload must be refused whether it arrives from the
    network or from cache. Today it is refused on one path and served on the other."""
    cache = _cache.FileCache(root=tmp_path)
    cache.set("market", "quote:NVDA", dict(UNPINNABLE, _source="yfinance"), ttl=900)

    env = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)

    assert env["cache_hit"] is True, "expected the seeded entry to be served"
    assert env["status"] == "error", (
        f"a cached quote without observed_at was served as {env['status']!r} — "
        f"Q71 requires refusal"
    )
    assert env["error"].startswith("DATA_STALE")


@pytest.mark.xfail(strict=True, reason=(
    "D4b: the stale-fallback path (Q44 degraded) returns BEFORE both the "
    "market_cap int coercion and the refusal.require_observed_at gate. It is the "
    "third path through get_quote and the second that bypasses Q71. Observed live: "
    "NVDA served a 9-day-old price with observed_at null and an uncoerced float "
    "market_cap."))
def test_stale_fallback_path_also_honours_the_gate_and_the_contract(tmp_path):
    """When the provider is unreachable, the stale fallback is the path that
    actually fires — so it is the one most in need of the gate, not least."""
    cache = _cache.FileCache(root=tmp_path)
    cache.set("market", "quote:NVDA",
              {"symbol": "NVDA", "price": 230.36, "market_cap": 5562502934738.159,
               "_source": "yfinance"}, ttl=900)

    env = market_data.get_quote("NVDA", providers=FAILING, cache_root=tmp_path)

    assert env["status"] == "degraded", env
    assert env["data"].get("observed_at"), (
        "stale fallback served a price with no observed_at — Q71 bypassed on the "
        "path that fires during a provider outage"
    )
    assert isinstance(env["data"].get("market_cap"), int), (
        "market_cap must be int per the contract; the stale path skips the coercion"
    )


def test_pinnable_quote_survives_the_cache_round_trip(tmp_path):
    """Guard: a properly pinnable quote must still be served from cache, with its
    observed_at intact. A fix for D4 must not simply refuse everything."""
    env = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    assert env["status"] == "ok"

    hit = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    assert hit["status"] == "ok" and hit["cache_hit"] is True
    assert hit["data"]["observed_at"] == PINNABLE["observed_at"]


# --- L5: cache semantics ------------------------------------------------------

def test_explicit_cache_root_is_authoritative(tmp_path, monkeypatch):
    """An explicit cache_root must fully contain the operation. If it does not,
    tests and workspaces silently contaminate the shared ~/.agentii cache."""
    sentinel = tmp_path / "sentinel-default-root"
    monkeypatch.setattr(_cache, "DEFAULT_ROOT", sentinel)

    market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path / "c")
    market_data.get_price_history("NVDA", providers={"h": lambda t, period="1y", interval="1d": {
        "symbol": t, "bars": [{"date": f"2026-09-{d:02d}", "open": 1.0, "high": 1.0,
                               "low": 1.0, "close": 1.0, "volume": 1} for d in range(1, 26)],
        "observed_at": "2026-09-09T16:00:00-04:00"}}, cache_root=tmp_path / "c")

    assert not sentinel.exists(), (
        f"an explicit cache_root still wrote to the default root: "
        f"{sorted(p.name for p in sentinel.rglob('*'))}"
    )


@pytest.mark.xfail(strict=False, reason=(
    "D6: the shared ~/.agentii/cache/market/ contains a 'CK35' fixture quote at "
    "$1.00 with a fabricated observed_at — test data leaked into the production "
    "cache. Environmental: passes on a machine with no populated cache."))
def test_shared_cache_holds_no_fixture_tickers():
    """A fabricated ticker in the production cache is worse than untidy: a later
    lookup of that symbol would serve fixture prices as if they were real."""
    root = Path.home() / ".agentii" / "cache" / "market"
    if not root.is_dir():
        pytest.skip("no shared cache on this machine")

    found = set()
    for path in root.glob("*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8")).get("value") or {}
        except (ValueError, OSError):
            continue
        symbol = value.get("symbol")
        if symbol in FIXTURE_TICKER_DENYLIST:
            found.add(symbol)
    assert not found, f"fixture tickers present in the shared cache: {sorted(found)}"


def test_cache_write_is_atomic(tmp_path):
    """No .tmp residue may survive a successful write (crash-safety invariant)."""
    market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    assert not list(tmp_path.rglob("*.tmp"))


# --- L6: contract conformance -------------------------------------------------

def test_envelope_validates_against_the_closed_schema(tmp_path):
    env = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    _envelope.validate(env)  # raises jsonschema.ValidationError on failure


def test_error_envelope_validates_against_the_closed_schema(tmp_path):
    env = market_data.get_quote("NVDA", providers=_provider(UNPINNABLE), cache_root=tmp_path)
    _envelope.validate(env)


def test_quote_carries_the_pinnable_core_fields(tmp_path):
    """The fields that make a quote usable must survive the round trip."""
    env = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    d = env["data"]
    for key in ("symbol", "price", "observed_at", "price_basis", "data_class",
                "retrieved_at"):
        assert key in d, f"contract field {key!r} missing from the quote payload"
    assert d["data_class"] == "fast"
    assert d["price_basis"] in ("close", "intraday")


@pytest.mark.xfail(strict=True, reason=(
    "D-contract: get_quote does not normalize a provider's payload to the "
    "contract's declared response shape. Any provider that omits a key yields a "
    "payload that violates contracts/get-realtime-quote-tool.md, and consumers "
    "cannot distinguish 'field absent' from 'field null'. This is the same "
    "divergence class the contract itself documents (spec 046 T007: 'contract says "
    "15 fields, code delivers 3')."))
def test_quote_normalizes_any_provider_payload_to_the_contract_shape(tmp_path):
    """Every field in the contract's response shape must be present as a key, even
    when the provider did not supply it. An absent key breaks consumers; a null key
    is merely a data problem."""
    env = market_data.get_quote("NVDA", providers=_provider(PINNABLE), cache_root=tmp_path)
    d = env["data"]
    for key in ("symbol", "price", "market_cap", "day_high", "day_low", "open",
                "previous_close", "volume", "ma_50", "observed_at", "price_basis",
                "data_class", "retrieved_at"):
        assert key in d, f"contract field {key!r} missing from the quote payload"
