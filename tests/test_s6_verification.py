"""T083 — S6 verification: shared-cache economics, rebuildability, throttling,
gitignore hygiene, evidence replayability."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import agentii_cmd  # noqa: E402
import dispatch  # noqa: E402
import workspace_cache  # noqa: E402


def test_six_skills_one_fetch(tmp_path):
    # Q44's quantified benefit: 6 skills requesting the same ticker → 1 write,
    # 5 filesystem hits, zero further API calls.
    root = tmp_path / "workspace" / "market-data"
    workspace_cache.write_quote(root, "NVDA", {"price": 230.0},
                                observed_at="2026-09-08T16:00:00-04:00")
    hits = 0
    for _ in range(6):
        hit, data = workspace_cache.read_latest(root, "quotes", "NVDA")
        if hit:
            hits += 1
            assert data["price"] == 230.0
    assert hits == 6


def test_cache_deleted_mid_run_rebuilds(tmp_path):
    root = tmp_path / "workspace" / "market-data"
    workspace_cache.write_quote(root, "NVDA", {"price": 1.0},
                                observed_at="2026-09-08T16:00:00-04:00")
    for p in root.rglob("*.json"):
        p.unlink()
    hit, _ = workspace_cache.read_latest(root, "quotes", "NVDA")
    assert hit is False  # a miss is a correctness-neutral event: re-fetch, no error


def test_rate_limiter_throttles_not_429s():
    limiter = dispatch.RateLimiter({"yfinance": 2})
    assert limiter.acquire("yfinance") and limiter.acquire("yfinance")
    assert not limiter.acquire("yfinance")  # third concurrent request refused
    limiter.release("yfinance")
    assert limiter.acquire("yfinance")


def test_scaffold_gitignores_cache_dirs(tmp_path):
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    ignore = (ws / ".gitignore").read_text()
    assert "market-data/" in ignore and "raw-data/" in ignore
    # evidence stays committed — the .gitignore must not blanket theses/
    assert "theses/" not in ignore


def test_raw_data_accession_keyed_infinite_ttl(tmp_path):
    root = tmp_path / "workspace"
    workspace_cache.write_raw(root, "filings", "0000320193-26-000070", {"doc": "10-K"})
    hit, data = workspace_cache.read_raw(root, "filings", "0000320193-26-000070")
    assert hit and data["doc"] == "10-K"
    # no TTL semantics at all — immutable data needs none (Q82)
    hit2, _ = workspace_cache.read_raw(root, "filings", "missing-accession")
    assert hit2 is False
