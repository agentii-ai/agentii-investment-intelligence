"""The single-skill output lint, registered so it actually runs (spec 062 FR-034 iii, T082).

WHY A REGISTERED TEST AND NOT A SCRIPT. `FR-031` (i) is explicit: a red case *"described in prose but not
in a registered suite does not satisfy this"*. The lint is the instrument; this file is what makes it part
of the build rather than a tool someone remembers to run.

THE THREE CASES THAT COULD NOT COME FROM THE LINT ITSELF, and why they are here:

  · **Both citation forms are counted.** The corpus carries **2,244** bare `/{N}` tails and **948**
    `page{N}` tails. The lint's first version accepted only the bare form, so it read every `page{N}`
    citation as absent: 21 artifacts failed the density rule and 46 failed the proximity rule, against a
    corpus whose real floor is 3.2. A test that pins both forms is what keeps that from returning — and
    it is the *smallest* possible fixture, so it can say exactly what broke.
  · **A roll-up is a list item that BEGINS with the link.** The first structural detector flagged any
    three consecutive lines containing links and reported **all 50** artifacts — consecutive prose lines
    that each carry an inline link are what the standard wants. The fixture below is the difference.
  · **The derived / gap / methodology classes are exempt.** The first R4 flagged `[DEDUCTED]` sentences,
    "No X disclosure" coverage gaps, and "Structured verification:" notes. Those have no page to cite.

The real-artifact case is `skipif`-guarded: it reads the held-out workspace, which is outside both
repositories and absent in CI. It is skipped, never passed — a gate that reports success because its input
is missing is the defect this specification is named after.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_output as co  # noqa: E402

#: The held-out workspace's artifacts — outside both repositories, so guarded rather than required.
HELD_OUT = pathlib.Path("/Users/frank/B/agentii-physical-ai/theses")
RED_CASE = HELD_OUT / "003-actuation-motion-chokepoint/artifacts/PH/2026-09-17_1647_supply-chain_default.md"

FM = "---\nas_of: 2026-09-01\nconstitution_pin: '1.3.0'\nassumption_pin: 1\ncorpus_version: x\nskill_pin: abc\n---\n"


def _write(tmp_path, body: str, fm: str = FM) -> pathlib.Path:
    p = tmp_path / "artifact.md"
    p.write_text(fm + body, encoding="utf-8")
    return p


def test_both_citation_forms_are_counted(tmp_path):
    """The regression that cost a 7× wrong headline: `/{N}` and `/page{N}` are both real citations."""
    body = (
        "## Analysis\n"
        "Revenue reached $1.2B in FY2025 https://agentii.ai/v/AMZN/sec131/23 and margin held at 42.0%.\n"
        "Gross margin was 42.0% on the same page https://agentii.ai/v/ISRG/sec166/page77 per the filing.\n"
        "Cash capex was $77.7B https://agentii.ai/v/AMZN/sec177/page41 against $55.6B prior.\n"
    )
    r = co.check(_write(tmp_path, body))
    assert r["links"] == 3, f"both forms must count; got {r['links']} — {r}"
    assert not [f for f in r["findings"] if f["rule"] == "R2-density"], r


def test_a_bare_fact_with_no_link_beside_it_fires(tmp_path):
    """R4: a material fact must carry its citation beside it. No link within one line either way."""
    body = (
        "## Analysis\n"
        "Revenue reached $1.2B in FY2025, up 18.0% year over year on volume.\n"
        "The segment margin expanded to 42.0% while the peer set averaged 31.0%.\n"
    )
    r = co.check(_write(tmp_path, body))
    rules = [f["rule"] for f in r["findings"]]
    assert "R4-bare-fact" in rules, r
    assert "R2-density" in rules, "2 lines, 0 links, floor 1 per 200 words — density must fire too"


def test_a_rollup_is_a_list_item_that_begins_with_the_link(tmp_path):
    """R3: the shape the standard rejects. Note the PROSE lines above it carry links and do not fire."""
    body = (
        "## Analysis\n"
        "Revenue reached $1.2B https://agentii.ai/v/AMZN/sec131/23 in FY2025.\n"
        "Margin held at 42.0% https://agentii.ai/v/AMZN/sec131/25 against a 31.0% peer average.\n"
        "Capex was $77.7B https://agentii.ai/v/AMZN/sec177/41, funded from operations.\n"
        "\n## Coverage Gaps & Citations\n"
        "1. https://agentii.ai/v/AMZN/sec131/23 — revenue and the FY2025 comparison\n"
        "2. https://agentii.ai/v/AMZN/sec131/25 — margin and the peer set\n"
        "3. https://agentii.ai/v/AMZN/sec177/41 — capex and its funding\n"
    )
    r = co.check(_write(tmp_path, body))
    rules = [f["rule"] for f in r["findings"]]
    assert "R3-rollup" in rules, r
    # And the prose above it is NOT a finding: that is the whole distinction this rule turns on.
    assert not [f for f in r["findings"] if f["rule"] == "R4-bare-fact"], r


def test_derived_gap_and_methodology_lines_are_exempt(tmp_path):
    """Three classes with no page to cite. The first R4 flagged all three on real artifacts."""
    body = (
        "## Analysis\n"
        "[DEDUCTED] The guidance implies a >100% one-year growth rate over the 2025 base.\n"
        "1. **No BOM or per-system cost stack.** The issuer discloses product margin only, at 66.3%.\n"
        "Structured verification: us-gaap:Revenues FY2025 returned 141.0M of contract revenue.\n"
    )
    r = co.check(_write(tmp_path, body))
    # R2 legitimately fires: three lines with no links is below any density floor. The claim here is
    # narrower and is the one that matters — the three EXEMPT classes do not fire R4.
    assert not [f for f in r["findings"] if f["rule"] == "R4-bare-fact"], r


@pytest.mark.skipif(not RED_CASE.is_file(),
                    reason="the held-out workspace is outside both repositories and absent in CI")
def test_the_real_pre_change_artifact_goes_red():
    """T082's red case: a PRODUCED artifact, not a synthetic one.

    `003-actuation-motion-chokepoint/artifacts/PH/2026-09-17_1647_supply-chain_default.md` cites nothing
    inline in 1,756 words. A synthetic file proves the lint can parse; this proves it catches something.
    """
    r = co.check(RED_CASE)
    rules = {f["rule"] for f in r["findings"]}
    assert {"R2-density", "R4-bare-fact"} <= rules, r
    assert r["density_per_200w"] == 0.0
    assert co.main([str(RED_CASE), "--strict"]) == 1, "--strict must gate on the red case"
