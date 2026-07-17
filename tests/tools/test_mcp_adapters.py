"""T065 — MCP adapter parity: adapter response == local data-tools output (no live server)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_manifest_covers_4_tool_surface():
    ad = _load("mcp_adapters", "data-tools/mcp_adapters.py")
    assert set(ad.REGISTRATION_MANIFEST) == {
        "get_economic_indicator", "get_economic_series",
        "get_market_data", "search_economic_calendar",
    }


def test_market_adapter_parity(tmp_path):
    ad = _load("mcp_adapters", "data-tools/mcp_adapters.py")
    md = _load("market_data", "data-tools/market_data.py")

    def fake_yf(ticker):
        return {"symbol": ticker, "price": 42.0}

    direct = md.get_quote("AAPL", providers={"yfinance": fake_yf}, cache_root=tmp_path / "a")
    viaad = ad.get_market_data("AAPL", providers={"yfinance": fake_yf}, cache_root=tmp_path / "b")
    # same shape + status + source (cache_hit may differ by dir; compare the rest)
    assert direct["status"] == viaad["status"]
    assert direct["source"] == viaad["source"]
    assert direct["data"]["symbol"] == viaad["data"]["symbol"] == "AAPL"


def test_macro_adapter_parity(tmp_path):
    ad = _load("mcp_adapters", "data-tools/mcp_adapters.py")
    mac = _load("macro_data", "data-tools/macro_data.py")

    def fake_fred(series_id):
        return {"series_id": series_id, "observations": []}

    direct = mac.get_series("GDP", providers={"fred": fake_fred}, cache_root=tmp_path / "a")
    viaad = ad.get_economic_indicator("GDP", providers={"fred": fake_fred}, cache_root=tmp_path / "b")
    assert direct["status"] == viaad["status"]
    assert direct["source"] == viaad["source"]


def test_dispatch_unknown_tool():
    ad = _load("mcp_adapters", "data-tools/mcp_adapters.py")
    env = ad.dispatch("nonexistent_tool")
    assert env["status"] == "error"


def test_calendar_not_implemented_is_well_formed():
    ad = _load("mcp_adapters", "data-tools/mcp_adapters.py")
    env = ad.search_economic_calendar()
    assert env["status"] == "error"
    assert env["data"] is None and env["error"]
