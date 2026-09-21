"""test_output_quality.py — FR-002's six criteria, one negative fixture each (spec 058 T026).

T026 says *"a report carrying every element except one MUST fail on that one"*, and the
first test here is the control that makes that sentence mean something: a well-formed
artifact must PASS. Without it, a gate that failed everything would satisfy every other
assertion in this file.

Criterion 6's fixture is the one worth naming. It is **not** an absent key: all five pins
are present in 206 of 206 corpus artifacts, and the enforcement is `if not fm.get(pin)`
(`scripts/g1_gate.py:126`) — a truthiness test. A pin whose value means nothing therefore
passes today. So the fixture is a pin present with a **truthy placeholder**, which is the
state the criterion exists to catch, and its control is the same pin ABSENT (a different
message, so the two cannot be confused).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import check_output_quality as q  # noqa: E402

SKILL_MD = """# fixture — Output Structure fixture

## Output Structure

1. **Executive Summary** — headline conclusions (≤50 words).
2. **Analysis** — the core analysis section.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per
   `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY; the bottom
   **Citations** section is a non-duplicative roll-up index.

**Citations & memory**: ≥1 citation per 50 words; every material fact, table row, and
metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}`
link; the closing reply includes a compact Key Citations list.
"""

PINS = """as_of: 2026-09-20
constitution_pin: v1.2.0
assumption_pin: q4-2026
corpus_version: c-2026-09
skill_pin: fixture@abc123
"""

GOOD_BODY = """## Executive Summary

Headline [FACT] with its link https://agentii.ai/v/FLY/sec101/12 and a few words.

## Analysis

Revenue was $5.2bn [FACT] (https://agentii.ai/v/FLY/sec101/13).

## Data classification

Revenue is [FACT]; the trajectory is [DEDUCTED]; the stance is [VIEW].

## Coverage Gaps & Citations

- https://agentii.ai/v/FLY/sec101/12
- https://agentii.ai/v/FLY/sec101/13
"""


@pytest.fixture
def skill(tmp_path: Path) -> Path:
    d = tmp_path / "skills" / "fixture"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(SKILL_MD)
    return d


def _check(tmp_path: Path, skill: Path, body: str, pins: str = PINS) -> list[str]:
    art = tmp_path / "artifact.md"
    art.write_text(f"---\n{pins}citations:\n  - {{url: \"https://agentii.ai/v/FLY/sec101/12\"}}\n"
                   f"---\n\n{body}")
    problems, _ = q.check_artifact(art, q.criteria_for(skill))
    return problems


def test_the_criteria_are_derived_from_the_skill_not_invented(skill):
    """FR-002's rule. The budget and the density come out of the skill's own text, and the
    gate records whether each was DECLARED or is a fallback."""
    c = q.criteria_for(skill)
    assert c["exec_words"] == 50 and c["exec_words_declared"] is True, c
    assert c["citations_per_words"] == 50 and c["citations_declared"] is True, c
    assert c["elements"] == ["Executive Summary", "Analysis", "Data classification",
                             "Coverage Gaps & Citations"], c

    bare = skill.parent / "bare"
    bare.mkdir()
    (bare / "SKILL.md").write_text("## Output Structure\n\n1. **Only One** — x\n")
    cb = q.criteria_for(bare)
    assert cb["exec_words"] == 200 and cb["exec_words_declared"] is False, (
        "an undeclared budget fell back silently without saying so")


def test_a_wellformed_artifact_passes(tmp_path, skill):
    """THE CONTROL. Every other test here asserts a failure; this one asserts the gate can
    say yes, or the rest of the file proves nothing."""
    problems = _check(tmp_path, skill, GOOD_BODY)
    assert problems == [], f"the control artifact failed:\n" + "\n".join(problems)


# ── one fixture per criterion ───────────────────────────────────────────────

def test_criterion_1_the_executive_summary_over_budget_fails(tmp_path, skill):
    long = " ".join(["word"] * 60) + " https://agentii.ai/v/FLY/sec101/12"
    body = GOOD_BODY.replace("Headline [FACT] with its link https://agentii.ai/v/FLY/sec101/12 and a few words.",
                             long)
    problems = _check(tmp_path, skill, body)
    assert any("criterion 1" in p and "50" in p for p in problems), problems


def test_criterion_2_an_untagged_artifact_fails(tmp_path, skill):
    import re as _re
    body = _re.sub(r"\[(?:FACT|DEDUCTED|VIEW)\] ?", "", GOOD_BODY)
    assert "[FACT]" not in body and "[DEDUCTED]" not in body, "the fixture kept a badge"
    problems = _check(tmp_path, skill, body)
    assert any("criterion 2" in p for p in problems), problems


def test_criterion_3_too_few_citations_fails(tmp_path, skill):
    """300 words of prose: the declared rule (1 per 50) needs 6 citation urls and the
    artifact supplies 2. The first version of this fixture used 120 words and PASSED —
    because the roll-up's two urls count, so 2 was enough for 130 words. The threshold
    arithmetic was the fixture's error, not the rule's."""
    filler = " ".join(["sentence"] * 300)
    body = GOOD_BODY.replace("Revenue was $5.2bn", filler)
    problems = _check(tmp_path, skill, body)
    assert any("criterion 3" in p and "≥1 per 50" in p for p in problems), problems


def test_criterion_4_a_figure_without_its_inline_link_fails(tmp_path, skill):
    body = GOOD_BODY.replace("Revenue was $5.2bn [FACT] (https://agentii.ai/v/FLY/sec101/13).",
                             "Revenue was $5.2bn [FACT] and grew 12%.")
    problems = _check(tmp_path, skill, body)
    assert any("criterion 4" in p for p in problems), problems


def test_criterion_5_a_duplicated_rollup_fails(tmp_path, skill):
    body = GOOD_BODY + "- https://agentii.ai/v/FLY/sec101/12\n"
    problems = _check(tmp_path, skill, body)
    assert any("criterion 5" in p and "non-duplicative" in p.lower() for p in problems), problems


def test_criterion_5_a_missing_rollup_fails(tmp_path, skill):
    body = GOOD_BODY.split("## Coverage Gaps & Citations")[0]
    problems = _check(tmp_path, skill, body)
    assert any("criterion 5" in p for p in problems), problems


def test_criterion_6_a_truthy_placeholder_pin_fails(tmp_path, skill):
    """THE fixture that matters: the key is PRESENT, so a key test would pass it."""
    pins = PINS.replace("assumption_pin: q4-2026", 'assumption_pin: "[TBD]"')
    problems = _check(tmp_path, skill, GOOD_BODY, pins)
    assert any("criterion 6" in p and "assumption_pin" in p for p in problems), problems
    assert any("placeholder" in p for p in problems), problems


def test_criterion_6_an_absent_pin_fails_differently_from_a_placeholder(tmp_path, skill):
    """The control for the control: absent and placeholder must be distinguishable, or the
    fixture above proves only that *something* fired."""
    pins = PINS.replace("assumption_pin: q4-2026\n", "")
    absent = _check(tmp_path, skill, GOOD_BODY, pins)
    assert any("is absent" in p for p in absent), absent
    assert not any("placeholder" in p for p in absent), (
        f"an absent pin was reported as a placeholder:\n{absent}")


def test_a_declared_element_absent_from_the_artifact_fails(tmp_path, skill):
    """FR-002's core: the skill declared it, the artifact does not have it. This is the
    criterion that measures 0 of 206 on Executive Summary in the real corpus."""
    body = GOOD_BODY.replace("## Analysis", "## Something Else")
    problems = _check(tmp_path, skill, body)
    assert any("declared element absent" in p and "Analysis" in p for p in problems), problems


def test_an_element_named_with_a_qualifier_counts_as_present(tmp_path):
    """The heading match starts-with, so `Executive Summary (Q3 2026)` is the element —
    and it does NOT match a different element that merely starts the same way."""
    headings = {"executive summary q3 2026", "analysis", "coverage gaps citations"}
    assert q.element_present("Executive Summary", headings) is True
    assert q.element_present("Analysis", headings) is True
    assert q.element_present("Analysis of Growth", {"analysis of growth"}) is True
    assert q.element_present("Executive Summary", {"executive summaryx"}) is False, (
        "a heading that merely shares a prefix was accepted — the slack must be at a word "
        "boundary or `Business Model` would match `Business Model Type`")


def test_an_artifact_with_no_resolvable_skill_is_reported_not_scored(tmp_path):
    """FR-002: the criteria come from the skill. An artifact that cannot be matched to one
    is reported, never graded against a default — a default would be an invented rule."""
    art = tmp_path / "artifacts" / "UNKNOWN" / "2026-09-20_unknown_methodology.md"
    art.parent.mkdir(parents=True)
    art.write_text("---\nticker: FLY\n---\n\n## Whatever\n\nProse.\n")
    problems, examined = q.check_artifacts(tmp_path / "artifacts")
    assert examined["unmatched"] == 1, examined
    assert any("no skill could be resolved" in p for p in problems), problems
