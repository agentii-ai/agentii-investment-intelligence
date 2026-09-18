"""test_hypothesis_lifecycle.py — T123. The hypothesis register's whole life.

Q84's opening argument is why this is a gate set rather than guidance: *optional
verification in finance equals no verification* — under token pressure and eight
parallel sub-agents an agent will skip it, so the bar has to be structural. Each
test below pins one structural bar.

The lifecycle these cover:

    created (VACUOUS, no epistemic_state)          T117
      -> has a mechanical falsifier?               T121  no  -> narrative note
      -> all support analogical?                   T115  yes -> keep, don't promote
      -> regulatory claim?                         T118  needs presence + decision
      -> two theses, one hypothesis                T119  -> ONE row
      -> refuted                                   T120  -> the same path as wrong_if
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import converge  # noqa: E402
import g1_gate  # noqa: E402
import portfolio_aggregate as pa  # noqa: E402


# ── T117: the creation rule ─────────────────────────────────────────────────

def test_a_new_claim_is_vacuous_and_has_no_epistemic_state():
    """Why this rule and not `epistemic_state: null`: Q85/Q129 keep the two axes
    orthogonal — 'was it examined' and 'what is its standing'. A claim that has
    not been examined must SAY so (VACUOUS, Q105) rather than omit the question,
    and it must not claim a standing it has not earned. `null` would be a third
    value the `epistemic_state` axis does not have."""
    import jsonschema
    schema = json.loads((ROOT.parent / "specs" / "046-agentii-research-orchestration"
                         / "contracts" / "thesis-frontmatter.schema.json")
                        .read_text(encoding="utf-8"))
    claim = {"id": "C1", "entity": "NVDA", "mechanism_outcome": "VACUOUS"}
    jsonschema.validate(
        {"claim": "x",
         "pillars": [{"id": "PIL-1", "priority": "P1", "wrong_if": []}],
         "judgment": {"claims": [claim]}},
        schema)
    assert "epistemic_state" not in claim
    # …and the schema REQUIRES the one it must carry
    req = schema["properties"]["judgment"]["properties"]["claims"]["items"]["required"]
    assert "mechanism_outcome" in req
    assert "epistemic_state" not in req, (
        "epistemic_state must stay OPTIONAL — it appears only once something "
        "evaluated the claim")


def test_the_taxonomy_actually_carries_the_three_axes_the_lifecycle_uses():
    """A schema naming a value the taxonomy does not define is the drift Q76
    exists to prevent."""
    import yaml
    axes = yaml.safe_load((ROOT / "contracts" / "taxonomy.yaml").read_text())["axes"]
    for axis, needed in (("mechanism_outcome", {"EXECUTED", "VACUOUS"}),
                         ("epistemic_state", {"supported", "indeterminate", "refuted"}),
                         ("source_classes", {"experiment_readout", "regulatory_decision",
                                             "audited_filing", "similarity_retrieval",
                                             "kol_commentary", "analogy"})):
        assert needed <= set(axes[axis]), (axis, set(axes[axis]))


# ── T115: promotion refused on analogical-only support ──────────────────────

def test_promotion_refused_when_every_support_class_is_analogical():
    fm = {"entity_claims": [{"id": "C1",
                             "source_classes": ["analogy", "kol_commentary"]}]}
    problems = g1_gate.check_evidence_class(fm)
    assert problems and "promotion refused" in problems[0]


def test_one_verified_class_is_enough_to_promote():
    """Q84 refuses promotion on ALL-analogical, not on ANY-analogical. A claim
    resting on a filing AND an analogy is a claim with a filing."""
    fm = {"entity_claims": [{"id": "C1",
                             "source_classes": ["analogy", "audited_filing"]}]}
    assert g1_gate.check_evidence_class(fm) == []


def test_a_claim_with_no_recorded_class_is_left_to_the_falsifier_gate():
    """Absence of `source_classes` is a different problem from an analogical set,
    and each gate reports its own subject — Q100's two-conditions-two-messages."""
    assert g1_gate.check_evidence_class({"entity_claims": [{"id": "C1"}]}) == []


# ── T121: no mechanical falsifier ⇒ not a hypothesis ────────────────────────

def test_a_claim_without_a_mechanical_falsifier_is_refused_as_a_hypothesis():
    problems = g1_gate.check_falsifier_completeness({"entity_claims": [{"id": "C1"}]})
    assert problems and "not a hypothesis" in problems[0]


def test_a_string_falsifier_needs_the_metric_threshold_source_triple():
    assert g1_gate.check_falsifier_completeness(
        {"entity_claims": [{"id": "C1",
                            "falsifier": "metric=x threshold=y source=z"}]}) == []
    assert g1_gate.check_falsifier_completeness(
        {"entity_claims": [{"id": "C1", "falsifier": "margin falls"}]}), \
        "a prose falsifier is not mechanical"


# ── T118: regulatory promotion on presence + decision, never a value match ──

_ROWS = [{"application_number": "NDA123", "decision": "Approved"},
         {"application_number": "NDA456", "decision": None}]


def test_regulatory_promotion_needs_the_application_number_to_match():
    """The measured failure a value match would cause: promoting a claim because
    some row happened to carry the same number, without that row being about the
    claim's subject at all."""
    problems = g1_gate.check_regulatory_promotion(
        {"entity_claims": [{"id": "C1", "application_number": "NDA999"}]}, _ROWS)
    assert problems and "never a value match" in problems[0]


def test_a_row_present_but_with_a_null_decision_does_not_promote():
    problems = g1_gate.check_regulatory_promotion(
        {"entity_claims": [{"id": "C1", "application_number": "NDA456"}]}, _ROWS)
    assert problems, "presence alone is not judgement — the decision must be non-null"


def test_a_matching_row_with_a_decision_promotes():
    assert g1_gate.check_regulatory_promotion(
        {"entity_claims": [{"id": "C1", "application_number": "NDA123"}]}, _ROWS) == []


# ── T119 / T122: one hypothesis, one row ────────────────────────────────────

_FALSIFIER = {"metric": "gross_margin", "threshold": "0.60", "source": "10-K"}


def test_two_theses_asserting_one_hypothesis_produce_ONE_row():
    claims = {
        "001-a": [{"id": "C1", "entity": "NVDA", "state": "pinned",
                   "epistemic_state": "supported", "falsifier": _FALSIFIER}],
        "002-b": [{"id": "C2", "entity": "NVDA", "state": "pinned",
                   "epistemic_state": "supported", "falsifier": _FALSIFIER}],
    }
    reg = pa.hypothesis_register([], claims)
    assert len(reg["rows"]) == 1
    assert reg["rows"][0]["theses"] == ["001-a", "002-b"]
    assert reg["rows"][0]["disagreeing"] is False


def test_disagreeing_instantiations_stay_ONE_row_and_route_to_conflicts():
    """T119: disagreement does NOT create a second row. A second row would hide
    the disagreement by splintering it, and a new enum value would be Q76's
    collapse. One row carrying both verdicts, flagged, routed to the IC."""
    claims = {
        "001-a": [{"id": "C1", "entity": "NVDA", "state": "pinned",
                   "epistemic_state": "supported", "falsifier": _FALSIFIER}],
        "002-b": [{"id": "C2", "entity": "NVDA", "state": "pinned",
                   "epistemic_state": "refuted", "falsifier": _FALSIFIER}],
    }
    reg = pa.hypothesis_register([], claims)
    assert len(reg["rows"]) == 1
    assert reg["rows"][0]["disagreeing"] is True
    assert reg["conflicts"] and reg["conflicts"][0]["subject"] == "NVDA"


def test_a_different_metric_is_a_different_hypothesis():
    """Q89's reason the key is four fields and not one: keyed on the subject
    alone, "NVDA grows" and "NVDA margins hold" would fuse."""
    other = dict(_FALSIFIER, metric="revenue_growth")
    claims = {
        "001-a": [{"id": "C1", "entity": "NVDA", "state": "pinned",
                   "falsifier": _FALSIFIER}],
        "002-b": [{"id": "C2", "entity": "NVDA", "state": "pinned",
                   "falsifier": other}],
    }
    assert len(pa.hypothesis_register([], claims)["rows"]) == 2


def test_the_register_is_marked_derived_and_says_so():
    """Q4's fourth application. A persisted register would diverge from the
    theses that produced it, silently, exactly as a persisted portfolio file
    would."""
    text = pa.render_hypotheses(pa.hypothesis_register([], {}))
    assert "DERIVED, never stored" in text


# ── T120: refuted routes on the same path as a fired wrong_if ───────────────

def test_refuted_is_evaluated_into_the_wrong_if_finding_shape(tmp_path):
    """Q87's reason for one path: a refuted claim and a fired falsifier are the
    same event with different instrumentation. A second path would need its own
    finding-ID scheme and its own convergence section, and the two would diverge
    (Q12 rule 3)."""
    thesis = tmp_path / "001-x"
    thesis.mkdir()
    (thesis / "thesis.md").write_text(json.dumps({"judgment": {"claims": [
        {"id": "C1", "entity": "NVDA", "metric": "gross_margin",
         "period": "Q2-2026", "state": "pinned", "epistemic_state": "refuted"}]}}),
        encoding="utf-8")
    out = converge._evaluate_refuted(thesis)
    assert len(out) == 1
    ent, metric, fid = out[0]
    assert (ent, metric) == ("NVDA", "gross_margin")
    # the SAME id scheme as a fired wrong_if — that is what "one path" means
    assert fid == converge.finding_id("NVDA", "gross_margin", "Q2-2026", "invalidated")


def test_a_supported_claim_produces_no_refutation_finding(tmp_path):
    thesis = tmp_path / "001-x"
    thesis.mkdir()
    (thesis / "thesis.md").write_text(json.dumps({"judgment": {"claims": [
        {"id": "C1", "entity": "NVDA", "metric": "m", "state": "pinned",
         "epistemic_state": "supported"}]}}), encoding="utf-8")
    assert converge._evaluate_refuted(thesis) == []


def test_an_unevaluated_claim_produces_no_refutation_finding(tmp_path):
    """A claim created VACUOUS with no `epistemic_state` (T117) has not been
    evaluated, so nothing has refuted it. Absence must not read as refutation —
    the mirror of Q105's rule."""
    thesis = tmp_path / "001-x"
    thesis.mkdir()
    (thesis / "thesis.md").write_text(json.dumps({"judgment": {"claims": [
        {"id": "C1", "entity": "NVDA", "metric": "m", "state": "pinned",
         "mechanism_outcome": "VACUOUS"}]}}), encoding="utf-8")
    assert converge._evaluate_refuted(thesis) == []
