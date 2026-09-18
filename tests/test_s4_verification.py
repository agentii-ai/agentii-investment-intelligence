"""T065 — S4 verification: the spec-mandated negative/positive battery for the
command surface (Q27/Q31/Q13/Q80/Q83/Q42)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentii_cmd  # noqa: E402
import alloc_thesis_id  # noqa: E402
import resolve_template  # noqa: E402
import validate_scenes  # noqa: E402
import g1_gate  # noqa: E402
import dispatch  # noqa: E402


def _ratify(ws, name="Test Fund"):
    """Scaffold a workspace and FILL IT IN, the way a human ratifying would.

    REPLACES `(ws/"constitution.md").read_text().replace("[WORKSPACE_NAME]", ...)`
    as of 2026-09-18 (T108/Q108). That one-line substitution was enough while
    ratification checked a single ALL-CAPS token; Q108 made it check EVERY
    bracketed placeholder case-insensitively, because `[sector focus]` surviving
    ratification is the same defect as `[WORKSPACE_NAME]` surviving it. A fresh
    scaffold now reports 26 unfilled placeholders — correctly — so a fixture that
    wants a ratified workspace must author one.

    Comments and code spans are left alone: they are documentation ABOUT the
    syntax, and the scaffold's own instruction line says `[ALL_CAPS]` in backticks."""
    import re as _re
    import agentii_cmd as _ac
    _ac.constitution_scaffold(ws)
    p = ws / "constitution.md"
    t = p.read_text(encoding="utf-8")
    t = _re.sub(r"<!--.*?-->", lambda m: m.group(0), t, flags=_re.S)
    # fill every placeholder that is NOT inside an HTML comment or a code span
    def fill(segment):
        return _re.sub(r"\[[A-Za-z][A-Za-z0-9_ -]{2,40}\]",
                       lambda m: name if "WORKSPACE" in m.group(0) else "authored", segment)
    parts = _re.split(r"(<!--.*?-->|`[^`\n]*`)", t, flags=_re.S)
    out = []
    for i, seg in enumerate(parts):
        out.append(seg if i % 2 else fill(seg))
    p.write_text("".join(out), encoding="utf-8")
    return ws


def test_concurrent_specify_gets_distinct_ids(tmp_path):
    ws = tmp_path / "workspace"
    _ratify(ws, "Fund X")
    a = agentii_cmd.specify(ws, "mvp")
    b = agentii_cmd.specify(ws, "mvp")
    assert a.name != b.name and a.is_dir() and b.is_dir()


def test_biotech_preset_wrap_resolves_over_core(tmp_path):
    t = tmp_path / "templates"
    (t / "presets" / "biotech").mkdir(parents=True)
    (t / "presets" / ".registry").write_text(yaml.dump(["biotech"]))
    (t / "plan-template.md").write_text("CORE")
    (t / "presets" / "biotech" / "plan-template.md").write_text(
        "---\n_strategy: wrap\n---\nFDA SECTIONS\n{CORE_TEMPLATE}\nCLINICAL SECTIONS\n")
    text, _ = resolve_template.resolve("plan-template.md", kit_templates=t)
    assert "CORE" in text and text.startswith("FDA SECTIONS")


def test_unresolvable_skill_name_fails_scene_validation(tmp_path):
    scenes = tmp_path / "scenes"
    (scenes / "x").mkdir(parents=True)
    (scenes / "x" / "SKILL.md").write_text(
        "---\nname: x\nrole: orchestrator\n---\nstages:\n  - skill: ghost\n")
    assert validate_scenes.validate_skill(scenes / "x", {"real-skill"})


def test_consequential_gate_never_delegable():
    # workflow.yml template encodes the two tiers; the consequential gates carry
    # requires_budget_estimate and are documented as never-delegable (Q80).
    wf = yaml.safe_load((ROOT / "plugins" / "vertical-plugins" / "scenarios" /
                         "templates" / "workflow.yml").read_text())
    tiers = {g["id"]: g["tier"] for g in wf["gates"]}
    assert tiers["gate4"] == "consequential" and tiers["gate1"] == "informational"
    assert wf["gates"][3]["requires_budget_estimate"] is True


def test_specify_while_unratified_refused(tmp_path):
    """UPDATED 2026-09-18 (T161). This fixture has NEITHER instrument, so it hits
    the neither-case — and that case now says so rather than reporting an
    unratified file that does not exist. T161 split one message into three:
    no instrument / this instrument is unratified / instrument missing that name
    (`constitution.md` vs `agentii.md`)."""
    ws = tmp_path / "workspace"
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    assert "no constitutional instrument" in str(exc.value)
    # …and the unratified case still says "unratified"
    agentii_cmd.constitution_scaffold(ws)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    assert "UNRATIFIED" in str(exc.value)


def test_early_thesis_bars_schema_requirement_is_declared():
    # Q42: the requirement lives in the plan command + entities template — both
    # must declare it so implement can refuse early theses without a bars schema.
    plan_skill = (ROOT / "plugins" / "vertical-plugins" / "scenarios" / "skills" /
                  "agentii" / "plan" / "SKILL.md").read_text()
    entities_tmpl = (ROOT / "plugins" / "vertical-plugins" / "scenarios" /
                     "templates" / "entities-template.md").read_text()
    assert "bars schema" in plan_skill
    assert "no bars schema, no implement" in entities_tmpl


def test_budget_and_skill_pin_wired(tmp_path):
    # T053: implement's budget enforcement + skill_pin recording are functional
    halted, msg = dispatch.enforce_budget(6, {"max_tasks": 5})
    assert halted
    sk = tmp_path / "sk"
    sk.mkdir()
    (sk / "SKILL.md").write_text("# s")
    h = dispatch.skill_version_hash(sk)
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    dispatch.record_skill_pin(thesis, "s", h)
    assert "s" in (thesis / "skill_pins.jsonl").read_text()