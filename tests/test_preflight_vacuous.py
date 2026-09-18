"""test_preflight_vacuous.py — T158 (Q12/Q105). The `requires:` preflight, pinned.

Q12 defines `requires:` at two levels, checked at two times (spec.md:504-516):

    data side   freshness / calc validation / assumption pin  → compile time
    edge side   predecessor output schema / completion marker → on the edge

`preflight()` implemented ONE check (`if req not in registry`) and applied it to
entries of BOTH kinds. So it was wrong in both directions — inert while empty,
and it would reject every spec-conformant entry once populated. Both directions
are pinned below, because a test that only covers the first would have called the
old code fixed the moment VACUOUS landed.

The gate is **compile-time resolution**, not satisfaction: whether
`xbrl_coverage: fresh` actually holds is answered at run time by the named
producer. The one satisfaction-adjacent thing that IS decidable here — an entry
naming a value the contract says can never satisfy — is checked, and pinned.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dispatch  # noqa: E402


# --- Q12's own example, which the old check rejected in full ---------------

def test_q12_own_example_entries_are_accepted():
    """THE regression. spec.md:71-79 gives these four entries as the canonical
    form. The old `if req not in registry` rejected every one of them, because
    none is a registry key — so the moment anyone populated `requires:` with the
    spec's own example, the gate would have failed the whole scenario."""
    registry = {"dcf": {"requires": [
        "xbrl_coverage: fresh",
        "validate_calculation: pass",
        "assumptions_pinned: true",
        "citations_min: 3",
    ]}}
    assert dispatch.preflight([{"skill": "dcf"}], registry) == []


# --- T158's three-way behaviour -------------------------------------------

def test_undecided_requires_is_vacuous_not_clean():
    """Q105: a gate that examined nothing must say so, not return `[]`.

    UPDATED 2026-09-18 (T157). This test used to pass `{"requires": []}` and
    demand VACUOUS. That encoded the collapse the fix removes: an empty list is
    now a *decision* (there are no preconditions) and passes; VACUOUS belongs to
    the field being ABSENT, which is the absence of a decision. The old fixture
    could not tell those apart — which was the defect."""
    registry = {"business-model": {}}                  # key absent = undecided
    problems = dispatch.preflight([{"skill": "business-model"}], registry)
    assert problems, "an undecided requires must not read as a clean pass"
    assert any(dispatch.VACUOUS in p for p in problems)
    assert any("business-model" in p for p in problems)


def test_declared_empty_is_a_decision_and_passes():
    """The other half of T157. `requires: []` says "I examined this and there
    are no preconditions" — a leaf skill is entitled to say that, and it must
    not be nagged forever for having decided."""
    registry = {"business-model": {"requires": []}}
    assert dispatch.preflight([{"skill": "business-model"}], registry) == []
    # ...and the node may declare it too, for a skill whose registry is undecided.
    registry = {"business-model": {}}
    plan = [{"skill": "business-model", "requires": []}]
    assert dispatch.preflight(plan, registry) == []


def test_unresolvable_skill_reference_fails_naming_the_source():
    registry = {"dcf": {"requires": ["ghost-skill"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert any("ghost-skill" in p and "registry" in p for p in problems)


def test_all_resolve_is_clean():
    registry = {"business-model": {"requires": ["dcf"]},
                "dcf": {"requires": ["business-model"]}}
    plan = [{"skill": "business-model", "requires": ["dcf"]},
            {"skill": "dcf", "requires": ["business-model"]}]
    assert dispatch.preflight(plan, registry) == []


# --- the four ways a predicate entry can be wrong -------------------------

def test_unknown_predicate_is_reported_as_unknowable():
    registry = {"dcf": {"requires": ["typo_predicate: 1"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert any("typo_predicate" in p and "not in contracts/requires-predicates" in p
               for p in problems)


def test_value_outside_the_enum_names_the_producer():
    registry = {"dcf": {"requires": ["xbrl_coverage: moldy"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert any("moldy" in p and "get_ticker_coverage" in p for p in problems)


def test_integer_predicate_rejects_a_non_integer():
    registry = {"dcf": {"requires": ["citations_min: many"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert any("citations_min" in p and "integer" in p for p in problems)


def test_a_value_that_can_never_satisfy_is_reported():
    """`validate_calculation: warn` parses, type-checks AND is in the enum, yet
    the contract's `satisfied_by` says only `pass` is met. The first version of
    check_predicate accepted it, so a self-defeating entry read as admissible.
    `stale` is the same shape for xbrl_coverage: DATA_STALE, not a pass."""
    registry = {"dcf": {"requires": ["validate_calculation: warn",
                                     "xbrl_coverage: stale"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert any("validate_calculation" in p and "never be satisfied" in p for p in problems)
    assert any("xbrl_coverage" in p and "never be satisfied" in p for p in problems)


# --- the vocabulary itself -------------------------------------------------

def test_vocabulary_contract_loads_and_matches_q12():
    vocab = dispatch.predicates()
    assert set(vocab) == {"xbrl_coverage", "validate_calculation",
                          "assumptions_pinned", "citations_min"}, (
        "the vocabulary is CLOSED and comes from Q12's own example — a change "
        "here is an enum extension and needs a producer, not just a list entry")
    for name, spec in vocab.items():
        assert spec.get("producer"), f"{name} names no producer — Q105"


def test_missing_vocabulary_is_reported_not_silently_passed():
    """A predicate check with no contract cannot evaluate anything. It must say
    so rather than let every predicate through as unknown-but-harmless."""
    registry = {"dcf": {"requires": ["xbrl_coverage: fresh"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry, vocab={})
    assert any("NO VOCABULARY" in p for p in problems)


def test_vacuous_is_not_raised_when_requires_live_on_the_registry_entry():
    """A node may declare none while its registry entry declares some — that is
    Q12's normal case (`requires` belongs to the skill's contract, not to the
    plan's scheduling). VACUOUS must not fire there."""
    registry = {"dcf": {"requires": ["xbrl_coverage: fresh"]}}
    problems = dispatch.preflight([{"skill": "dcf"}], registry)
    assert not any(dispatch.VACUOUS in p for p in problems)


@pytest.mark.parametrize("entry,why", [
    ("business-model", "bare token = process-side skill reference"),
    ("xbrl_coverage: fresh", "name: value = data-side capability predicate"),
])
def test_the_syntax_is_what_distinguishes_the_two_kinds(entry, why):
    """Q12's placement rule. If you cannot tell which side an entry is on, the
    entry is wrong — which is MR-1's sentence applied to `requires:`."""
    assert (dispatch.PREDICATE_RX.match(entry) is not None) == (": " in entry), why
