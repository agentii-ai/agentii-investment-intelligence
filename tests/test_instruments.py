"""test_instruments.py — T159–T162 (Q140/Q81/Q83). Instrument detection.

Q140's finding, stated once: **`agentii.md` is a chronicle or a constitution, and
which one depends on whether `constitution.md` exists.** Q81's rotation and Q83's
prohibition both assumed it was always the former. Where it is the latter, the
rotation **rotates away the project's principles** — this spec's seventh instance
of one recurring defect, and the first that executes a destructive action rather
than returning an empty success.

The predicate is WORKSPACE-scoped, read from the filesystem, with no new state.
Q143: it is NOT the mode predicate, which is run-scoped. The two are orthogonal
and 046 briefly declared them one — see tests/test_meta_rules.py, Check 44's
sibling assertions on MR-3.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentii_cmd  # noqa: E402
import reconcile_instruments as ri  # noqa: E402

WORKSPACE = "/Users/frank/B"
LIVE = {"SPCX": Path(WORKSPACE) / "agentii-space-tech-SPCX",
        "physical-ai": Path(WORKSPACE) / "agentii-physical-ai"}


# ── T159: the detector ──────────────────────────────────────────────────────

def test_constitution_present_means_it_governs(tmp_path):
    (tmp_path / "constitution.md").write_text("ratified\n", encoding="utf-8")
    (tmp_path / "agentii.md").write_text("# Memory Index\n", encoding="utf-8")
    kind, why = agentii_cmd.detect_instrument(tmp_path)
    assert kind == agentii_cmd.INSTRUMENT_CONSTITUTION
    assert "chronicle" in why


def test_agentii_md_alone_IS_the_constitution(tmp_path):
    """The case Q81's rotation would destroy."""
    (tmp_path / "agentii.md").write_text("# Principles\n\nP1 — no leverage.\n",
                                         encoding="utf-8")
    kind, why = agentii_cmd.detect_instrument(tmp_path)
    assert kind == agentii_cmd.INSTRUMENT_AGENTII_MD
    assert "IS the constitution" in why
    assert "do NOT apply" in why


def test_neither_instrument_is_its_own_case(tmp_path):
    """Three states, not two. 'No constitution.md' is not the same as
    'no instrument' — that equivalence is the false binary Q140 removed."""
    kind, why = agentii_cmd.detect_instrument(tmp_path)
    assert kind == agentii_cmd.INSTRUMENT_NONE
    assert "neither" in why


def test_ratification_reads_whichever_file_governs(tmp_path):
    """The test is the same either way — an unreplaced `[WORKSPACE_NAME]` means
    the human has not filled in the real values — but WHICH file carries it
    depends on which instrument governs."""
    (tmp_path / "agentii.md").write_text("# P\n\n[WORKSPACE_NAME] rules apply.\n",
                                         encoding="utf-8")
    assert agentii_cmd.constitution_ratified(tmp_path) is False
    (tmp_path / "agentii.md").write_text("# P\n\nNo placeholders.\n", encoding="utf-8")
    assert agentii_cmd.constitution_ratified(tmp_path) is True
    # …and the constitution wins when both exist
    (tmp_path / "constitution.md").write_text("[WORKSPACE_NAME]\n", encoding="utf-8")
    assert agentii_cmd.constitution_ratified(tmp_path) is False


def test_no_instrument_is_never_ratified(tmp_path):
    assert agentii_cmd.constitution_ratified(tmp_path) is False


# ── T161: the refusal names which instrument is missing ─────────────────────

def test_specify_refuses_only_the_neither_case(tmp_path):
    with pytest.raises(SystemExit) as e:
        agentii_cmd.specify(tmp_path, "x")
    msg = str(e.value)
    assert "no constitutional instrument" in msg
    assert "constitution.md" in msg and "agentii.md" in msg


def test_specify_accepts_a_ratified_agentii_md(tmp_path):
    """The false binary's cost: this workspace was REFUSED before T161, even
    though `agentii.md` IS its constitution — and 52 skill files reference that
    instrument, so this is not a marginal configuration."""
    (tmp_path / "agentii.md").write_text("# Principles\n\nP1 — no leverage.\n",
                                         encoding="utf-8")
    thesis = agentii_cmd.specify(tmp_path, "demo")
    assert thesis.is_dir()


def test_specify_names_the_unratified_file(tmp_path):
    (tmp_path / "agentii.md").write_text("# P\n\n[WORKSPACE_NAME]\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        agentii_cmd.specify(tmp_path, "x")
    assert "agentii.md" in str(e.value)
    assert "UNRATIFIED" in str(e.value)


# ── T162: the reconciler ────────────────────────────────────────────────────

def test_reconciler_flags_a_principles_bearing_agentii_md_as_unsafe_to_rotate(tmp_path):
    (tmp_path / "agentii.md").write_text("# Principles\n\nP1 — no leverage.\n",
                                         encoding="utf-8")
    out = ri.survey(tmp_path)
    assert out["instrument"] == "agentii-md"
    assert out["rotation_safe"] is False
    assert "unrecoverable" in out["verdict"]


def test_reconciler_reports_principles_lost_in_a_migration(tmp_path):
    """The only item that catches a workspace ALREADY migrated onto the wrong
    path. A drop nobody decided is the failure; only a diff makes it visible."""
    (tmp_path / "agentii.md").write_text(
        "# Project Principles\n\n"
        "## P1 — Concentration\n\nNo single position MUST exceed 8%.\n\n"
        "## P2 — Leverage\n\nLeverage is FORBIDDEN.\n", encoding="utf-8")
    # a migration that silently dropped P2
    (tmp_path / "constitution.md").write_text(
        "# Constitution\n\n## P1 — Concentration\n\nNo single position MUST exceed 8%.\n",
        encoding="utf-8")
    out = ri.survey(tmp_path)
    lost = out["reconcile"]["lost"]
    assert any("Leverage" in x for x in lost), lost
    assert not any("Concentration" in x for x in lost), "P1 survived and must not be reported"


def test_reconciler_extracts_normative_lines_not_every_line():
    text = ("# Title\n\nJust prose about the project.\n\n"
            "Positions MUST NOT exceed 8% of capital.\n")
    ps = ri.extract_principles(text)
    assert any("MUST NOT" in p for p in ps)
    assert not any("Just prose" in p for p in ps)


# ── the live workspaces, asserted against reality ───────────────────────────

@pytest.mark.parametrize("name", sorted(LIVE))
def test_live_workspaces_are_on_the_safe_path(name):
    """MEASURED, not assumed. Both live workspaces carry `constitution.md` and no
    `agentii.md`, so neither exercises the single-skill branch — which is exactly
    why Q141/Q143's defects were invisible until someone read the documents
    against each other rather than against a run."""
    ws = LIVE[name]
    if not ws.is_dir():
        pytest.skip(f"{ws} not present on this machine")
    out = ri.survey(ws)
    assert out["instrument"] == "constitution", out
    assert out["rotation_safe"] is True
    assert not (ws / "agentii.md").is_file(), (
        "if this now exists, the instrument picture changed and Q141's measured "
        "claim about these workspaces needs re-deriving")


# ── T108b: Q67 drift-trigger coverage ───────────────────────────────────────

def test_scaffold_ships_every_canonical_trigger_pair():
    """The scaffold under-specified — it shipped ONE trigger and no `basis` — and
    two workspaces then improvised two different subsets. A scaffold that ships
    the full canonical set is what stops the next workspace improvising."""
    import yaml
    tmpl = yaml.safe_load(
        (ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
         / "constitution-template.yaml").read_text(encoding="utf-8"))
    triggers = (tmpl.get("regime") or {}).get("drift_triggers") or []
    covers = {t.get("covers") for t in triggers}
    assert covers >= set(agentii_cmd.CANONICAL_TRIGGER_COVERS), (
        f"the scaffold must carry every canonical pair; it carries {covers}")
    for t in triggers:
        assert t.get("basis"), f"trigger {t.get('indicator')!r} ships without `basis`"
        assert t.get("covers"), f"trigger {t.get('indicator')!r} ships without `covers`"


def test_coverage_reports_a_workspace_with_no_triggers(tmp_path):
    c = agentii_cmd.drift_trigger_coverage(tmp_path)
    assert set(c["missing"]) == set(agentii_cmd.CANONICAL_TRIGGER_COVERS)


def test_coverage_counts_declared_pairs_and_flags_missing_basis(tmp_path):
    (tmp_path / "constitution.yaml").write_text(
        "regime:\n"
        "  drift_triggers:\n"
        "    - indicator: ISM Manufacturing PMI\n"
        "      covers: regime\n"
        "      basis: '54.6 at ratification'\n"
        "    - indicator: US 10Y Treasury yield\n"
        "      covers: net_long\n"
        "      condition: 10Y > 5.25%\n",
        encoding="utf-8")
    c = agentii_cmd.drift_trigger_coverage(tmp_path)
    assert "regime" in c["covers"] and "net_long" in c["covers"]
    assert c["missing"] == ["sector_bias overweight"]
    assert c["no_basis"] == ["US 10Y Treasury yield"]


@pytest.mark.parametrize("name", sorted(LIVE))
def test_live_workspace_drift_coverage_is_reported(name):
    """MEASURED, and this is the finding T108b records: neither live workspace
    covers the yield-curve or credit-spread pairs, because `covers` did not exist
    to declare. T107 is the migration and it is user-facing."""
    ws = LIVE[name]
    if not ws.is_dir():
        pytest.skip(f"{ws} not present on this machine")
    c = agentii_cmd.drift_trigger_coverage(ws)
    assert c["declared"], "the workspace declares triggers"
    assert c["missing"], (
        "if this is now empty, T107's migration has run and this test should "
        "become an assertion that coverage is complete")


# ── T108: the scaffold gates (Q108/Q112/Q120/Q123) ──────────────────────────

def test_fresh_scaffold_is_correctly_unratifiable():
    """Q108: `[WORKSPACE_NAME]` gone is not authorship. A fresh scaffold has 26
    unfilled placeholders and must not ratify — the previous check tested ONE
    ALL-CAPS token, so `[sector focus]` survived ratification."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        agentii_cmd.constitution_scaffold(ws)
        assert agentii_cmd.constitution_ratified(ws) is False
        assert len(agentii_cmd.scaffold_problems(ws)) > 10


def test_lowercase_placeholder_blocks_ratification(tmp_path):
    """The specific cost of the case-sensitive check: a lowercase placeholder is
    exactly what a human types when filling one in partially."""
    (tmp_path / "constitution.md").write_text(
        "# C\n\n[sector focus] applies to the book.\n", encoding="utf-8")
    codes = [c for c, _ in agentii_cmd.scaffold_problems(tmp_path)]
    assert "ASSUMPTION_UNPINNED" in codes


def test_documentation_about_the_syntax_does_not_block(tmp_path):
    """Two exclusions, both found by this gate refusing to ratify a scaffold it
    had just produced — i.e. firing on the template rather than on the author:
      * backticks — the scaffold says *"replace every `[ALL_CAPS]`"*
      * HTML comments — the SIR template is spelled out for a FUTURE amendment
    A gate that can never pass is a gate that gets disabled."""
    (tmp_path / "constitution.md").write_text(
        "# C\n\n<!-- Sync Impact Report: version: [OLD_VERSION] -> [NEW_VERSION] -->\n"
        "Replace every `[ALL_CAPS]` token.\n", encoding="utf-8")
    assert [c for c, _ in agentii_cmd.scaffold_problems(tmp_path)
            if c == "ASSUMPTION_UNPINNED"] == []


def test_a_principle_named_but_not_registered_is_unframed(tmp_path):
    """Q123, from F2's audit: the Sync Impact Report named a principle by one name
    while the body called it another — 'drift hazard in a machine-read field'.
    A machine-read field may only name an identifier that EXISTS."""
    (tmp_path / "constitution.md").write_text(
        "# C\n\nP1 governs. P9 does not exist.\n", encoding="utf-8")
    (tmp_path / "constitution.yaml").write_text(
        "principles:\n  - id: P1\n  - id: P2\n", encoding="utf-8")
    problems = agentii_cmd.scaffold_problems(tmp_path)
    codes = {c for c, _ in problems}
    assert "UNFRAMED_REFERENCE" in codes
    assert any("P9" in d for _, d in problems)


def test_a_template_shaped_value_checks_is_reported(tmp_path):
    """Q112: `value-checks.yaml` carrying only template rules is indistinguishable
    from a real one unless the placeholders are checked."""
    (tmp_path / "constitution.md").write_text("# C\n\nP1 governs.\n", encoding="utf-8")
    (tmp_path / "value-checks.yaml").write_text(
        "rules:\n  - when: [CONDITION]\n    then: [ACTION]\n", encoding="utf-8")
    codes = {c for c, _ in agentii_cmd.scaffold_problems(tmp_path)}
    assert "SCHEMA_MISMATCH" in codes
