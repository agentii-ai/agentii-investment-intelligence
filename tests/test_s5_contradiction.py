"""S5 tests (T066–T069): entity index contradiction detection, aggregate
constitution postconditions, the daily sweep (expiry/drift/dependency), and the
G2 validator harness."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dispatch  # noqa: E402
import g2_validator  # noqa: E402
import reduce_journals  # noqa: E402

GOOD = """---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "x:y"
mode: default
data_class: slow
entity_claims:
  - entity: NVDA
    metric: {metric}
    value: {value}
    unit: pct
    period: 2026Q2
    source: "xbrl:x"
    retrieved_at: {retrieved_at}
position_pct: {pos}
sector: {sector}
---

# body
"""


def _artifact(thesis: Path, name: str, metric="gross_margin", value=73.0,
              retrieved_at="2026-09-08T09:12:00-04:00", pos=4.0, sector="semis"):
    art = thesis / "artifacts" / name
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(GOOD.format(metric=metric, value=value, retrieved_at=retrieved_at,
                               pos=pos, sector=sector))
    return art


# --- T067: entity index --------------------------------------------------------

def test_same_fact_same_value_no_contradiction(tmp_path):
    thesis = tmp_path / "t"
    _artifact(thesis, "a1.md")
    _artifact(thesis, "a2.md")
    idx = reduce_journals.build_entity_index(thesis / "artifacts")
    assert idx["contradictions"] == []
    assert idx["suspected_restatements"] == []


def test_direct_contradiction_detected(tmp_path):
    thesis = tmp_path / "t"
    _artifact(thesis, "a1.md", value=73.0)
    _artifact(thesis, "a2.md", value=61.0)  # same fact, different value, same retrieval
    idx = reduce_journals.build_entity_index(thesis / "artifacts")
    assert idx["contradictions"], idx
    assert idx["contradictions"][0]["entity"] == "NVDA"


def test_different_retrieved_at_is_suspected_restatement(tmp_path):
    thesis = tmp_path / "t"
    _artifact(thesis, "a1.md", value=73.0, retrieved_at="2026-06-01T00:00:00-04:00")
    _artifact(thesis, "a2.md", value=73.0, retrieved_at="2026-09-08T09:12:00-04:00")
    idx = reduce_journals.build_entity_index(thesis / "artifacts")
    # same value: nothing to compare. Use differing values across retrieval times:
    _artifact(thesis, "a3.md", value=61.0, retrieved_at="2026-09-08T09:12:00-04:00")
    idx = reduce_journals.build_entity_index(thesis / "artifacts")
    assert idx["suspected_restatements"]  # 73 (old retrieval) vs 61 (new retrieval)
    assert idx["contradictions"] == []  # never reported as a direct contradiction


# --- T068: aggregate postconditions -------------------------------------------

CONST = """constraints:
  - id: CONC_SECTOR
    arity: aggregate
    group_by: sector
    max: 25.0
  - id: EXPO_MACRO
    arity: aggregate
    group_by: macro_driven
    max: 40.0
"""


def test_aggregate_breach_reported_never_resolved(tmp_path):
    thesis = tmp_path / "t"
    for i in range(8):
        _artifact(thesis, f"a{i}.md", pos=4.0)  # 8 × 4% semis = 32% > 25%
    con = tmp_path / "constitution.yaml"
    con.write_text(CONST)
    problems = reduce_journals.check_aggregate(thesis / "artifacts", con)
    assert any("CONSTITUTION_BREACH" in p and "CONC_SECTOR" in p for p in problems)


def test_aggregate_hard_fails_unratified(tmp_path):
    thesis = tmp_path / "t"
    unratified = GOOD.replace("constitution_pin: 0.1.0", "constitution_pin: unratified")
    art = thesis / "artifacts" / "a.md"
    art.parent.mkdir(parents=True)
    art.write_text(unratified)
    con = tmp_path / "constitution.yaml"
    con.write_text(CONST)
    problems, notices = reduce_journals.check_aggregate(
        thesis / "artifacts", con, with_notices=True)
    assert any("unratified" in p for p in problems)  # hard fail, not a notice


def test_aggregate_passes_within_limits(tmp_path):
    thesis = tmp_path / "t"
    _artifact(thesis, "a1.md", pos=4.0)
    _artifact(thesis, "a2.md", pos=5.0)  # 9% ≤ 25%
    con = tmp_path / "constitution.yaml"
    con.write_text(CONST)
    assert reduce_journals.check_aggregate(thesis / "artifacts", con) == []


# --- T069: daily sweep ---------------------------------------------------------

def test_expiry_trigger_flips_pending_review(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "thesis.md").write_text(json.dumps({
        "judgment": {"claims": [
            {"id": "c-1", "entity": "NVDA", "state": "pinned"}]},
        "expiry_triggers": ["earnings_release"], "subscriptions": ["NVDA"]}))
    calendar = {"2026-09-08": ["NVDA"]}  # fake earnings calendar
    flips = dispatch.daily_sweep([thesis], earnings_calendar=calendar,
                                 constitution=None, theses_by_id={})
    assert any("c-1" in f for f in flips)


def test_dependency_propagation_flips_consumer(tmp_path):
    upstream = tmp_path / "theses" / "007-nvda"
    upstream.mkdir(parents=True)
    (upstream / "thesis.md").write_text(json.dumps({
        "judgment": {"claims": [{"id": "c-001", "state": "superseded"}]}}))
    downstream = tmp_path / "theses" / "012-sector"
    downstream.mkdir(parents=True)
    (downstream / "thesis.md").write_text(json.dumps({
        "judgment": {"claims": [{"id": "s-1", "state": "pinned",
                                 "depends_on": ["c-001"]}]},
        "depends_on": [{"thesis_id": "007", "claims": ["c-001"]}]}))
    flips = dispatch.daily_sweep([upstream, downstream], earnings_calendar={},
                                 constitution=None, theses_by_id={"007": upstream})
    assert any("s-1" in f and "pending_review" in f for f in flips)


def test_constitution_drift_finding(tmp_path):
    constitution = tmp_path / "constitution.yaml"
    constitution.write_text(yaml.dump({
        "regime": {"declared": "expansion",
                   "drift_triggers": [{"indicator": "ISM Manufacturing PMI",
                                       "condition": "ISM < 50 for 2 consecutive months"}]}}))
    indicators = {"ISM Manufacturing PMI": [48.1, 49.0]}  # 2 months < 50 → drift
    findings = dispatch.check_constitution_drift(constitution, indicators)
    assert any("constitution_drift" in f for f in findings)


# --- T066: G2 validator harness ------------------------------------------------

def test_g2_verdict_schema_is_fixed():
    verdict = g2_validator.make_verdict(artifact="a.md", falsifiable=True,
                                        contradictions=[], supports=True)
    g2_validator.validate_verdict(verdict)  # must not raise
    bad = dict(verdict)
    bad.pop("falsifiable")
    with pytest.raises(ValueError):
        g2_validator.validate_verdict(bad)


def test_g2_dispatch_runs_injected_validator(tmp_path):
    def fake_validator(artifact: Path, prompt: str) -> dict:
        assert "bounded prompt" in prompt  # the prompt is narrowed, never open-ended
        return g2_validator.make_verdict(artifact=str(artifact), falsifiable=True,
                                         contradictions=[], supports=True)
    verdict = g2_validator.dispatch(tmp_path / "a.md", fake_validator)
    assert verdict["falsifiable"] is True
