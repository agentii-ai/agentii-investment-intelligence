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


def test_scaffold_refuses_to_clobber_ratified_constitution(tmp_path):
    """D75 #3: a ratified constitution is the workspace's doctrine — scaffold must
    refuse to overwrite it silently (the dogfooding session clobbered a ratified
    v1.0.0 with placeholders). --force is the deliberate reset."""
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    (ws / "constitution.md").write_text(
        (ws / "constitution.md").read_text().replace("[WORKSPACE_NAME]", "Test Fund"))
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.constitution_scaffold(ws)
    assert "already ratified" in str(exc.value)
    # the ratified doctrine survived the refused scaffold
    assert "Test Fund" in (ws / "constitution.md").read_text()
    # --force is the deliberate reset path
    agentii_cmd.constitution_scaffold(ws, force=True)
    assert "[WORKSPACE_NAME]" in (ws / "constitution.md").read_text()


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


# --- F1 remediation: the SKILL.md-documented spec-matrix path -----------------

SPEC_MATRIX = """## 3. Skill Deployment Matrix
| Skill | Vertical | Depth | Tickers | Market Data Stage | Purpose |
|---|---|:---:|---|---|---|
| `business-model` | ERC | Full | NVDA, AMD | none | understand |
| `recent-quarter` | ERC | Light | NVDA | none | earnings |
"""


def test_parse_spec_matrix():
    rows = agentii_cmd.parse_spec_matrix(SPEC_MATRIX)
    assert [r["skill"] for r in rows] == ["business-model", "recent-quarter"]
    assert rows[0]["tickers"] == ["NVDA", "AMD"]
    assert rows[0]["depth"] == "full"
    assert rows[1]["depth"] == "light"


def test_depth_to_modes_q79_merge():
    import yaml

    reg = yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    deep_modes = agentii_cmd.depth_to_modes("full", reg, "business-model")
    assert len(deep_modes) >= 3  # registry-expanded: the skill's real mode slugs
    light_modes = agentii_cmd.depth_to_modes("light", reg, "business-model")
    assert light_modes  # essentials_modes (backfilled in S7)
    assert light_modes != deep_modes or len(light_modes) < len(deep_modes)


def test_tasks_from_spec_end_to_end(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_MATRIX)
    import subprocess

    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "agentii_cmd.py"), "tasks",
         "--thesis", str(thesis), "--spec", str(spec)],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    rows = [l for l in res.stdout.splitlines() if l.startswith("- [ ]")]
    # Full-depth business-model × {NVDA, AMD} expands to registry modes; the
    # Light-depth recent-quarter row carries essentials_modes.
    bm_rows = [r for r in rows if "business-model" in r]
    rq_rows = [r for r in rows if "recent-quarter" in r]
    assert len(bm_rows) >= 6  # 2 tickers × ≥3 deep modes
    import yaml

    reg = yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    essentials = next(s["essentials_modes"] for s in reg["skills"]
                      if s["skill_name"] == "recent-quarter")
    # Light = essentials_modes (Q79): 1 ticker × len(essentials) rows
    assert len(rq_rows) == len(essentials)
    assert any("× business-model ×" in r for r in bm_rows)


# --- D75 #4: agentii.clarify (the 8th kit command) ----------------------------

SPEC_UNDERSPEC = """# Research Thesis: x

## 1. Research Question
Which humanoid companies win?

### Pillar 1 — (Priority: P1)
**wrong_if**: If adoption stalls.

**Subscribed**: NVDA, TSLA

## 2. Universe Definition
| Ticker | Company | Sector | Weight | Rationale for Inclusion |
|---|---|:---:|---|
| TSLA | Tesla | Tech | 20% |  |
| NVDA | NVIDIA | Tech | 20% | Compute leader |
"""


def test_clarify_scanner_finds_underspecified_items(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC)
    qs = agentii_cmd.clarify_questions(spec)
    ids = {q["id"] for q in qs}
    assert "wrongif-0" in ids          # prose wrong_if → machine-checkable
    assert "rationale-TSLA" in ids     # universe row without rationale
    assert "budget" in ids             # Q58 undeclared
    assert "expiry" in ids             # Q59 undeclared
    assert "subscriptions" in ids      # tokens not in TICKER × skill form
    assert len(qs) <= agentii_cmd.MAX_CLARIFY_QUESTIONS


def test_clarify_scanner_clean_spec_yields_fewer_questions(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC.replace("If adoption stalls.",
                                           "metric=units threshold=1000 source=company"))
    qs = agentii_cmd.clarify_questions(spec)
    assert not any(q["id"] == "wrongif-0" for q in qs)


def test_clarify_encode_appends_clarifications_section(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC)
    report = agentii_cmd.clarify_encode(spec, [
        {"question": "Declare the thesis budget", "answer": "{max_tasks: 80, max_retries_per_task: 2}"}])
    text = spec.read_text()
    assert "## Clarifications" in text
    assert "max_tasks: 80" in text
    assert "encoded 1 answer" in report
    # second encode appends, never rewrites
    agentii_cmd.clarify_encode(spec, [
        {"question": "Q2", "answer": "A2"}])
    assert text.count("## Clarifications") == 1
