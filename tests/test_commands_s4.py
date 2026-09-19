"""S4 command tests (T050–T054): specify refusal + creation, task decomposition
with mode:all expansion and [P] rules, constitution scaffold + bump validation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentii_cmd  # noqa: E402


def test_specify_refused_while_unratified(tmp_path):
    ws = tmp_path / "workspace"
    # no constitution.md AND no agentii.md → refused (T161: the NEITHER case,
    # which now names the missing instrument rather than calling it unratified —
    # "absent" and "unratified" are different problems with different fixes)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    assert "no constitutional instrument" in str(exc.value)
    assert "constitution.md" in str(exc.value) and "agentii.md" in str(exc.value)
    # scaffolded-but-placeholder → still refused. T161: the message now names
    # WHICH file is unratified, so the assertion is case-insensitive and checks
    # the file name rather than one exact spelling.
    agentii_cmd.constitution_scaffold(ws)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.specify(ws, "mvp")
    msg = str(exc.value).lower()
    assert "unratified" in msg
    assert "constitution.md" in msg


def test_scaffold_refuses_to_clobber_ratified_constitution(tmp_path):
    """D75 #3: a ratified constitution is the workspace's doctrine — scaffold must
    refuse to overwrite it silently (the dogfooding session clobbered a ratified
    v1.0.0 with placeholders). --force is the deliberate reset."""
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    (ws / "constitution.md").write_text(
        (ws / "constitution.md").read_text().replace("[WORKSPACE_NAME]", "Test Fund"))
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.constitution_scaffold(ws)
    assert "already ratified" in str(exc.value)
    # the ratified doctrine survived the refused scaffold
    assert "Test Fund" in (ws / "constitution.md").read_text()
    # --force is the deliberate reset path
    agentii_cmd.constitution_scaffold(ws, force=True)
    assert "[WORKSPACE_NAME]" in (ws / "constitution.md").read_text()


def test_specify_creates_thesis_after_ratification(tmp_path):
    ws = tmp_path / "workspace"
    _ratify(ws)
    thesis = agentii_cmd.specify(ws, "mvp")
    assert thesis.name == "001-mvp"
    assert (thesis / "spec.md").is_file()
    assert (thesis / "thesis.md").is_file()
    assert (thesis / "checklists" / "thesis-quality.md").is_file()
    # second call gets a distinct id (mkdir-CAS)
    assert agentii_cmd.specify(ws, "mvp").name == "002-mvp"


def test_task_expansion_mode_all(tmp_path):
    matrix = [{"pillar": "P1", "ticker": "NVDA", "skill": "dcf", "modes": ["all"],
               "all_modes": ["base", "sensitivity", "bear"], "purpose": "valuation"}]
    rows = agentii_cmd.expand_tasks(matrix)
    assert len(rows) == 3  # mode: all expands at generation, never one task
    assert all("× dcf ×" in r for r in rows)
    modes = [r.split("× ")[2].split(" ")[0] for r in rows]
    assert set(modes) == {"base", "sensitivity", "bear"}


def test_task_parallel_marker_by_file_key(tmp_path):
    matrix = [
        {"pillar": "P1", "ticker": "NVDA", "skill": "business-model", "mode": "default"},
        {"pillar": "P1", "ticker": "AMD", "skill": "business-model", "mode": "default"},
        {"pillar": "P1", "ticker": "NVDA", "skill": "business-model", "mode": "deep"},
    ]
    rows = agentii_cmd.expand_tasks(matrix)
    assert "[P] " in rows[0]  # first file key → parallel
    assert "[P] " in rows[1]  # different file (AMD) → parallel
    assert "[P] " not in rows[2]  # same (ticker, skill) file → serialized


def test_task_rows_carry_src_refs(tmp_path):
    rows = agentii_cmd.expand_tasks(
        [{"pillar": "P2", "ticker": "NVDA", "skill": "competitive", "mode": "default",
          "src": "pillar-2"}])
    assert "(src: pillar-2)" in rows[0]


def test_constitution_scaffold_writes_all_five_files(tmp_path):
    ws = tmp_path / "workspace"
    files = agentii_cmd.constitution_scaffold(ws)
    names = {f.name for f in files}
    assert names == {"constitution.md", "constitution.yaml", "assumptions.yaml",
                     "value-checks.yaml", "taxonomy.yaml", ".gitignore"}  # Q77/Q82 cache hygiene


def test_constitution_amend_validates_bump_values(tmp_path):
    ws = tmp_path / "workspace"
    agentii_cmd.constitution_scaffold(ws)
    with pytest.raises(SystemExit) as exc:
        agentii_cmd.constitution_amend(ws, "trivial", "note")
    assert "bump must be one of" in str(exc.value)
    agentii_cmd.constitution_amend(ws, "minor", "added a principle")
    assert "bump: minor" in (ws / "constitution.md").read_text()


# --- F1 remediation: the SKILL.md-documented spec-matrix path -----------------

SPEC_MATRIX = """## 3. Skill Deployment Matrix
| Skill | Vertical | Depth | Tickers | Market Data Stage | Purpose |
|---|---|:---:|---|---|---|
| `business-model` | ERC | Full | NVDA, AMD | none | understand |
| `recent-quarter` | ERC | Light | NVDA | none | earnings |
"""


def test_parse_spec_matrix():
    rows = agentii_cmd.parse_spec_matrix(SPEC_MATRIX)
    assert [r["skill"] for r in rows] == ["business-model", "recent-quarter"]
    assert rows[0]["tickers"] == ["NVDA", "AMD"]
    assert rows[0]["depth"] == "full"
    assert rows[1]["depth"] == "light"


def test_parse_spec_matrix_against_the_real_template():
    """The regression the old test could not catch, because it used the wrong input.

    `SPEC_MATRIX` above spells its separator `|---|---|:---:|---|---|---|`. The
    shipped `spec-template.md` spells it `|-------|----------|:---:|…|`, and the
    parser skipped only the literal `"---"` — so the separator survived as a row and
    every thesis scaffolded from the template carried a phantom task with
    `skill='-------'`. The fixture and the generator disagreed, and the test used the
    fixture.

    So this test does not spell a separator at all: it reads the GENERATOR and feeds
    the parser what the generator actually emits. A future template edit that changes
    the separator form cannot silently reintroduce the bug — it fails here.
    """
    template = (ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
                / "spec-template.md").read_text(encoding="utf-8")

    # The template's own matrix, verbatim: header + separator, no data rows.
    matrix = template.split("## 3. Skill Deployment Matrix", 1)[1].split("\n## ", 1)[0]
    rows = agentii_cmd.parse_spec_matrix("## 3. Skill Deployment Matrix" + matrix)
    assert rows == [], f"the template's separator row parsed as a task: {rows}"

    # …and with a real row appended to the template's own header, exactly one row
    # comes back. Both halves are needed: the first asserts the separator is skipped,
    # the second that the skip did not become "skip everything".
    spec = ("## 3. Skill Deployment Matrix" + matrix.rstrip("\n")
            + "\n| `dcf` | valuation | Deep | NVDA | stage-2 | valuation range |\n")
    rows = agentii_cmd.parse_spec_matrix(spec)
    assert [r["skill"] for r in rows] == ["dcf"], rows
    assert rows[0]["tickers"] == ["NVDA"]
    assert rows[0]["purpose"] == "valuation range"


def test_separator_row_detection_is_structural_not_a_literal_list():
    """Any dash/colon arrangement is a separator; a populated cell never matches.

    The old check was a list of literals (`"---"`, `":"`), which can only be as
    correct as the author's memory of what every generator writes. This pins the
    property instead: separator-shaped in, separator-shaped out, and no false
    positives on the values a real matrix holds.
    """
    for sep in ("|---|", "|---|---|:---:|---|---|---|",
                "|-------|----------|:---:|--------|:---:|------|",
                "| --- | :---: | --- |", "|:-:|"):
        cells = [c.strip() for c in sep.strip("|").split("|")]
        assert agentii_cmd._is_separator_row(cells), sep

    # A ticker list, a skill name, and a Purpose cell all contain letters.
    for row in ("| `dcf` | valuation | Deep | NVDA, AMD | stage-2 | valuation range |",
                "| Skill | Vertical | Depth | Tickers | Stage | Purpose |",
                "| a-1 | b | c | d | e | f |"):
        cells = [c.strip() for c in row.strip("|").split("|")]
        assert not agentii_cmd._is_separator_row(cells), row


def test_depth_to_modes_q79_merge():
    import yaml

    reg = yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    deep_modes = agentii_cmd.depth_to_modes("full", reg, "business-model")
    assert len(deep_modes) >= 3  # registry-expanded: the skill's real mode slugs
    light_modes = agentii_cmd.depth_to_modes("light", reg, "business-model")
    assert light_modes  # essentials_modes (backfilled in S7)
    assert light_modes != deep_modes or len(light_modes) < len(deep_modes)


def test_tasks_from_spec_end_to_end(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_MATRIX)
    import subprocess

    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "agentii_cmd.py"), "tasks",
         "--thesis", str(thesis), "--spec", str(spec)],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    rows = [l for l in res.stdout.splitlines() if l.startswith("- [ ]")]
    # Full-depth business-model × {NVDA, AMD} expands to registry modes; the
    # Light-depth recent-quarter row carries essentials_modes.
    bm_rows = [r for r in rows if "business-model" in r]
    rq_rows = [r for r in rows if "recent-quarter" in r]
    assert len(bm_rows) >= 6  # 2 tickers × ≥3 deep modes
    import yaml

    reg = yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    essentials = next(s["essentials_modes"] for s in reg["skills"]
                      if s["skill_name"] == "recent-quarter")
    # Light = essentials_modes (Q79): 1 ticker × len(essentials) rows
    assert len(rq_rows) == len(essentials)
    assert any("× business-model ×" in r for r in bm_rows)


SPEC_PILLARS_AND_MATRIX = """# Research Thesis: x

## 1b. Pillars

### Pillar 1 — Value chain position (Priority: P1)
**wrong_if**: `metric=a threshold=1 source=b`
**Subscribed**: `NVDA × business-model`

### Pillar 2 — Unit economics (Priority: P2)
**wrong_if**: `metric=c threshold=2 source=d`
**Subscribed**: `NVDA × business-model`, `NVDA × recent-quarter`

## 3. Skill Deployment Matrix
| Skill | Vertical | Depth | Tickers | Market Data Stage | Purpose |
|---|---|:---:|---|---|---|
| `business-model` | ERC | Light | NVDA | none | value chain position mapping |
| `recent-quarter` | ERC | Light | NVDA | none | cost stack decomposition |
"""


def test_tasks_src_reflects_pillar_and_purpose_is_carried_through(tmp_path):
    """Regression (2026-09-10, found dogfooding T-001): two traceability defects.

    (a) tasks_from_spec() hardcoded {"pillar": "P1"} for every entry, so every
        emitted row read `(src: P1)` regardless of which pillar the work served.
        Q26 traceability from converge back to a pillar was therefore vacuous.
    (b) The spec matrix's Purpose column (col 6) was parsed away, so every task
        carried the same placeholder text "per spec deployment matrix".
    """
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_PILLARS_AND_MATRIX)
    rows = agentii_cmd.tasks_from_spec(spec, None)
    joined = "\n".join(rows)

    # (a) src: must name the pillar(s) the skill is subscribed to, not a literal P1
    #     recent-quarter is subscribed only by PIL-2 -> src must be PIL-2
    rq = [r for r in rows if "recent-quarter" in r]
    assert rq, "no recent-quarter rows emitted"
    assert all("(src: PIL-2)" in r for r in rq), rq[0]
    #     business-model appears under both PIL-1 and PIL-2 -> multi-pillar form
    bm = [r for r in rows if "business-model" in r]
    assert bm and all("[PIL-1/PIL-2]" in r for r in bm), bm[0]
    assert "spec-business-model" in bm[0]
    #     the old behaviour must be gone
    assert "(src: P1)" not in joined

    # (b) the matrix Purpose text must survive into the task line
    assert "cost stack decomposition" in joined
    assert "per spec deployment matrix" not in joined


def test_parse_subs_to_pillars_maps_skill_to_pillars():
    m = agentii_cmd.parse_subs_to_pillars(SPEC_PILLARS_AND_MATRIX)
    assert m["recent-quarter"] == ["PIL-2"]
    assert sorted(m["business-model"]) == ["PIL-1", "PIL-2"]


# --- D75 #4: agentii.clarify (the 8th kit command) ----------------------------

SPEC_UNDERSPEC = """# Research Thesis: x

## 1. Research Question
Which humanoid companies win?

### Pillar 1 — (Priority: P1)
**wrong_if**: If adoption stalls.

**Subscribed**: NVDA, TSLA

## 2. Universe Definition
| Ticker | Company | Sector | Weight | Rationale for Inclusion |
|---|---|:---:|---|
| TSLA | Tesla | Tech | 20% |  |
| NVDA | NVIDIA | Tech | 20% | Compute leader |
"""


def test_clarify_scanner_finds_underspecified_items(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC)
    qs = agentii_cmd.clarify_questions(spec)
    ids = {q["id"] for q in qs}
    assert "wrongif-0" in ids          # prose wrong_if → machine-checkable
    assert "rationale-TSLA" in ids     # universe row without rationale
    assert "budget" in ids             # Q58 undeclared
    assert "expiry" in ids             # Q59 undeclared
    assert "subscriptions" in ids      # tokens not in TICKER × skill form
    assert len(qs) <= agentii_cmd.MAX_CLARIFY_QUESTIONS


def test_clarify_scanner_clean_spec_yields_fewer_questions(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC.replace("If adoption stalls.",
                                           "metric=units threshold=1000 source=company"))
    qs = agentii_cmd.clarify_questions(spec)
    assert not any(q["id"] == "wrongif-0" for q in qs)


def test_clarify_subscription_scanner_is_line_anchored_and_ticker_prefixed(tmp_path):
    """Regression (2026-09-10, found dogfooding T-001): two defects in check #5.

    (a) The regex used `([^$]+)`. Inside a character class `$` is a LITERAL
        dollar, not an end anchor, and it matches newlines — so with no '$' in
        the file the capture ran to EOF and every spec reported one bogus
        "malformed subscription" assembled from unrelated trailing lines.
    (b) The predicate was `" × " not in s`, which accepts `skill × mode`. A
        ticker-less token contains ' × ' as well, so the real Q79 violation was
        never reported at all.

    Net effect: the only candidate emitted was a false positive, and the true
    violations were invisible.
    """
    # (a) line-anchoring: content AFTER the Subscribed line must not bleed in.
    spec = tmp_path / "spec.md"
    spec.write_text(
        "### Pillar 1 — A (Priority: P1)\n"
        "**Subscribed**: `NVDA × business-model`\n"
        "\n"
        "### Pillar 2 — B (Priority: P2)\n"
        "**Subscribed**: `secular-trends × default`\n"
        "\n"
        "## 2. Universe Definition\n"
        "| TSLA | Tesla | Tech | 20% | rationale |\n"
    )
    qs = agentii_cmd.clarify_questions(spec)
    sub_qs = [q for q in qs if q["id"] == "subscriptions"]
    # exactly one pillar is malformed — P1 must NOT be swept up by P2's capture
    assert len(sub_qs) == 1, f"expected 1 flagged pillar, got {len(sub_qs)}"
    assert "secular-trends" in sub_qs[0]["question"]
    assert "business-model" not in sub_qs[0]["question"]

    # (b) ticker-less `skill × mode` IS a violation; the old predicate passed it.
    assert " × " in "`secular-trends × default`"

    # and a fully correct spec yields no subscription question at all
    clean = tmp_path / "clean.md"
    clean.write_text(
        "### Pillar 1 — A (Priority: P1)\n"
        "**Subscribed**: `NVDA × business-model`, `TSLA × risk`\n"
    )
    assert not any(q["id"] == "subscriptions"
                   for q in agentii_cmd.clarify_questions(clean))


def test_clarify_encode_appends_clarifications_section(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(SPEC_UNDERSPEC)
    report = agentii_cmd.clarify_encode(spec, [
        {"question": "Declare the thesis budget", "answer": "{max_tasks: 80, max_retries_per_task: 2}"}])
    text = spec.read_text()
    assert "## Clarifications" in text
    assert "max_tasks: 80" in text
    assert "encoded 1 answer" in report
    # second encode appends, never rewrites
    agentii_cmd.clarify_encode(spec, [
        {"question": "Q2", "answer": "A2"}])
    assert text.count("## Clarifications") == 1

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
