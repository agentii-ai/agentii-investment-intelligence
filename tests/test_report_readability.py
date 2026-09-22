"""Fixtures for the blocking readability gate (spec 058 T087, FR-064).

ONE NEGATIVE FIXTURE PER BLOCKING CONVENTION, plus the control that matters more than any of them: a
well-formed report that clears all four. A gate with only negative fixtures is a gate nobody can tell
from `return ["problem"]` — it would fire on everything and look thorough while doing it.

Every fixture below is SYNTHETIC and about a fictional segment. That is not incidental: the contract is
derived from the Morgan Stanley corpus **methodology only** (`FR-063`), and a fixture lifted from a real
report is precisely the content ingestion the rule forbids.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_report_readability as rr  # noqa: E402

#: A page that clears every blocking convention. Its prose is deliberately unremarkable — the point is
#: the SHAPE (claim first, exhibit, reading of the exhibit, implication before the data ends).
GOOD_PAGE = """
<section class="page">
  <h2>Launch is the growth engine, and the mix is the number to watch</h2>
  <p>The launch segment now drives more of the group's growth than any other unit, which implies the
  mix shift matters more than the headline total.</p>
  <table><tr><th>Segment</th><th>Revenue</th></tr><tr><td>Launch</td><td>120</td></tr></table>
  <p>Read together, the two lines show the shift accelerating, so the multiple should follow the mix
  rather than the total.</p>
</section>
"""


def test_good_report_clears_every_blocking_convention():
    """The control. Without it, four negative fixtures prove only that the module can say 'no'."""
    assert rr.check(GOOD_PAGE) == []


def test_lede_before_evidence_fires_when_evidence_comes_first():
    """CONVENTION 1, negative fixture: the page opens with the exhibit."""
    bad = """
    <section class="page">
      <h2>Segment detail</h2>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>The table above sets out the segment split for the period under review.</p>
    </section>
    """
    problems = rr.check_lede_before_evidence(bad)
    assert problems, "an exhibit before any prose must be reported"
    assert "lede-before-evidence" in problems[0]


def test_lede_before_evidence_fires_on_a_label_lede():
    """CONVENTION 1, the subtler half: prose that is present but states no claim.

    This is the failure the corpus mining predicted would be hardest to catch and the one the old
    keyword proxy let through — a sentence that is grammatically a sentence and rhetorically a label.
    """
    bad = """
    <section class="page">
      <h2>Segment detail</h2>
      <p>Segment detail for the period.</p>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>The table above sets out the segment split for the period under review.</p>
    </section>
    """
    problems = rr.check_lede_before_evidence(bad)
    assert problems, "a topic-label opening is not a lede"


def test_exhibit_takeaway_fires_when_an_exhibit_has_no_reading():
    """CONVENTION 2, negative fixture: a table with nothing after it."""
    bad = """
    <section class="page">
      <h2>Launch is the growth engine</h2>
      <p>The launch segment drives more of the group's growth than any other unit.</p>
      <table><tr><td>Launch</td><td>120</td></tr></table>
    </section>
    """
    problems = rr.check_exhibit_takeaways(bad)
    assert problems, "an exhibit with no takeaway must be reported"
    assert "exhibit-takeaway" in problems[0]


def test_exhibit_takeaway_accepts_a_figcaption_that_is_a_sentence():
    """The false positive the check was written to avoid.

    A caption that states the reading IS the takeaway; flagging it would train authors to duplicate the
    sentence below the figure, which makes reports longer and no clearer.
    """
    ok = """
    <section class="page">
      <h2>Launch is the growth engine</h2>
      <p>The launch segment drives more of the group's growth than any other unit.</p>
      <figure><table><tr><td>Launch</td><td>120</td></tr></table>
        <figcaption>Launch revenue grew faster than every other segment, which is why the mix moved.</figcaption>
      </figure>
    </section>
    """
    assert rr.check_exhibit_takeaways(ok) == []


def test_numbers_only_paragraph_fires():
    """CONVENTION 3, negative fixture: the literal reported symptom."""
    bad = """
    <section class="page">
      <h2>Launch is the growth engine</h2>
      <p>The launch segment drives more of the group's growth than any other unit.</p>
      <p>120 | 84 | 12% | 3.4x | $4.1bn | 27%</p>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>Read together, the lines show the shift accelerating, so the multiple should follow the mix.</p>
    </section>
    """
    problems = rr.check_numbers_only_paragraphs(bad)
    assert problems, "a paragraph of figures must be reported"
    assert "numbers-only-paragraph" in problems[0]


def test_numbers_only_does_not_fire_on_a_sentence_with_numbers_in_it():
    """The other false positive: real prose is full of figures.

    A checker that flagged every numeric sentence would be disabled within a day, and the convention it
    was meant to protect would go with it.
    """
    ok = """
    <section class="page">
      <h2>Launch is the growth engine</h2>
      <p>Launch revenue grew 12% to $4.1bn, ahead of the 9% consensus, which implies the mix shift is
      running faster than the market assumes.</p>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>Read together, the lines show the shift accelerating, so the multiple should follow the mix.</p>
    </section>
    """
    assert rr.check_numbers_only_paragraphs(ok) == []


def test_conclusion_first_fires_when_the_implication_is_buried():
    """CONVENTION 4, negative fixture: a label heading, evidence, and the meaning last."""
    bad = """
    <section class="page">
      <h2>Segment detail</h2>
      <p>Segment detail for the period under review.</p>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>The table above sets out the split.</p>
      <p>This implies the mix shift is the number to watch.</p>
    </section>
    """
    problems = rr.check_conclusion_first(bad)
    assert problems, "a section that states its claim only at the end must be reported"
    assert "conclusion-first" in problems[0]


def test_conclusion_first_is_satisfied_by_a_claim_heading():
    """**The false positive that corrected this check, kept as a fixture.**

    The first version asked whether the first implication preceded the LAST exhibit, and it fired on
    page 2 of a real delivered report whose shape is: a claim heading, its exhibit, then a 104-word
    reading of it. That is a correct sell-side page — the heading carries the conclusion and the exhibit
    is followed by its takeaway, which is what convention 2 asks for.

    The corpus is what settled it: the shipped reports consistently use claim headings, so a check that
    ignores the heading measures the wrong thing. A gate that fires on a good report is a gate that gets
    switched off, and the convention it protects goes with it.
    """
    ok = """
    <section class="page">
      <h2>Launch cost has a hard floor</h2>
      <table><tr><td>Launch</td><td>120</td></tr></table>
      <p>Read together, the lines show the shift accelerating, so the multiple should follow the mix.</p>
    </section>
    """
    assert rr.check_conclusion_first(ok) == []


def test_conclusion_first_does_not_fire_on_a_page_with_no_exhibit():
    """The boundary: a page with no exhibit has no ordering to get wrong.

    A prose page states its claim wherever the prose is; this check is about evidence arriving before
    the argument.
    """
    page = """
    <section class="page">
      <h2>Segment detail</h2>
      <p>Segment detail for the period under review.</p>
    </section>
    """
    assert rr.check_conclusion_first(page) == []


def test_a_content_with_no_pages_is_reported_rather_than_passed():
    """The gate must not pass a document it could not read.

    This is the defect class the whole specification is about — a declared mechanism returning empty
    success. A checker whose subject is missing has found a problem, not an absence of one.
    """
    problems = rr.check("<html><body><p>no pages here</p></body></html>")
    assert problems, "content with no report pages must not clear the gate"
    assert "no report pages" in problems[0]


# ── the two corpus-derived checks (contracts/report-readability.md §3) ────────────────────────────


def _page(body: str) -> str:
    return f'<section class="page">{body}</section>'


def test_interpretive_floor_fires_when_figures_are_never_read():
    """CONVENTION 5, negative fixture: sentences that are all numbers, in bulk.

    The corpus floor is 0.25 — the observed minimum across every sampled document was 0.27 — and
    `check_interpretive_floor` needs at least ten numeric sentences before a ratio means anything, so
    the fixture is deliberately long enough to be measured at all.
    """
    numeric = " ".join(f"Segment {i} revenue was 120." for i in range(12))
    bad = _page(f"<h2>Launch is the growth engine</h2><p>{numeric}</p>"
                "<table><tr><td>x</td></tr></table><p>Read together they show the shift.</p>")
    problems = rr.check_interpretive_floor(bad)
    assert problems, "numeric sentences with no interpretation must be reported"
    assert "interpretive-floor" in problems[0]


def test_interpretive_floor_does_not_fire_below_the_minimum_sample():
    """The boundary that stops a short page from being judged on noise.

    A page with four numeric sentences has no ratio worth computing, and a check that fired on it would
    fail every short report for arithmetic rather than for prose.
    """
    short = _page("<h2>Launch is the growth engine</h2><p>Revenue was 1, 2, 3 and 4.</p>")
    assert rr.check_interpretive_floor(short) == []


def test_exhibit_monotonicity_fires_on_a_decreasing_sequence():
    """CONVENTION 6, negative fixture: exhibit numbers going backwards."""
    bad = _page(
        "<h2>Launch is the growth engine</h2>"
        "<p>Exhibit 4 sets out the split, which implies the mix moved.</p>"
        "<p>Exhibit 2 shows the same series earlier, so the direction is clear.</p>"
    )
    problems = rr.check_exhibit_monotonicity(bad)
    assert problems, "a decreasing exhibit sequence must be reported"
    assert "exhibit-monotonicity" in problems[0]


def test_exhibit_monotonicity_permits_gaps_and_a_non_unit_start():
    """Two tolerances the corpus forced, kept as a fixture because they are the tempting mistakes.

    Exhibit numbers legitimately skip, and Market_Share's headings are a subset of its numbered
    exhibits, so the sequence need not start at 1. An invariant of the form "1..N with no gaps" fails
    real documents — this asserts the looser rule the corpus actually supports.
    """
    ok = _page(
        "<h2>Launch is the growth engine</h2>"
        "<p>Exhibit 12 sets out the split, which implies the mix moved.</p>"
        "<p>Exhibit 27 shows the later series, so the direction is clear.</p>"
    )
    assert rr.check_exhibit_monotonicity(ok) == []


def test_exhibit_monotonicity_does_not_fire_on_a_single_exhibit():
    """One exhibit has no order to get wrong; the check is gated, not passed by luck."""
    ok = _page("<h2>Launch is the growth engine</h2><p>Exhibit 9 sets out the split, so the mix moved.</p>")
    assert rr.check_exhibit_monotonicity(ok) == []


def test_the_two_contested_conventions_are_reported_and_not_blocking():
    """**The split that the corpus derivation forced.**

    `FR-064` names exhibit-takeaway and conclusion-first as blocking. The corpus contradicts both —
    exhibit-takeaway holds in only 43-49% of the largest family's exhibit sections, and conclusion-first
    is contradicted by 77-80 of its 103-106 sections. So they are REPORTED and not obeyed, and this
    test is what stops a later change from quietly promoting them back into `CHECKS`.
    """
    blocking_names = {name for name, _ in rr.CHECKS}
    reported_names = {name for name, _ in rr.REPORTED_ONLY}

    assert "exhibit-takeaway" not in blocking_names
    assert "conclusion-first" not in blocking_names
    assert reported_names == {"exhibit-takeaway", "conclusion-first"}

    # And the page the two conventions flag is NOT blocked by the gate — the point of demoting them,
    # stated as an assertion rather than left to the reader. (This fixture does trip convention 1, whose
    # lede rule the corpus does support; that is a different finding and it is reported as such.)
    contested = _page(
        "<h2>Segment detail</h2>"
        "<p>Segment detail for the period under review.</p>"
        "<table><tr><td>Launch</td><td>120</td></tr></table>"
        "<p>This implies the mix shift is the number to watch.</p>"
    )
    assert rr.reported(contested), "the contested conventions still observe it"
    assert not any("exhibit-takeaway" in p or "conclusion-first" in p for p in rr.check(contested)), (
        "neither contested convention may appear in the blocking verdict")
