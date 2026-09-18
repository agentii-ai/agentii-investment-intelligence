"""The `{ticker}-live/` capture harness — folder contract and failure fidelity.

The harness's most important property is that it writes FAILURES as faithfully as
successes. When the provider is rate-limited or blocked, the absence of data is
itself the finding, and a success-only harness would hide precisely the condition
this whole exercise exists to surface. These tests pin that property.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-tools"))
import live_snapshot  # noqa: E402

OBSERVED_AT = "2026-09-09T16:00:00-04:00"

# A SINGLE provider that serves both shapes. One entry means no ordering question
# arises: neither get_quote nor get_price_history selects providers by capability
# (they walk the dict by priority, then insertion order — see D1 and its mirror
# D-capability in test_market_data_adapter.py), so a multi-entry fake would make
# this file test provider selection instead of the folder contract.
def _ok_provider(t, period="1y", interval="1d"):
    return {
        "symbol": t,
        "price": 230.36,
        "market_cap": 5_562_502_934_738,
        "observed_at": OBSERVED_AT,
        "price_basis": "close",
        "data_class": "fast",
        "bars": [{"date": f"2026-06-{d:02d}", "open": 1.0, "high": 2.0, "low": 0.5,
                  "close": 1.5, "volume": 100} for d in range(1, 26)],
    }


OK_PROVIDERS = {"fake_both": _ok_provider}

# Reproduces the live condition: every provider raises (429 / 403 in reality).
FAILING_PROVIDERS = {
    "fake": lambda t: (_ for _ in ()).throw(RuntimeError("Too Many Requests")),
    "fake_history": lambda t, period="1y", interval="1d": (
        _ for _ in ()).throw(RuntimeError("Too Many Requests")),
}


def test_success_writes_the_full_folder(tmp_path):
    summary = live_snapshot.capture_ticker(tmp_path, "NVDA",
                                           providers=OK_PROVIDERS,
                                           cache_root=tmp_path / "cache")
    folder = tmp_path / "NVDA-live"
    assert folder.is_dir()
    for name in ("quote_latest.json", "history_1y_1d.json", "attempts.ndjson", "INDEX.md"):
        assert (folder / name).is_file(), f"missing {name}"

    quote = json.loads((folder / "quote_latest.json").read_text())
    assert quote["status"] == "ok"
    assert quote["data"]["price"] == pytest.approx(230.36)

    assert summary["quote"]["status"] == "ok"
    assert summary["history"]["bar_count"] == 25
    assert summary["history"]["last_close"] == pytest.approx(1.5)


def test_failure_is_captured_not_swallowed(tmp_path):
    """The provider being down must produce a folder, not a crash and not silence."""
    summary = live_snapshot.capture_ticker(tmp_path, "NVDA",
                                           providers=FAILING_PROVIDERS,
                                           cache_root=tmp_path / "cache")
    folder = tmp_path / "NVDA-live"

    quote = json.loads((folder / "quote_latest.json").read_text())
    assert quote["status"] == "error"
    assert "SOURCE_UNAVAILABLE" in quote["error"]
    assert summary["quote"]["status"] == "error"
    assert summary["quote"]["error"]

    # The index must state the failure plainly rather than omit the ticker.
    index = (folder / "INDEX.md").read_text()
    assert "error" in index.lower()


def test_attempt_log_is_append_only_and_records_every_attempt(tmp_path):
    """A second run appends; it never truncates the history of what was tried."""
    for _ in range(2):
        live_snapshot.capture_ticker(tmp_path, "NVDA", providers=OK_PROVIDERS,
                                     cache_root=tmp_path / "cache")

    lines = (tmp_path / "NVDA-live" / "attempts.ndjson").read_text().strip().splitlines()
    assert len(lines) == 4, "two runs x (quote + history) = four rows"
    rows = [json.loads(line) for line in lines]
    assert {r["kind"] for r in rows} == {"quote", "history"}
    assert all(r["ticker"] == "NVDA" for r in rows)


def test_workspace_index_reports_the_headline_first(tmp_path):
    """The committed summary's job is to answer 'how much of the universe actually
    resolved?' before listing anything."""
    summaries = [
        live_snapshot.capture_ticker(tmp_path, "NVDA", providers=OK_PROVIDERS,
                                     cache_root=tmp_path / "cache"),
        live_snapshot.capture_ticker(tmp_path, "SPCX", providers=FAILING_PROVIDERS,
                                     cache_root=tmp_path / "cache"),
    ]
    md = live_snapshot.render_workspace_index(summaries)
    assert "quote ok**: 1/2" in md
    assert "`NVDA`" in md and "`SPCX`" in md
    assert "SOURCE_UNAVAILABLE" in md  # distinct errors surfaced, not buried


def test_no_tmp_residue(tmp_path):
    live_snapshot.capture_ticker(tmp_path, "NVDA", providers=OK_PROVIDERS,
                                 cache_root=tmp_path / "cache")
    assert not list(tmp_path.rglob("*.tmp"))


def test_cli_writes_live_index(tmp_path):
    rc = live_snapshot.main(["--workspace", str(tmp_path),
                             "--tickers", "NVDA,PH",
                             "--cache-root", str(tmp_path / "cache")])
    assert rc == 0
    assert (tmp_path / "LIVE-INDEX.md").is_file()
    assert (tmp_path / "NVDA-live" / "INDEX.md").is_file()
    assert (tmp_path / "PH-live" / "INDEX.md").is_file()
    # 19 thesis tickers is the documented default
    assert len(live_snapshot.THESIS_TICKERS) == 19
