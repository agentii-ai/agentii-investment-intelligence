"""S4 script tests (T047/T059/T060/T061): template resolution stack, scenario DAG
validation, content-derived finding IDs, derived thesis index."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import finding_id  # noqa: E402
import resolve_template  # noqa: E402
import thesis_status  # noqa: E402
import validate_scenes  # noqa: E402


# --- T047: resolve_template ----------------------------------------------------

def _templates(tmp_path):
    t = tmp_path / "templates"
    (t / "overrides").mkdir(parents=True)
    (t / "presets" / "biotech").mkdir(parents=True)
    (t / "presets" / "banks").mkdir(parents=True)
    (t / "plan-template.md").write_text("CORE plan body")
    (t / "presets" / ".registry").write_text(yaml.dump(["biotech", "banks"]))
    return t


def test_core_resolves_when_no_layers_exist(tmp_path):
    t = _templates(tmp_path)
    text, chain = resolve_template.resolve("plan-template.md", kit_templates=t)
    assert text == "CORE plan body"
    assert chain[-1].name == "plan-template.md"


def test_kit_override_wins_and_stops(tmp_path):
    t = _templates(tmp_path)
    (t / "overrides" / "plan-template.md").write_text("OVERRIDE body")
    text, chain = resolve_template.resolve("plan-template.md", kit_templates=t)
    assert text == "OVERRIDE body"


def test_preset_wrap_composes_over_core(tmp_path):
    t = _templates(tmp_path)
    (t / "presets" / "biotech" / "plan-template.md").write_text(
        "---\n_strategy: wrap\n---\nFDA SECTION\n{CORE_TEMPLATE}\nCLINICAL SECTION\n")
    text, _chain = resolve_template.resolve("plan-template.md", kit_templates=t)
    assert text.startswith("FDA SECTION")
    assert "CORE plan body" in text
    assert text.rstrip().endswith("CLINICAL SECTION")


def test_workspace_layer_is_highest_priority(tmp_path):
    t = _templates(tmp_path)
    (t / "overrides" / "plan-template.md").write_text("OVERRIDE body")
    ws = tmp_path / "workspace"
    (ws / ".agentii" / "orchestration" / "templates" / "overrides").mkdir(parents=True)
    (ws / ".agentii" / "orchestration" / "templates" / "overrides" / "plan-template.md").write_text("WORKSPACE body")
    text, _ = resolve_template.resolve("plan-template.md", workspace_root=ws, kit_templates=t)
    assert text == "WORKSPACE body"


def test_missing_template_raises(tmp_path):
    t = _templates(tmp_path)
    with pytest.raises(FileNotFoundError):
        resolve_template.resolve("ghost-template.md", kit_templates=t)


# --- T059: validate_scenes -----------------------------------------------------

def test_scene_with_unresolvable_node_fails(tmp_path):
    scenes = tmp_path / "scenes"
    (scenes / "full-equity-research").mkdir(parents=True)
    (scenes / "full-equity-research" / "SKILL.md").write_text("""---
name: full-equity-research
role: orchestrator
---
stages:
  - skill: business-model
  - skill: ghost-skill
""")
    problems = validate_scenes.validate_skill(scenes / "full-equity-research",
                                              {"business-model", "recent-quarter"})
    assert any("ghost-skill" in p for p in problems)


def test_scene_resolving_passes(tmp_path):
    scenes = tmp_path / "scenes"
    (scenes / "full-equity-research").mkdir(parents=True)
    (scenes / "full-equity-research" / "SKILL.md").write_text("""---
name: full-equity-research
role: orchestrator
---
stages:
  - skill: business-model
  - skill: recent-quarter
""")
    assert validate_scenes.validate_skill(scenes / "full-equity-research",
                                          {"business-model", "recent-quarter"}) == []


def test_kit_body_is_not_dag_checked(tmp_path):
    scenes = tmp_path / "scenes"
    (scenes / "converge").mkdir(parents=True)
    (scenes / "converge" / "SKILL.md").write_text("""---
name: converge
role: kit
---
# Append-only gap closure
""")
    assert validate_scenes.validate_skill(scenes / "converge", set()) == []


# --- T060: finding_id ----------------------------------------------------------

def test_finding_ids_are_content_derived_and_stable():
    a = finding_id.finding_id("NVDA", "gross_margin", "2026Q2", "stale")
    b = finding_id.finding_id("NVDA", "gross_margin", "2026Q2", "stale")
    c = finding_id.finding_id("NVDA", "gross_margin", "2026Q3", "stale")
    assert a == b and a != c
    assert len(a) == 12


# --- T061: thesis_status -------------------------------------------------------

def test_status_scan_and_index_emit(tmp_path):
    ws = tmp_path / "workspace"
    thesis = ws / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "thesis.md").write_text(
        '{"mechanical": {}, "judgment": {"claims": [{"id": "c-1", "state": "pending_review"}], '
        '"conviction": null, "wrong_if": []}}')
    # frontmatter-style data isn't used here; status reads the JSON doc + frontmatter
    rows = thesis_status.scan_workspace(ws)
    assert rows[0]["id"] == "001-mvp"
    assert rows[0]["pending_review"] == 1
    index = thesis_status.render_index(rows)
    assert index.startswith(thesis_status.INDEX_HEADER.rstrip())
    assert "001-mvp" in index
    # Check 34's property: regeneration is byte-identical (pure function of input)
    assert thesis_status.render_index(rows) == index
