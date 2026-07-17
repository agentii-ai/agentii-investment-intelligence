"""T035 — tests for scripts/quality-scan.py (write FIRST).

5 dimensions, each 0-2 (total 0-10): Completeness, Knowledge Density,
Citation Integrity, Methodology Depth, Output Structure. Deterministic:
scores computed from on-disk SKILL.md + references/, no LLM/MCP.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
QSCAN = REPO_ROOT / "scripts" / "quality-scan.py"


def _load():
    spec = importlib.util.spec_from_file_location("quality_scan", QSCAN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _skill(tmp_path, *, name="demo", with_kf=True, refs=3, methodology=True,
           output_structure=True, error_handling=True):
    d = tmp_path / "plugins" / "vertical-plugins" / "equity-research-core" / "skills" / "agentii" / name
    (d / "references").mkdir(parents=True)
    body = ["---", f"name: {name}", "multi_ticker_semantics: single_target", "---", ""]
    if methodology:
        body += ["## Methodology", "### Step 1", "### Step 2", "### Step 3",
                 "### Step 4", "### Step 5", ""]
    if output_structure:
        body += ["## Output Structure", "line1", "line2", "line3", "line4", "line5", ""]
    if error_handling:
        body += ["## Error Handling", "handle it", ""]
    (d / "SKILL.md").write_text("\n".join(body))
    if with_kf:
        rows = "\n".join(
            f"| str_{i:03d} | T{i} | quality | one-line | https://agentii.ai/v/AAPL/str_{i:03d}/1 |"
            for i in range(refs)
        )
        (d / "references" / "knowledge-frameworks.md").write_text(
            "# Knowledge Frameworks\n\n## Referenced Strategies\n\n"
            "| strategy_id | title | kind | one-line | cite |\n|---|---|---|---|---|\n" + rows + "\n"
        )
    return d


def test_script_exists():
    assert QSCAN.is_file()


def test_full_score_skill(tmp_path):
    mod = _load()
    d = _skill(tmp_path, refs=5)
    rep = mod.score_skill(d)
    assert rep["score"] == 10.0
    assert set(rep["dimensions"]) == {
        "completeness", "knowledge_density", "citation_integrity",
        "methodology_depth", "output_structure",
    }


def test_missing_knowledge_frameworks_drops_density(tmp_path):
    mod = _load()
    d = _skill(tmp_path, with_kf=False)
    rep = mod.score_skill(d)
    assert rep["dimensions"]["knowledge_density"] == 0
    assert "knowledge_density" in rep["failing_dimensions"]
    assert rep["score"] < 10.0


def test_missing_error_handling_drops_completeness(tmp_path):
    mod = _load()
    d = _skill(tmp_path, error_handling=False)
    rep = mod.score_skill(d)
    assert rep["dimensions"]["completeness"] < 2


def test_shallow_methodology_drops_depth(tmp_path):
    mod = _load()
    d = _skill(tmp_path, methodology=False)
    rep = mod.score_skill(d)
    assert rep["dimensions"]["methodology_depth"] < 2


def test_broken_citation_drops_integrity(tmp_path):
    mod = _load()
    d = _skill(tmp_path, with_kf=True, refs=1)
    kf = d / "references" / "knowledge-frameworks.md"
    kf.write_text(
        "## Referenced Strategies\n\n| strategy_id | title | kind | one | cite |\n|---|---|---|---|---|\n"
        "| str_x | T | quality | one | (no citation link) |\n"
    )
    rep = mod.score_skill(d)
    assert rep["dimensions"]["citation_integrity"] < 2


def test_threshold_gate_pass_fail(tmp_path):
    mod = _load()
    good = _skill(tmp_path / "g", refs=5)
    bad = _skill(tmp_path / "b", with_kf=False, methodology=False)
    assert mod.score_skill(good)["score"] >= 7
    assert mod.score_skill(bad)["score"] < 7


def test_cli_json_shape_and_threshold(tmp_path):
    import yaml
    _skill(tmp_path, name="business-model", refs=5)
    reg = tmp_path / "skill-registry.yaml"
    reg.write_text(yaml.safe_dump({"version": "1.0.0", "skills": [
        {"skill_name": "business-model", "vertical": "equity-research-core", "layer_tags": ["L2"]},
    ]}))
    res = subprocess.run(
        [sys.executable, str(QSCAN), "--json", "--threshold", "7",
         "--registry", str(reg), "--skills-root", str(tmp_path / "plugins")],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    payload = json.loads(res.stdout)
    assert "results" in payload
    entry = payload["results"][0]
    for k in ("skill", "score", "dimensions", "failing_dimensions"):
        assert k in entry
