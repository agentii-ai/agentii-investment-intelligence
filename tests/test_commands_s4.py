"""S4 command tests (T050–T054): specify refusal + creation, task decomposition
with mode:all expansion and [P] rules, constitution scaffold + bump validation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentii_cmd  # noqa: E402


def test_specify_refused_while_unratified(tmp_path):
    ws = tmp_path / "workspace"
    # no constitution.md at all → refused
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    assert "unratified" in str(exc.value)
    # scaffolded-but-placeholder → still refused
    agentii_cmd.constitution_scaffold(ws)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    assert "unratified" in str(exc.value)


def test_specify_creates_thesis_after_ratification(tmp_path):
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    (ws / "constitution.md").write_text(
        (ws / "constitution.md").read_text().replace("[WORKSPACE_NAME]", "Test Fund"))
    thesis = agentii_cmd.specify(ws, "mvp")
    assert thesis.name == "001-mvp"
    assert (thesis / "spec.md").is_file()
    assert (thesis / "thesis.md").is_file()
    assert (thesis / "checklists" / "thesis-quality.md").is_file()
    # second call gets a distinct id (mkdir-CAS)
    assert agentii_cmd.specify(ws, "mvp").name == "002-mvp"


def test_task_expansion_mode_all(tmp_path):
    matrix = [{"pillar": "P1", "ticker": "NVDA", "skill": "dcf", "modes": ["all"],
               "all_modes": ["base", "sensitivity", "bear"], "purpose": "valuation"}]
    rows = agentii_cmd.expand_tasks(matrix)
    assert len(rows) == 3  # mode: all expands at generation, never one task
    assert all("× dcf ×" in r for r in rows)
    modes = [r.split("× ")[2].split(" ")[0] for r in rows]
    assert set(modes) == {"base", "sensitivity", "bear"}


def test_task_parallel_marker_by_file_key(tmp_path):
    matrix = [
        {"pillar": "P1", "ticker": "NVDA", "skill": "business-model", "mode": "default"},
        {"pillar": "P1", "ticker": "AMD", "skill": "business-model", "mode": "default"},
        {"pillar": "P1", "ticker": "NVDA", "skill": "business-model", "mode": "deep"},
    ]
    rows = agentii_cmd.expand_tasks(matrix)
    assert "[P] " in rows[0]  # first file key → parallel
    assert "[P] " in rows[1]  # different file (AMD) → parallel
    assert "[P] " not in rows[2]  # same (ticker, skill) file → serialized


def test_task_rows_carry_src_refs(tmp_path):
    rows = agentii_cmd.expand_tasks(
        [{"pillar": "P2", "ticker": "NVDA", "skill": "competitive", "mode": "default",
          "src": "pillar-2"}])
    assert "(src: pillar-2)" in rows[0]


def test_constitution_scaffold_writes_all_five_files(tmp_path):
    ws = tmp_path / "workspace"
    files = agentii_cmd.constitution_scaffold(ws)
    names = {f.name for f in files}
    assert names == {"constitution.md", "constitution.yaml", "assumptions.yaml",
                     "value-checks.yaml", "taxonomy.yaml", ".gitignore"}  # Q77/Q82 cache hygiene


def test_constitution_amend_validates_bump_values(tmp_path):
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.constitution_amend(ws, "trivial", "note")
    assert "bump must be one of" in str(exc.value)
    agentii_cmd.constitution_amend(ws, "minor", "added a principle")
    assert "bump: minor" in (ws / "constitution.md").read_text()
