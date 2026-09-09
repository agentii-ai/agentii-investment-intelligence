"""S3 tests (T037/T038/T039): the full G1 rule set — corpus framing, lookahead,
constitution scalar postcondition, sector-native coverage, data-quality blocking,
value plausibility (fail/warn split), anti-anchoring (blind_estimate)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g1_gate  # noqa: E402

GOOD = """---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "dcf:abc123"
mode: default
data_class: slow
method_selection:
  - ref: sg-001
    decision: adopted
entity_claims:
  - entity: NVDA
    metric: gross_margin
    value: 73.0
    unit: pct
    period: 2026Q2
    source: "xbrl:us-gaap:GrossProfit/Revenues"
    retrieved_at: 2026-09-08T09:12:00-04:00
blind_estimate:
  written_at: 2026-09-08T08:00:00-04:00
  value: 210.0
position_pct: 4.0
---

# NVDA analysis

References /v/NVDA/sec120/page5 and /v/NVDA/sec130/page2 support the margin view.
<ref:strategy id="sg-001" fund="Baillie Gifford" era="2019-2021">
  Methodology summary block.
</ref:strategy>
"""


def _artifact(tmp_path, text=GOOD, name="art.md"):
    art = tmp_path / name
    art.write_text(text)
    return art


# --- T037: full rule set ------------------------------------------------------

def test_full_gate_passes_clean_artifact(tmp_path):
    problems = g1_gate.check_artifact_full(_artifact(tmp_path))
    assert problems == []


def test_unframed_corpus_text_fails(tmp_path):
    # Q19 rule 1: an unclosed (or mismatched) ref block is detectable unframed corpus
    bad = GOOD.replace("</ref:strategy>", "")  # open without close
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("UNFRAMED_REFERENCE" in p or "unframed" in p.lower() for p in problems)


def test_mismatched_closing_tag_fails(tmp_path):
    bad = GOOD.replace("</ref:strategy>", "</ref:analogue_case>")  # same-name rule (Q19)
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("ref" in p.lower() for p in problems)


def test_setup_content_in_citation_slot_fails(tmp_path):
    bad = GOOD + "\n\nSignal from <ref:technical_setup id=\"s1\">a bullish breakout pattern</ref:technical_setup> supports the thesis. /v/NVDA/sec120/page5 cites it."
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("setup" in p.lower() for p in problems)


def test_strategy_without_method_selection_fails(tmp_path):
    bad = GOOD.replace("method_selection:", "method_selection_removed:")
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("method_selection" in p for p in problems)


def test_lookahead_violation_fails(tmp_path):
    bad = GOOD.replace("period: 2026Q2", "period: 2026Q4")  # later than as_of 2026-09-08
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("LOOKAHEAD" in p for p in problems)


def test_constitution_scalar_postcondition(tmp_path):
    constitution = tmp_path / "constitution.yaml"
    constitution.write_text(yaml.dump({
        "constraints": [{"id": "POS_SINGLE", "arity": "scalar", "field": "position_pct",
                         "max": 7.0}]}))
    ok = g1_gate.check_artifact_full(_artifact(tmp_path), constitution_path=constitution)
    assert ok == []
    bad = GOOD.replace("position_pct: 4.0", "position_pct: 12.0")
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad), constitution_path=constitution)
    assert any("CONSTITUTION_BREACH" in p or "position_pct" in p for p in problems)


def test_unratified_constitution_skips_scalar_gracefully(tmp_path):
    bad = GOOD.replace("constitution_pin: 0.1.0", "constitution_pin: unratified")
    constitution = tmp_path / "constitution.yaml"
    constitution.write_text(yaml.dump({
        "constraints": [{"id": "POS_SINGLE", "arity": "scalar", "field": "position_pct",
                         "max": 7.0}]}))
    problems, notices = g1_gate.check_artifact_full(_artifact(tmp_path, bad),
                                                    constitution_path=constitution,
                                                    with_notices=True)
    assert all("constitution" not in p.lower() or "skip" in p.lower() for p in problems)
    assert any("unratified" in n for n in notices)


def test_sector_native_coverage(tmp_path):
    matrix = ["business-model", "recent-quarter"]
    problems = g1_gate.check_sector_native("med.medicines_biotech", matrix)
    assert problems  # no native skill
    matrix2 = matrix + ["fda-catalyst-analysis"]
    assert g1_gate.check_sector_native("med.medicines_biotech", matrix2) == []
    assert g1_gate.check_sector_native("med.healthcare_services", ["business-model"]) == []


def test_blocking_data_quality_fails(tmp_path):
    bad = GOOD.replace("position_pct: 4.0",
                       "data_quality_flags:\n  - source: xbrl\n    severity: blocking")
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad))
    assert any("blocking" in p for p in problems)


# --- T038: value plausibility, fail/warn split ---------------------------------

VC = tmp_path = None  # placeholder, set in fixture


def _value_checks(tmp_path):
    vc = tmp_path / "value-checks.yaml"
    vc.write_text(yaml.dump({"version": 1, "rules": [
        {"id": "margin", "metric": ["gross_margin"], "op": "between", "args": [-1, 1], "level": "fail"},
        {"id": "tg", "metric": "terminal_growth", "op": "lt_ref", "ref_metric": "risk_free_rate", "level": "fail"},
    ]}))
    return vc


def test_value_implausible_fails(tmp_path):
    bad = GOOD.replace("value: 73.0", "value: 7.3")  # 730% margin — definitionally impossible
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad),
                                           value_checks_path=_value_checks(tmp_path))
    assert any("VALUE_IMPLAUSIBLE" in p for p in problems)


def test_statistical_outlier_warns_not_fails(tmp_path):
    # negative margin = warn-class (biotech) — the fail/warn split is load-bearing
    vc = tmp_path / "value-checks.yaml"
    vc.write_text(yaml.dump({"version": 1, "rules": [
        {"id": "neg_margin", "metric": ["gross_margin"], "op": "lt", "args": [0], "level": "warn"}]}))
    bad = GOOD.replace("value: 73.0", "value: -0.4")
    problems, notices = g1_gate.check_artifact_full(_artifact(tmp_path, bad),
                                                    value_checks_path=vc, with_notices=True)
    assert problems == []
    assert any("warn" in n for n in notices)


def test_ref_op_terminal_growth_vs_risk_free(tmp_path):
    # terminal_growth >= risk_free → fail (definitionally impossible per Q21)
    vc = tmp_path / "value-checks.yaml"
    vc.write_text(yaml.dump({"version": 1, "rules": [
        {"id": "tg", "metric": "terminal_growth", "op": "lt_ref",
         "ref_metric": "risk_free_rate", "level": "fail"},
        {"id": "wacc", "metric": "wacc", "op": "gt_ref",
         "ref_metric": "risk_free_rate", "level": "fail"},
    ]}))
    bad = GOOD.replace("metric: gross_margin\n    value: 73.0",
                       "metric: terminal_growth\n    value: 0.04")
    bad = bad.replace("period: 2026Q2", "period: 2026Q2\n  - entity: NVDA\n"
                      "    metric: risk_free_rate\n    value: 0.03\n    period: 2026Q2")
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, bad),
                                           value_checks_path=vc)
    assert any("terminal_growth" in p and "VALUE_IMPLAUSIBLE" in p for p in problems)


# --- T039: anti-anchoring ------------------------------------------------------

def test_blind_estimate_ordering(tmp_path):
    good = GOOD  # written_at 08:00 < retrieved_at 09:12 ✓
    assert g1_gate.check_artifact_full(_artifact(tmp_path, good)) == []
    anchored = GOOD.replace("written_at: 2026-09-08T08:00:00-04:00",
                            "written_at: 2026-09-08T10:00:00-04:00")
    problems = g1_gate.check_artifact_full(_artifact(tmp_path, anchored))
    assert any("blind" in p.lower() or "anchor" in p.lower() for p in problems)
