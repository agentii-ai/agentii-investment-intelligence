"""test_artifact_contract.py — spec 058 Phase 2 (US5): the artifact contract, enforced.

Phase 2's premise: the contract must declare every field a gate reads, and a gate that
cannot read its input must say so rather than report the field absent. Two defects
motivate it, both measured in the corpus:

  * `entity_claims` is read by five gates and absent from 128 artifacts, so every
    cross-run contradiction check in theses 001–003 was vacuous — and `build_entity_index`
    reported `contradictions: 0`, a number that was arithmetically forced, not earned.
  * A `\\$` where `` `$` `` was meant is an invalid YAML escape and silently destroyed a
    whole frontmatter block (`parsed keys: []`), which G1 then reported as **five missing
    pins** — sending a reader to add five fields to a document that already had all five.

The second one had already been FIXED: `describe_frontmatter_problems` was written to
report a format failure as a format failure. It had **no callers**. Writing a mechanism
is not wiring it, which is why these tests drive the reporting paths by name.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import g1_gate  # noqa: E402
import reduce_journals  # noqa: E402

# The observed defect verbatim: `\$` inside a double-quoted YAML scalar is not a valid
# escape, so the block does not parse. Every other field is present and correct.
DOLLAR_ESCAPE = (
    "---\n"
    "as_of: 2026-09-21\n"
    "constitution_pin: v1.2.0\n"
    "assumption_pin: q4-2026\n"
    "corpus_version: c-2026-09\n"
    "skill_pin: recent-quarter@abc123\n"
    "mode: methodology\n"
    "data_class: public\n"
    'note: "cost \\$5m in capex"\n'
    "---\n\n# Body\n"
)


def test_the_dollar_escape_really_does_break_the_block():
    """The fixture must reproduce the failure, or the tests below prove nothing."""
    assert g1_gate.has_frontmatter(DOLLAR_ESCAPE), "the block must START with `---`"
    assert g1_gate.parse_frontmatter(DOLLAR_ESCAPE) == {}, (
        "the escape no longer destroys the parse — the fixture has gone stale"
    )
    with pytest.raises(g1_gate.FrontmatterError):
        g1_gate.parse_frontmatter_strict(DOLLAR_ESCAPE)


def test_a_parse_failure_is_reported_as_a_format_failure_not_as_missing_pins():
    """T016/T017 / FR-038. The load-bearing assertion is the SECOND one.

    Reporting `frontmatter does not parse` is the easy half. The half that matters is
    that it does NOT also report pins: a document carrying all five, reported as missing
    all five, is a reader sent to fix the wrong thing.
    """
    problems = g1_gate.describe_frontmatter_problems(DOLLAR_ESCAPE, where="fixture.md")
    joined = " ".join(problems)
    assert "does not PARSE" in joined, f"the parse failure was not named:\n{joined}"
    assert "missing pin" not in joined, (
        f"a parse failure was ALSO reported as missing pins — the exact defect FR-038 "
        f"removes:\n{joined}"
    )


def test_the_artifact_entry_points_report_a_parse_failure(tmp_path):
    """The reporting paths must be WIRED, not merely correct.

    `describe_frontmatter_problems` existed with zero callers, so the fix for this defect
    was inert while looking complete. Both `check_artifact` and `check_artifact_full` are
    asserted by name because either could be unwired again.
    """
    art = tmp_path / "2026-09-21_1030_recent-quarter_methodology.md"
    art.write_text(DOLLAR_ESCAPE)

    short = g1_gate.check_artifact(art)
    assert any("does not PARSE" in p for p in short), (
        f"check_artifact did not report the parse failure:\n{short}"
    )
    assert not any("missing pin" in p for p in short), short

    full = g1_gate.check_artifact_full(art)
    assert any("does not PARSE" in p for p in full), (
        f"check_artifact_full did not report the parse failure:\n{full}"
    )
    assert not any("missing pin" in p for p in full), full

    pair = g1_gate.check_artifact_full(art, with_notices=True)
    assert isinstance(pair, tuple) and len(pair) == 2, (
        "check_artifact_full's with_notices=True shape changed — S1 callers unpack it"
    )


def test_a_well_formed_artifact_is_unaffected():
    """The fix must not become a false positive on the corpus's normal shape."""
    good = DOLLAR_ESCAPE.replace('note: "cost \\$5m in capex"', 'note: "cost $5m in capex"')
    assert g1_gate.parse_frontmatter_strict(good)["corpus_version"] == "c-2026-09"
    assert g1_gate.describe_frontmatter_problems(good, where="ok.md") == []


def test_parse_frontmatter_still_returns_empty_for_the_thirteen_presence_callers():
    """T016's constraint: the `{}` contract is kept, because thirteen call sites rely on it.

    `parse_frontmatter` answers a PRESENCE question and must keep answering `{}` for both
    "no block" and "malformed block". Widening it would silently change every caller.
    """
    assert g1_gate.parse_frontmatter(DOLLAR_ESCAPE) == {}
    assert g1_gate.parse_frontmatter("# no frontmatter here\n") == {}
    assert g1_gate.parse_frontmatter("---\n---\n") == {}


# ── T018/T019 — the contradiction index (FR-039) ──────────────────────────────

def _artifact(dirpath: Path, name: str, claims_yaml: str) -> Path:
    p = dirpath / name
    p.write_text("---\n" + claims_yaml + "---\n\n# Body\n")
    return p


def test_an_absent_entity_falls_back_to_ticker_and_never_becomes_None(tmp_path):
    """T018 / FR-039, driven by the corpus's own shape.

    Measured across 477 real claims: `ticker` is non-null in 477/477 and `entity` in
    425/477, so 52 claims carry no `entity`. They are NOT malformed — the artifacts say
    so themselves ("`entity: FLY  # mirrors ticker: g1_gate requires entity, the contract
    docs say ticker`") — so the index must fall back, not reject and not name them "None".
    """
    _artifact(tmp_path, "a.md",
              "entity_claims:\n"
              "  - {ticker: FLY, metric: revenue, value: 100, period: 2026Q2, retrieved_at: t1}\n")
    _artifact(tmp_path, "b.md",
              "entity_claims:\n"
              "  - {ticker: FLY, metric: revenue, value: 200, period: 2026Q2, retrieved_at: t1}\n")
    idx = reduce_journals.build_entity_index(tmp_path)
    assert len(idx["contradictions"]) == 1, idx["contradictions"]
    assert idx["contradictions"][0]["entity"] == "FLY", (
        f"ticker was not used as the entity: {idx['contradictions'][0]}"
    )
    assert "None" not in {c["entity"] for c in idx["contradictions"]}


def test_a_claim_with_neither_entity_nor_ticker_is_counted_not_named_None(tmp_path):
    """The genuinely malformed case: counted and reported, never filed under 'None'."""
    _artifact(tmp_path, "a.md",
              "entity_claims:\n"
              "  - {metric: revenue, value: 100, period: 2026Q2}\n")
    idx = reduce_journals.build_entity_index(tmp_path)
    assert idx["examined"]["claims_malformed"] == 1, idx["examined"]
    assert "None" not in {c["entity"] for c in idx["contradictions"]}
    assert idx["malformed"] and "no entity" in idx["malformed"][0]


def test_a_clean_zero_is_distinguishable_from_examining_nothing(tmp_path):
    """T019 / FR-039 — the whole point. Thesis 003 reported `contradictions: 0` on
    0 of 45 artifacts carrying `entity_claims`: a number that was arithmetically forced.

    Two cases, same `contradictions: []`, different `mechanism_outcome`.
    """
    empty = reduce_journals.build_entity_index(tmp_path)          # no artifacts at all
    assert empty["mechanism_outcome"] == "VACUOUS", empty["examined"]
    assert empty["examined"]["artifacts_with_claims"] == 0

    _artifact(tmp_path, "a.md",
              "entity_claims:\n"
              "  - {ticker: FLY, metric: revenue, value: 100, period: 2026Q2}\n")
    read = reduce_journals.build_entity_index(tmp_path)            # read one, found none
    assert read["mechanism_outcome"] == "EXECUTED", read["examined"]
    assert read["contradictions"] == [], "both cases have no contradictions…"
    assert read["examined"]["claims_scanned"] == 1, "…but only one examined a claim"


def test_a_qualitative_claim_is_skipped_not_crashed_on(tmp_path):
    """A `unit: text` claim carries a non-numeric value — 5 in the corpus.

    `float()` on it raised ValueError and crashed the entire index, which is how this
    was found: the first run against the real corpus died on
    `'integration_of_lunar_technology_stack'`. Legitimate claim, not comparable, so
    counted and skipped.
    """
    _artifact(tmp_path, "a.md",
              "entity_claims:\n"
              "  - {ticker: FLY, metric: integration_rationale, value: not_revenue,"
              " unit: text, period: 2026Q2}\n"
              "  - {ticker: FLY, metric: revenue, value: 100, period: 2026Q2}\n")
    idx = reduce_journals.build_entity_index(tmp_path)   # must not raise
    assert idx["examined"]["claims_scanned"] == 2, idx["examined"]
    assert idx["examined"]["claims_not_comparable"] == 1, idx["examined"]
    assert idx["not_comparable"], "the skipped claim must be reported, not dropped"


def test_an_unparseable_artifact_is_excluded_loudly_never_as_declaring_nothing(tmp_path):
    """T018/T019's blind spot, closed 2026-09-21 (`FR-038`).

    The auditor's fixture verbatim: one good artifact and one malformed by a `\\$` escape,
    the malformed one carrying **999** against the good one's **100** in the SAME
    (entity, metric, period). Before this fix:

        artifacts_scanned: 2 · claims_scanned: 1 · mechanism_outcome: EXECUTED
        contradictions: [] · malformed: [] · not_comparable: []

    A real contradiction, dropped, and nothing anywhere said an artifact had been skipped.
    `journal_frontmatter` used the lenient parser, where "does not parse" and "declares no
    claims" are the same `{}` — the conflation T016 removed from `g1_gate`, one call site
    away, in the function T016's own note named.
    """
    art = tmp_path / "artifacts"
    art.mkdir()
    _artifact(art, "good.md",
              "entity_claims:\n"
              "  - {ticker: FLY, metric: revenue, value: 100, period: 2026Q2, retrieved_at: t1}\n")
    (art / "broken.md").write_text(
        '---\nas_of: 2026-09-21\nnote: "cost \\$5m"\n'
        "entity_claims:\n"
        "  - {ticker: FLY, metric: revenue, value: 999, period: 2026Q2, retrieved_at: t1}\n"
        "---\n\n# broken\n")

    idx = reduce_journals.build_entity_index(art)
    assert idx["examined"]["artifacts_scanned"] == 2, idx["examined"]
    assert idx["examined"]["artifacts_unparseable"] == 1, (
        f"a malformed artifact was not counted as unparseable — it is being read as one "
        f"that declares nothing:\n{idx['examined']}")
    assert idx["unparseable"] and "does not parse" in idx["unparseable"][0], idx["unparseable"]
    assert "not read as" in idx["unparseable"][0].lower(), idx["unparseable"]

    # And the human-facing surface says it, before any count it would otherwise inflate.
    res = subprocess.run(
        [sys.executable, str(KIT / "scripts" / "challenge.py"), "--thesis", str(tmp_path)],
        capture_output=True, text=True, cwd=str(KIT))
    out = res.stdout + res.stderr
    assert "UNPARSEABLE" in out, f"challenge.py did not surface it:\n{out}"
    assert out.index("UNPARSEABLE") < out.index("contradictions:"), (
        "the exclusion is reported AFTER the count it invalidates, so a reader takes the "
        f"count first:\n{out}")


def test_the_aggregate_refuses_to_under_count_silently(tmp_path):
    """The same hole at the constitution floor.

    `check_aggregate` sums `position_pct` per sector against a declared max. A malformed
    artifact contributes no sector and no position — so it silently REMOVES exposure from
    a total that exists to bound exposure. That is worse than a missing report: it is a
    breach check reporting under the breach.
    """
    _artifact(tmp_path, "good.md", "sector: space\nposition_pct: 5\n")
    (tmp_path / "broken.md").write_text(
        '---\nsector: space\nposition_pct: 30\nnote: "cost \\$1m"\n---\n\n# broken\n')
    constitution = tmp_path / "constitution.yaml"
    constitution.write_text("constraints: []\n")

    problems = reduce_journals.check_aggregate(tmp_path, constitution)
    assert problems, "an artifact that does not parse passed the aggregate silently"
    assert any("does not parse" in p for p in problems), problems
    assert any("under-count" in p for p in problems), problems


def test_the_contract_surfaces_the_field_no_gate_consumes():
    """T020 / FR-040 — `upstream_stale` must not go quiet again.

    It is carried by all 41 SPACX artifacts, correct in all 41, and read by nothing.
    The kit cannot remove it (the workspace declares it) and cannot yet consume it (the
    value names a source thesis and version the kit has no registry for), so the one
    thing it can do is REPORT it — on every run, so the condition cannot be forgotten.
    """
    res = subprocess.run(
        [sys.executable, str(KIT / "scripts" / "check_gate_fields.py")],
        capture_output=True, text=True, cwd=str(KIT),
    )
    out = res.stdout + res.stderr
    assert "upstream_stale" in out, (
        "the field with no consumer is no longer reported anywhere — FR-040's condition "
        f"has gone invisible again (which is how it survived 41 artifacts):\n{out}"
    )
    assert "FR-040" in out, f"the notice does not cite the requirement it serves:\n{out}"
