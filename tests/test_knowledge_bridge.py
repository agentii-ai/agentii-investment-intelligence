"""T041 — tests for scripts/knowledge_bridge.py (write FIRST).

The bridge maps enrichment stages to spec-037 MCP queries and selects the runtime
analogue axis by domain. spec-037 is injected (a fake client) so CI is deterministic
and key-free. Covers: axis selection, empty-result path, coverage_gap annotation.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE = REPO_ROOT / "scripts" / "knowledge_bridge.py"


def _load():
    spec = importlib.util.spec_from_file_location("knowledge_bridge", BRIDGE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeClient:
    """Stand-in spec-037 MCP client returning canned rows."""
    def __init__(self, rows=None, raise_on=None):
        self._rows = rows or {}
        self._raise_on = raise_on or set()

    def search_investment_strategies(self, **kw):
        if "strategies" in self._raise_on:
            raise ConnectionError("spec-037 unreachable")
        return self._rows.get("strategies", [])

    def search_investment_cases(self, **kw):
        return self._rows.get("cases", [])

    def search_technical_setups(self, **kw):
        return self._rows.get("setups", [])


def test_script_exists():
    assert BRIDGE.is_file()


def test_axis_selection_by_domain():
    mod = _load()
    assert mod.select_analogue_axis("valuation") == "strategy"
    assert mod.select_analogue_axis("competitive positioning") == "case"
    assert mod.select_analogue_axis("price action / technical") == "setup"
    # unknown domain falls back to strategy
    assert mod.select_analogue_axis("something-else") == "strategy"


def test_fetch_strategies_maps_to_rows():
    mod = _load()
    client = FakeClient(rows={"strategies": [
        {"strategy_id": "s1", "title": "Moat", "kind": "quality", "summary": "wide moat", "citation_id": "s1", "ticker": "AAPL", "page": 3},
    ]})
    result = mod.fetch_enrichment(client, "strategy-enrichment", skill_entry={"layer_tags": ["L2"], "category_tags": ["K1"]})
    assert result["status"] == "ok"
    rows = result["records"]["strategies"]
    assert rows[0]["citation_id"] == "s1"
    # citation link is the clickable /v/ form
    assert any("agentii.ai/v/" in str(c) for c in rows[0]["columns"])


def test_empty_result_path():
    mod = _load()
    client = FakeClient(rows={"strategies": []})
    result = mod.fetch_enrichment(client, "strategy-enrichment", skill_entry={"layer_tags": ["L2"]})
    assert result["status"] == "empty"
    assert result["records"]["strategies"] == []


def test_coverage_gap_on_unreachable():
    mod = _load()
    client = FakeClient(raise_on={"strategies"})
    result = mod.fetch_enrichment(client, "strategy-enrichment", skill_entry={"layer_tags": ["L2"]})
    assert result["status"] == "coverage_gap"
    assert "coverage_gap" in result
    assert result["records"] == {}


def test_setup_enrichment_only_l4():
    mod = _load()
    client = FakeClient(rows={"setups": [{"setup_id": "st1", "title": "Flag", "pattern_type": "continuation", "timeframe": "1D", "citation_id": "st1", "ticker": "SPY", "page": 1}]})
    l2 = mod.fetch_enrichment(client, "setup-enrichment", skill_entry={"layer_tags": ["L2"]})
    assert l2["status"] == "skipped"  # L4-only preset on non-L4 skill
    l4 = mod.fetch_enrichment(client, "setup-enrichment", skill_entry={"layer_tags": ["L4"]})
    assert l4["status"] == "ok"
