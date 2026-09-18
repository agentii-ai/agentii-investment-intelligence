"""S3 tests (T040/T042): price-stage refusal + allowlist consistency; dispatcher
remainder — compile-time preflight, retry policy by failure class, Q60 reuse
validation, Q13/Q54 routing declarations."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import dispatch  # noqa: E402
import g1_gate  # noqa: E402
import refusal  # noqa: E402


# --- T040: price-stage refusal -------------------------------------------------

def test_late_stage_price_history_refused():
    env = refusal.require_price_access("late", "get_price_history")
    assert env["status"] == "error"
    assert env["error"].startswith("PRICE_ACCESS_PREMATURE")


def test_late_stage_realtime_quote_allowed():
    assert refusal.require_price_access("late", "get_realtime_quote") is None


def test_early_stage_history_allowed():
    assert refusal.require_price_access("early", "get_price_history") is None


def test_allowlist_consistency_q45():
    # early MUST include get_price_history; late MUST include get_realtime_quote
    # and NOT get_price_history — illegal states are deterministic (Q45).
    assert g1_gate.check_market_data_allowlist("early", ["get_price_history"]) == []
    assert g1_gate.check_market_data_allowlist("early", ["get_realtime_quote"])
    assert g1_gate.check_market_data_allowlist("late", ["get_realtime_quote"]) == []
    assert g1_gate.check_market_data_allowlist("late",
                                               ["get_realtime_quote", "get_price_history"])
    assert g1_gate.check_market_data_allowlist("none", []) == []


# --- T042: dispatcher remainder -------------------------------------------------

def test_compile_time_preflight_fast_fails_naming_the_node():
    registry = {"business-model": {"requires": ["xbrl_coverage: fresh"]},
                "dcf": {"requires": ["business-model"]}}
    plan = [{"skill": "business-model", "requires": ["xbrl_coverage: fresh"]},
            {"skill": "dcf", "requires": ["business-model", "ghost-skill"]}]
    problems = dispatch.preflight(plan, registry)
    assert problems and any("dcf" in p and "ghost-skill" in p for p in problems)


def test_preflight_passes_when_all_requires_resolve():
    """Every node declares requires, and every one resolves.

    CHANGED 2026-09-18 (Q12/Q105). The fixture used to be
    `plan = [{"skill": "business-model"}, {"skill": "dcf", "requires": [...]}]`
    with `assert preflight(...) == []` — and the FIRST node had no `requires` at
    all. So the test asserted that examining nothing produces no problems, i.e.
    it froze the silent pass in place as the expected behaviour. Its own name
    said "when all requires resolve" while the node it was passing doesn't
    resolve, it doesn't exist.

    NOTE: the entries here are REGISTRY KEYS (skill names), because that is what
    the implementation checks (`if req not in registry`). Q12's spec shows
    `requires` as capability predicates instead — `xbrl_coverage: fresh`,
    `validate_calculation: pass` — which would EVERY ONE fail this check. That
    mismatch is real and recorded as a landing item; this test pins the current
    model rather than pretending the two agree."""
    registry = {"business-model": {"requires": ["dcf"]},
                "dcf": {"requires": ["business-model"]}}
    plan = [{"skill": "business-model", "requires": ["dcf"]},
            {"skill": "dcf", "requires": ["business-model"]}]
    assert dispatch.preflight(plan, registry) == []


def test_preflight_now_accepts_a_capability_predicate():
    """RETIRED 2026-09-18 (T153/T154). This test used to pin the mismatch, with
    the instruction: *"if this ever passes, the predicate model has been
    implemented — update Q12's landing item and delete this test."* It passes;
    this is that deletion, kept as a positive assertion so the regression cannot
    silently return.

    The old body asserted the OPPOSITE — that Q12's own example entry
    `xbrl_coverage: fresh` is rejected. Full coverage of the model is in
    tests/test_preflight_vacuous.py."""
    registry = {"dcf": {"requires": ["xbrl_coverage: fresh"]}}
    plan = [{"skill": "dcf"}]
    assert dispatch.preflight(plan, registry) == [], (
        "Q12's own example entry must be ACCEPTED. If this fails, the predicate "
        "model has regressed to checking registry keys for both kinds of entry.")


def test_preflight_reports_vacuous_when_requires_is_undecided():
    """Q105/T157: a gate that examined nothing must say so, not return `[]`.

    UPDATED 2026-09-18 (T157): the fixture was `{"requires": []}`, which is now
    a deliberate "no preconditions" and passes. VACUOUS belongs to the key being
    ABSENT. Full three-state coverage is in tests/test_preflight_vacuous.py."""
    registry = {"business-model": {}}                  # absent = undecided
    plan = [{"skill": "business-model"}]
    problems = dispatch.preflight(plan, registry)
    assert problems, "an undecided requires must not read as a clean pass"
    assert any(dispatch.VACUOUS in p for p in problems)
    assert any("business-model" in p for p in problems)


def test_preflight_reads_the_registry_as_well_as_the_node():
    """The old docstring claimed registry requires were checked; the code read
    only the node's. Both are checked now, and the message says which."""
    registry = {"business-model": {"requires": ["ghost-from-registry"]}}
    plan = [{"skill": "business-model"}]          # node declares none
    problems = dispatch.preflight(plan, registry)
    assert any("ghost-from-registry" in p and "registry" in p for p in problems)


def test_retry_policy_by_failure_class():
    # deterministic failures fast-fail (retry cannot change the result);
    # VALIDATOR_FAIL retries N≈2 WITH the failure report injected.
    retries, inject = dispatch.retry_policy("DATA_STALE")
    assert (retries, inject) == (0, False)
    retries, inject = dispatch.retry_policy("VALIDATOR_FAIL")
    assert (retries, inject) == (2, True)


def test_q60_reuse_validation(tmp_path):
    art = tmp_path / "art.md"
    art.write_text("""---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "x:y"
mode: default
data_class: slow
---

# body
""")
    current = {"assumption_pin": 1}
    # valid frontmatter + as_of inside the freshness window → reuse (skip)
    verdict = dispatch.reuse_verdict(art, freshness_window_days=7,
                                     current_pins=current, now="2026-09-10")
    assert verdict == "reuse"
    # as_of outside the window → force re-run
    verdict = dispatch.reuse_verdict(art, freshness_window_days=7,
                                     current_pins=current, now="2026-10-01")
    assert verdict == "force_rerun"
    # corrupted frontmatter → force re-run
    art.write_text("garbage without frontmatter")
    assert dispatch.reuse_verdict(art, 7, current, "2026-09-10") == "force_rerun"
