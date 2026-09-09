"""T013/T015: market_data.py spec-046 fields — observed_at/retrieved_at/price_basis/data_class.

Q71 hard rule: a quote lacking observed_at may not be used in any pinned artifact —
enforced structurally at the data layer (the quote is refused, not merely warned).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import market_data  # noqa: E402

FAKE_OK = {
    "fake": lambda t: {
        "symbol": t,
        "price": 230.0,
        "market_cap": 5562502934738,
        "observed_at": "2026-09-08T16:00:00-04:00",
        "price_basis": "close",
        "data_class": "fast",
    }
}
FAKE_NO_OBSERVED_AT = {"fake": lambda t: {"symbol": t, "price": 230.0}}


def test_quote_carries_spec046_fields(tmp_path):
    env = market_data.get_quote("NVDA", providers=FAKE_OK, cache_root=tmp_path)
    assert env["status"] == "ok"
    d = env["data"]
    assert d["observed_at"].startswith("2026-09-08")
    assert d["price_basis"] == "close"
    assert d["data_class"] == "fast"
    assert "retrieved_at" in d  # ISO-parseable NY time
    import datetime

    datetime.datetime.fromisoformat(d["retrieved_at"])


def test_quote_lacking_observed_at_is_refused(tmp_path):
    # Q71 hard rule at the data layer: the agent structurally cannot obtain the quote.
    env = market_data.get_quote("NVDA", providers=FAKE_NO_OBSERVED_AT, cache_root=tmp_path)
    assert env["status"] == "error"
    assert env["error"].startswith("DATA_STALE")
    assert "observed_at" in env["error"]


def test_cache_hit_reports_cache_age_seconds(tmp_path):
    first = market_data.get_quote("NVDA", providers=FAKE_OK, cache_root=tmp_path)
    assert first["cache_hit"] is False
    second = market_data.get_quote("NVDA", providers=FAKE_OK, cache_root=tmp_path)
    assert second["cache_hit"] is True
    assert isinstance(second["data"]["cache_age_seconds"], (int, float))
    assert second["data"]["cache_age_seconds"] >= 0
