"""S2 tests (T027–T033): converge.py — append-only gap closure, the cadence engine.

Q26 contract under test:
- clean run leaves tasks.md BYTE-IDENTICAL (no empty section header);
- gaps append a `## Phase N: Convergence` section — never rewrite/reorder/delete;
- evaluation reads artifact CURRENT state (never git history, never `[x]`);
- stale/invalidated are deterministic and uncapped; judgment-class capped (Q40);
- finding IDs are content-derived — re-runs don't duplicate identical findings.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import converge  # noqa: E402

CURRENT_PINS = {"assumption_pin": 1, "corpus_version": "2026-08",
                "as_of": "2026-09-08", "constitution_pin": "0.1.0",
                "skill_pin": "recent-quarter:abc"}

ARTIFACT = """---
assumption_pin: {assumption_pin}
corpus_version: "{corpus_version}"
as_of: {as_of}
constitution_pin: {constitution_pin}
skill_pin: "{skill_pin}"
mode: default
data_class: slow
entity_claims:
  - entity: NVDA
    metric: gross_margin
    value: {gross_margin}
    unit: pct
    period: 2026Q2
    source: "xbrl:us-gaap:GrossProfit/Revenues"
    retrieved_at: 2026-09-08T09:12:00-04:00
---

# Artifact
"""

TASKS = """# Research Tasks

## Phase 1
- [ ] T001 [S1] NVDA × recent-quarter × default (src: Q30/Q79)
"""


def _thesis(tmp_path, *, gross_margin=73.0, pins=None, include_tasks=True,
            wrong_if=None, mark_x=False):
    thesis = tmp_path / "theses" / "001-mvp"
    (thesis / "artifacts" / "NVDA").mkdir(parents=True)
    pins = pins if pins is not None else CURRENT_PINS
    art = ARTIFACT.format(gross_margin=gross_margin, **pins)
    (thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md").write_text(art)
    if include_tasks:
        tasks = TASKS
        if mark_x:
            tasks = tasks.replace("- [ ]", "- [x]")
        (thesis / "tasks.md").write_text(tasks)
    if wrong_if is not None:
        (thesis / "thesis.md").write_text(json.dumps(
            {"mechanical": {}, "judgment": {"wrong_if": wrong_if, "conviction": None,
                                            "claims": []}}))
    return thesis


def test_clean_run_is_byte_identical(tmp_path):
    thesis = _thesis(tmp_path)
    tasks_path = thesis / "tasks.md"
    before = tasks_path.read_bytes()
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "converged"
    assert tasks_path.read_bytes() == before  # Q26: byte-identical, no empty section


def test_missing_pins_yield_stale_gap_append_only(tmp_path):
    stale_pins = dict(CURRENT_PINS, assumption_pin=None)  # older-than-current
    thesis = _thesis(tmp_path, pins=stale_pins)
    tasks_path = thesis / "tasks.md"
    before_lines = tasks_path.read_text().splitlines()
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "gaps_found"
    after = tasks_path.read_text()
    # append-only: every original line intact, in order
    assert after.splitlines()[: len(before_lines)] == before_lines
    assert "## Phase 1: Convergence" in after
    assert "stale" in after
    assert "src:" in after


def test_triggered_wrong_if_yields_invalidated_gap(tmp_path):
    wrong_if = [{"metric": "gross_margin", "threshold": 70, "source": "xbrl", "op": "<"}]
    thesis = _thesis(tmp_path, gross_margin=55.0, wrong_if=wrong_if)
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "gaps_found"
    assert "invalidated" in (thesis / "tasks.md").read_text()


def test_untriggered_wrong_if_is_clean(tmp_path):
    wrong_if = [{"metric": "gross_margin", "threshold": 70, "source": "xbrl", "op": "<"}]
    thesis = _thesis(tmp_path, gross_margin=73.0, wrong_if=wrong_if)
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "converged"


def test_x_mark_is_ignored_artifact_state_is_truth(tmp_path):
    # [x] says done; the artifact is gone — converge must report `missing` (Q26:
    # the ledger can lie; its correction is deterministic).
    thesis = _thesis(tmp_path, mark_x=True)
    (thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md").unlink()
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "gaps_found"
    assert "missing" in (thesis / "tasks.md").read_text()


def test_rerun_does_not_duplicate_identical_findings(tmp_path):
    stale_pins = dict(CURRENT_PINS, as_of="2026-08-01")
    thesis = _thesis(tmp_path, pins=stale_pins)
    converge.run(thesis, current_pins=CURRENT_PINS)
    first = (thesis / "tasks.md").read_text()
    result2 = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result2["status"] == "converged"  # same findings already appended
    assert (thesis / "tasks.md").read_text() == first  # byte-identical second run


def test_finding_ids_are_content_derived():
    a = converge.finding_id("NVDA", "assumption_pin", "2026Q2", "stale")
    b = converge.finding_id("NVDA", "assumption_pin", "2026Q2", "stale")
    c = converge.finding_id("AMD", "assumption_pin", "2026Q2", "stale")
    assert a == b and a != c  # Q40: content-derived, stable across runs


def test_judgment_gaps_are_capped(tmp_path):
    # Judgment-class evaluator (missing/partial/contradicts/unrequested) honors the
    # Q40 cap: with many missing artifacts it reports at most MAX_JUDGMENT_FINDINGS.
    thesis = _thesis(tmp_path)
    for i in range(12):
        (thesis / "artifacts" / f"TKR{i}" / "x_skill_default.md").unlink(missing_ok=True)
    # create 12 task rows referencing missing artifacts
    rows = ["# Research Tasks", "## Phase 1"]
    for i in range(12):
        rows.append(f"- [ ] T{i:03d} [S1] TKR{i} × skill × default (src: Q30)")
    (thesis / "tasks.md").write_text("\n".join(rows))
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "gaps_found"
    assert result["judgment_findings"] <= converge.MAX_JUDGMENT_FINDINGS
