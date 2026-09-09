"""S4 extension tests (T053/T055/T057): skill_pin hashing + budget enforcement,
converge extensions (skill_version_mix / checklist re-evaluation / budget_paused),
pending_gate aging in thesis_status."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import converge  # noqa: E402
import dispatch  # noqa: E402
import thesis_status  # noqa: E402


# --- T053: implement budget + skill_pin ---------------------------------------

def test_skill_version_hash_is_content_derived(tmp_path):
    sk = tmp_path / "skill"
    (sk / "references").mkdir(parents=True)
    (sk / "SKILL.md").write_text("# v1\n")
    h1 = dispatch.skill_version_hash(sk)
    (sk / "SKILL.md").write_text("# v2 — methodology changed\n")
    h2 = dispatch.skill_version_hash(sk)
    assert h1 != h2 and len(h1) == 12


def test_budget_halt_is_deterministic():
    halted, msg = dispatch.enforce_budget(41, {"max_tasks": 40})
    assert halted and "BUDGET_HALT" in msg
    halted, _ = dispatch.enforce_budget(40, {"max_tasks": 40})
    assert not halted
    halted, _ = dispatch.enforce_budget(999, None)  # no budget declared → no gate
    assert not halted


def test_skill_pin_appends_not_overwrites(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    dispatch.record_skill_pin(thesis, "dcf", "aaa111")
    dispatch.record_skill_pin(thesis, "dcf", "bbb222")  # version change → append
    lines = (thesis / "skill_pins.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    assert "aaa111" in lines[0] and "bbb222" in lines[1]


# --- T055: converge extensions ------------------------------------------------

def test_skill_version_mix_detection(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    (thesis / "artifacts" / "NVDA").mkdir(parents=True)
    (thesis / "artifacts" / "NVDA" / "a_recent-quarter_default.md").write_text("""---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "recent-quarter:oldhash1"
mode: default
data_class: slow
---

# body
""")
    (thesis / "tasks.md").write_text("# tasks\n")
    # current hash differs from the artifact's recorded hash → mix
    findings = converge.check_skill_version_mix(
        thesis, {"recent-quarter": "newhash2"})
    assert any("skill_version_mix" in f or "version" in f.lower() for f in findings)
    findings_ok = converge.check_skill_version_mix(
        thesis, {"recent-quarter": "oldhash1"})
    assert findings_ok == []


def test_budget_paused_finding(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "tasks.md").write_text("# tasks\n")
    (thesis / "thesis.md").write_text('{"judgment": {"budget_paused": true}}')
    result = converge.run(thesis, current_pins={"assumption_pin": 1})
    assert "budget_paused" in (thesis / "tasks.md").read_text() or \
           result["status"] == "gaps_found"


def test_checklist_reevaluation_regressions(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "tasks.md").write_text("# tasks\n")
    (thesis / "checklists").mkdir(parents=True)
    (thesis / "checklists" / "thesis-quality.md").write_text(
        "- [x] CHK001 wrong_if 均含 metric+threshold+source [Measurability]\n")
    # no spec.md at all → the measurable items fail → regression (unchecked again)
    regressions = converge.re_evaluate_checklist(thesis)
    assert regressions  # something regressed when requirements are absent


# --- T057: pending_gate aging --------------------------------------------------

def test_pending_gate_aging_surfaced(tmp_path):
    ws = tmp_path / "workspace"
    thesis = ws / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "thesis.md").write_text(
        '{"judgment": {"claims": [{"id": "c-9", "state": "pending_gate", '
        '"gate_since": "2026-09-01T10:00:00-04:00"}]}}')
    rows = thesis_status.scan_workspace(ws)
    assert rows[0]["pending_review"] == 0
    # pending_gate claims count and age are surfaced (Q80: blocking is observable)
    gates = thesis_status.pending_gates(rows[0], ws / "theses" / "001-mvp")
    assert any("c-9" in g for g in gates)
