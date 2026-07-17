"""T018 — tests for the idempotent knowledge-frameworks writer (write FIRST).

Covers: create-from-template when missing, idempotent citation insert (dedupe
by citation_id), and preservation of existing rows. Deterministic — the writer
takes explicit citation records (no LLM/MCP calls).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "enhance_skill", REPO_ROOT / "scripts" / "enhance-skill.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def strategy_rows():
    return [
        {"citation_id": "str_001", "columns": ["str_001", "Moat Durability", "quality", "wide-moat compounding", "AAPL"]},
        {"citation_id": "str_002", "columns": ["str_002", "Mean Reversion", "value", "oversold snapback", "AAPL"]},
    ]


def test_creates_from_template_when_missing(tmp_path, strategy_rows):
    mod = _load()
    kf = tmp_path / "references" / "knowledge-frameworks.md"
    n = mod.insert_citations(kf, table="strategies", rows=strategy_rows, skill_name="demo")
    assert kf.is_file()
    assert n == 2
    text = kf.read_text()
    assert "## Referenced Strategies" in text
    assert "str_001" in text and "str_002" in text


def test_idempotent_insert_dedupes_by_citation_id(tmp_path, strategy_rows):
    mod = _load()
    kf = tmp_path / "references" / "knowledge-frameworks.md"
    mod.insert_citations(kf, table="strategies", rows=strategy_rows, skill_name="demo")
    # second run with the same rows -> zero new inserts, identical content
    before = kf.read_text()
    n = mod.insert_citations(kf, table="strategies", rows=strategy_rows, skill_name="demo")
    assert n == 0
    assert kf.read_text() == before


def test_insert_appends_only_new_rows(tmp_path, strategy_rows):
    mod = _load()
    kf = tmp_path / "references" / "knowledge-frameworks.md"
    mod.insert_citations(kf, table="strategies", rows=strategy_rows[:1], skill_name="demo")
    n = mod.insert_citations(kf, table="strategies", rows=strategy_rows, skill_name="demo")
    assert n == 1  # only str_002 is new
    text = kf.read_text()
    assert text.count("str_001") == 1
    assert text.count("str_002") == 1


def test_count_citations_helper(tmp_path, strategy_rows):
    mod = _load()
    kf = tmp_path / "references" / "knowledge-frameworks.md"
    mod.insert_citations(kf, table="strategies", rows=strategy_rows, skill_name="demo")
    assert mod.count_citations(kf) == 2
