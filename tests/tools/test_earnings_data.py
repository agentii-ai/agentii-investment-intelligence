"""T053 — tests for data-tools/earnings_data.py (~~earnings_data).

defeatbeta-api (zero-key) primary; FMP (keyed) fallback; scraper lowest priority.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "earnings_data.py"


def _load():
    spec = importlib.util.spec_from_file_location("earnings_data", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _envval():
    spec = importlib.util.spec_from_file_location("_envelope", REPO_ROOT / "data-tools" / "_envelope.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_zero_key_transcript_via_defeatbeta(tmp_path):
    m = _load()
    def fake_db(ticker, quarter):
        return {"ticker": ticker, "quarter": quarter, "transcript": "We had a strong quarter."}
    env = m.get_transcript("AAPL", "2026Q1", providers={"defeatbeta-api": fake_db}, cache_root=tmp_path)
    assert env["status"] in ("ok", "degraded")
    assert env["source"] == "defeatbeta-api"
    _envval().validate(env)


def test_failover_to_fmp_when_defeatbeta_down(tmp_path):
    m = _load()
    def db_down(t, q):
        raise RuntimeError("defeatbeta down")
    def fmp_ok(t, q):
        return {"ticker": t, "quarter": q, "transcript": "fallback text"}
    env = m.get_transcript("AAPL", "2026Q1",
                           providers={"defeatbeta-api": db_down, "fmp": fmp_ok},
                           cache_root=tmp_path)
    assert env["status"] in ("ok", "degraded")
    assert env["source"] == "fmp"


def test_scraper_is_last_resort(tmp_path):
    m = _load()
    order = m.provider_priority_order(["earnings-whispers", "defeatbeta-api", "fmp"])
    assert order[0] == "defeatbeta-api"
    assert order[-1] == "earnings-whispers"  # scraper last (R7)
