"""S6 tests (T074–T083): workspace market-data cache, get_price_history,
field-by-field growth, max_in_flight, evidence snapshots, staged orders."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import dispatch  # noqa: E402
import market_data  # noqa: E402
import staged_orders  # noqa: E402
import workspace_cache  # noqa: E402

FAKE_OK = {"fake": lambda t: {
    "symbol": t, "price": 230.0, "market_cap": 5562502934738,
    "observed_at": "2026-09-08T16:00:00-04:00", "price_basis": "close",
    "data_class": "fast"}}
FAKE_HIST = {"fake": lambda t, period="1y", interval="1d": {
    "symbol": t, "bars": [{"date": f"2026-09-{d:02d}", "open": 1.0, "high": 2.0,
                           "low": 0.5, "close": 1.5, "volume": 100} for d in range(1, 26)],
    "observed_at": "2026-09-08T16:00:00-04:00"}}


# --- T074: workspace market-data cache ----------------------------------------

def test_filesystem_first_lookup_and_index(tmp_path):
    root = tmp_path / "workspace" / "market-data"
    workspace_cache.write_quote(root, "NVDA", {"price": 230.0},
                                observed_at="2026-09-08T16:00:00-04:00")
    hit, data = workspace_cache.read_latest(root, "quotes", "NVDA")
    assert hit is True
    assert data["price"] == 230.0
    index = workspace_cache.read_index(root)
    assert "NVDA" in index


def test_ttl_expiry_forces_refetch(tmp_path):
    root = tmp_path / "workspace" / "market-data"
    workspace_cache.write_quote(root, "NVDA", {"price": 230.0},
                                observed_at="2026-09-08T16:00:00-04:00",
                                ttl_seconds=-1)  # already expired
    hit, _ = workspace_cache.read_latest(root, "quotes", "NVDA", ttl_seconds=900)
    assert hit is False


def test_atomic_write_no_tmp_residue(tmp_path):
    root = tmp_path / "workspace" / "market-data"
    workspace_cache.write_quote(root, "NVDA", {"price": 1.0},
                                observed_at="2026-09-08T16:00:00-04:00")
    assert not list(root.rglob("*.tmp"))


# --- T075: get_price_history --------------------------------------------------

def test_price_history_bars_and_insufficient_history(tmp_path):
    env = market_data.get_price_history("NVDA", providers=FAKE_HIST,
                                        cache_root=tmp_path / "c")
    assert env["status"] == "ok"
    assert len(env["data"]["bars"]) == 25
    tiny = {"fake": lambda t, period="1y", interval="1d": {
        "symbol": t, "bars": [{"date": "2026-09-01", "open": 1, "high": 2, "low": 0.5,
                               "close": 1.5, "volume": 1}],
        "observed_at": "2026-09-08T16:00:00-04:00"}}
    env2 = market_data.get_price_history("NVDA", providers=tiny, cache_root=tmp_path / "c2")
    assert env2["status"] == "error"
    assert env2["error"].startswith("INSUFFICIENT_HISTORY")


# --- T076: field growth -------------------------------------------------------

def test_quote_fields_grow_with_provider(tmp_path):
    rich = {"fake": lambda t: {
        "symbol": t, "price": 230.0, "market_cap": 5562502934738.159,
        "observed_at": "2026-09-08T16:00:00-04:00", "price_basis": "close",
        "data_class": "fast", "day_high": 235.0, "day_low": 228.0,
        "open": 231.0, "previous_close": 229.0, "volume": 50000000,
        "ma_50": 210.0}}
    env = market_data.get_quote("NVDA", providers=rich, cache_root=tmp_path / "c")
    d = env["data"]
    assert d["day_high"] == 235.0 and d["ma_50"] == 210.0
    # market_cap coerced to int per the contract
    assert isinstance(d.get("market_cap"), (int, type(None)))


# --- T080: max_in_flight ------------------------------------------------------

def test_max_in_flight_ceiling():
    limiter = dispatch.RateLimiter({"sec": 10, "yfinance": 2000})
    assert limiter.acquire("sec") is True
    limiter = dispatch.RateLimiter({"sec": 0})  # exhausted budget
    assert limiter.acquire("sec") is False


# --- T079: evidence snapshots -------------------------------------------------

def test_evidence_snapshot_written_and_immutable(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    from evidence import snapshot_quote
    path = snapshot_quote(thesis, "NVDA", {"price": 230.0},
                          observed_at="2026-09-08T16:00:00-04:00",
                          retrieved_at="2026-09-08T16:01:00-04:00",
                          price_basis="close")
    assert path.is_file()
    rec = yaml.safe_load(path.read_text())
    assert rec["ticker"] == "NVDA"
    assert rec["price_basis"] == "close"
    # immutable: re-writing the same ticker appends a new timestamped file
    path2 = snapshot_quote(thesis, "NVDA", {"price": 231.0},
                           observed_at="2026-09-08T16:02:00-04:00",
                           retrieved_at="2026-09-08T16:03:00-04:00",
                           price_basis="close")
    assert path2 != path
    assert len(list(path.parent.glob("*.yaml"))) == 2


# --- T081: staged orders ------------------------------------------------------

def test_staged_order_preconditions(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    base = {"symbol": "NVDA", "side": "long", "qty": 10, "price": 232.0,
            "thesis_id": "001-mvp", "claim_id": "c-1",
            "ic_approval_ref": "ic-2026-09-08", "expires_at": "2026-09-09T16:00:00-04:00"}
    ok = staged_orders.check_preconditions(
        dict(base),
        constitution_pin="0.1.0", stale_price=False, blind_order_ok=True,
        blocking_flags=False, aggregate_pass=True)
    assert ok == []
    # unratified → hard-fail (the money boundary accepts no placeholder governance)
    problems = staged_orders.check_preconditions(
        dict(base), constitution_pin="unratified", stale_price=False,
        blind_order_ok=True, blocking_flags=False, aggregate_pass=True)
    assert any("unratified" in p for p in problems)
    # missing expires_at → required
    no_expiry = dict(base)
    no_expiry.pop("expires_at")
    problems = staged_orders.check_preconditions(
        no_expiry, constitution_pin="0.1.0", stale_price=False,
        blind_order_ok=True, blocking_flags=False, aggregate_pass=True)
    assert any("expires_at" in p for p in problems)


def test_staged_order_writer_emits_yaml(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    proposal = {"symbol": "NVDA", "side": "long", "qty": 10, "price": 232.0,
                "thesis_id": "001-mvp", "claim_id": "c-1",
                "ic_approval_ref": "ic-1", "expires_at": "2026-09-09T16:00:00-04:00"}
    path = staged_orders.write_proposal(thesis, proposal)
    assert path.is_file()
    rec = yaml.safe_load(path.read_text())
    assert rec["expires_at"] == "2026-09-09T16:00:00-04:00"
