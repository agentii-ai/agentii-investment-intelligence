#!/usr/bin/env python3
"""check_output_quality.py — FR-002: each skill's output is held to THAT skill's own
declared `## Output Structure` (spec 058 T024/T025).

FR-002's rule, in its own words: *"Criteria are **derived from the skill, never invented**
— a skill is held to a standard it already agreed to."* So every threshold below is read
out of the skill's own `## Output Structure` section, and the fallbacks are declared as
fallbacks rather than silently applied:

  * the Executive Summary word budget — `(≤200 words)` on the element's line;
  * the citation density — `≥1 citation per 200 words` in the Citations paragraph;
  * the classification vocabulary — `[FACT]` / `[DEDUCTED]` / `[VIEW]`;
  * the element list itself — the numbered `**Bold**` elements of `## Output Structure`.

ONE IMPLEMENTATION, THREE CALLERS (T024's corrected design). The criteria live in
`criteria_for()` and `check_artifact()`; `scripts/artifact_baseline.py` imports them for
its corpus measurement, the CLI below is what `quickstart.md` Scenario 3 runs, and
`tests/test_output_quality.py` drives each criterion with a fixture that must fail. The
alternative — a gate and a baseline each measuring "declared elements present/missing" —
is the two-implementations-of-one-check defect this kit keeps removing (`D1`).

CRITERION 6 IS A VALUE CHECK, NOT A KEY CHECK — and that distinction is the whole point
(T025's note). All five pins are present in **206 of 206** corpus artifacts, and the
enforcement is `if not fm.get(pin)` (`scripts/g1_gate.py:126`), a truthiness test: a pin
whose value is `"[TBD]"` or `unratified` passes today. So this criterion tests the VALUE
against a declared placeholder vocabulary and names the value when it fails.

WHAT IT CANNOT SEE, stated because an unreported gap reads as coverage
---------------------------------------------------------------------
* **Criterion 4 is a proximity proxy.** "Every material fact is immediately followed by its
  inline link" is checked as *a line stating a material fact must carry a `/v/` link on it or
  one line either side* — and the definition is IMPORTED, `check_output.bare_fact_lines`,
  rather than re-derived here: two definitions of one rule is the drift this kit keeps
  removing. What it still cannot see: a link that resolves to the wrong page, and a fact
  stated without a currency amount, a percentage or a quotation, which it does not recognise
  as a fact at all. The corpus-wide count is reported rather than a verdict, because the
  honest answer is "N lines state a fact and carry no link", not "this artifact is wrong".
* **The element check matches HEADINGS.** An artifact that discusses "Business Model Type"
  in prose without a heading is scored absent. That is the declared convention (§ elements
  are sections) and it is why the corpus measures 0 of 206 on Executive Summary — the
  finding is real, and this note is why nobody has to re-derive that it is a heading rule.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Criterion 4's rule has ONE implementation and it is not this file's. See `criterion 4` below for
# why the calibrated definition wins, and `check_output.bare_fact_lines` for the calibration.
import check_output as lint  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
ERC = ROOT / "plugins" / "vertical-plugins" / "equity-research-core" / "skills" / "agentii"
# FR-002 applies to EVERY skill, not only the equity-research-core nine: measured 2026-09-21,
# scoping the search to ERC left 135 of 221 corpus artifacts unmatched — because
# `revenue-decomp` and `sotp-valuation` are models-and-pitches skills. An artifact that
# cannot be matched is reported (never graded against a default), but a matcher that
# cannot find the skill it belongs to produces a report about the matcher.
ALL_SKILLS_ROOT = ROOT / "plugins" / "vertical-plugins"

FIVE_PINS = ("as_of", "constitution_pin", "assumption_pin", "corpus_version", "skill_pin")

# A pin value that carries no information. Declared rather than guessed, and only ever
# consulted for the five pins: an artifact may legitimately write "unknown" in prose.
PLACEHOLDER_VALUES = {
    "", "-", "—", "n/a", "na", "none", "null", "nil", "tbd", "tba", "todo", "unset",
    "unknown", "placeholder", "unratified", "xxx", "x", "0", "0000-00-00", "[tbd]",
    "[todo]", "[unset]", "<tbd>", "?", "??",
}

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_OUT_STRUCTURE = re.compile(r"^## Output Structure\s*\n(.*?)(?=\n## |\Z)", re.DOTALL | re.M)
_NUMBERED = re.compile(r"^\s*(\d+)\.\s+\*\*(?P<title>[^*]+)\*\*", re.M)
_WORD_BUDGET = re.compile(r"[≤<=]\s*(\d+)\s*words?", re.I)
_PER_WORDS = re.compile(r"per\s+(\d+)\s+words?", re.I)
_LINK = re.compile(r"https://agentii\.ai/v/[^\s)\"'\\>]+")
_BADGE = re.compile(r"\[(?:FACT|DEDUCTED|VIEW)\]")
#: `_FIGURE` USED TO LIVE HERE and is deleted rather than left: after criterion 4 began importing
#: `check_output.bare_fact_lines` (2026-09-25) nothing read it. Its pattern was
#: `[\$€£]\d|\d+(?:\.\d+)?(%|bn|billion|m|million|k|x)|\b\d{4}\b` — the last alternative is why it
#: fired on a year, which the rule it duplicates explicitly refuses. A constant with no reader is
#: a claim with no check (spec 058 `T261` deleted `TOKEN_BUDGETS` for the same reason); if a future
#: criterion needs a figure pattern, it needs a criterion, not a resurrection.
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")


# ── criteria, derived from the skill ────────────────────────────────────────

def criteria_for(skill_dir: Path) -> dict:
    """The thresholds this skill declares about its own output.

    Every field records whether it was DECLARED or is a fallback, so the gate can say
    which standard it applied and a reader can tell a skill's own rule from this script's.
    """
    sk = skill_dir / "SKILL.md"
    text = sk.read_text(encoding="utf-8", errors="ignore") if sk.is_file() else ""
    m = _OUT_STRUCTURE.search(text)
    block = m.group(1) if m else ""
    elements = [e.group("title").strip() for e in _NUMBERED.finditer(block)]
    budget = None
    for line in block.splitlines():
        if "executive summary" in line.lower():
            b = _WORD_BUDGET.search(line)
            if b:
                budget = int(b.group(1))
    per = _PER_WORDS.search(text)
    return {
        "skill": skill_dir.name,
        "elements": elements,
        "exec_words": budget if budget is not None else 200,
        "exec_words_declared": budget is not None,
        "citations_per_words": int(per.group(1)) if per else 200,
        "citations_declared": per is not None,
        "badges_declared": bool(_BADGE.search(text)),
    }


# ── the artifact ────────────────────────────────────────────────────────────

def _frontmatter(text: str) -> dict:
    m = _FRONTMATTER.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _body(text: str) -> str:
    m = _FRONTMATTER.match(text)
    return text[m.end():] if m else text


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def _headings(body: str) -> set[str]:
    return {_norm(l.lstrip("# ").strip()) for l in body.splitlines() if _HEADING.match(l)}


def element_present(title: str, headings: set[str]) -> bool:
    """A declared element counts as present when a heading names it.

    Starts-with rather than equality: a skill declares `Executive Summary` and an artifact
    writes `## Executive Summary (Q3 2026)`, which is the element. The slack is at the
    end of the title only — so `Business Model Type` does not match `Business Model`."""
    n = _norm(title)
    return any(h == n or h.startswith(n + " ") for h in headings)


def _count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def section(body: str, title: str) -> str | None:
    """The body of the section whose heading starts with `title`."""
    lines = body.splitlines()
    n = _norm(title)
    start = None
    for i, l in enumerate(lines):
        if _HEADING.match(l) and _norm(l.lstrip("# ").strip()).startswith(n):
            start = i + 1
            break
    if start is None:
        return None
    out = []
    for l in lines[start:]:
        if _HEADING.match(l):
            break
        out.append(l)
    return "\n".join(out)


def check_text(text: str, *,
               criteria: dict | None = None) -> tuple[list[str], dict]:
    """`(problems, counts)` for one artifact. `criteria` comes from `criteria_for`; when
    omitted, only the criteria that need no skill are applied (the pins, and the roll-up's
    own non-duplication). Existence of a declared element is NOT one of them: it comes from
    the skill, so a caller without criteria cannot check it and must not pretend to."""
    problems: list[str] = []
    counts: dict = {}
    fm = _frontmatter(text)
    body = _body(text)

    # ── criterion 6: the five pins, by VALUE ────────────────────────────────
    for p in FIVE_PINS:
        if p not in fm:
            problems.append(f"criterion 6: pin `{p}` is absent — the artifact declares no "
                            f"{p}, so nothing can be reproduced from it")
            continue
        v = str(fm.get(p) or "").strip()
        if v.lower() in PLACEHOLDER_VALUES:
            problems.append(
                f"criterion 6: pin `{p}` = {v!r} is a placeholder. All five keys are "
                f"present in 206 of 206 corpus artifacts, so a key test passes "
                f"universally — the value is the thing that carries meaning (FR-002)")
    counts["pins"] = len(FIVE_PINS)

    # ── criterion 3 + the citation surface ─────────────────────────────────
    inline = _LINK.findall(body)
    fm_urls = [s.get("url") for s in (fm.get("citations") or [])
               if isinstance(s, dict) and s.get("url")]
    words = _count_words(body)
    counts["words"] = words
    counts["inline_links"] = len(inline)
    counts["citation_urls"] = len(set(inline) | set(fm_urls))
    per = (criteria or {}).get("citations_per_words", 200)
    needed = max(1, words // per) if words else 0
    counts["citations_needed"] = needed
    if needed and counts["citation_urls"] < needed:
        problems.append(
            f"criterion 3: {counts['citation_urls']} citation url(s) for {words} words — "
            f"the rule is ≥1 per {per} words, so {needed} are required (declared in this "
            f"skill's own Citations paragraph)")

    # ── criterion 2: the classification badges ─────────────────────────────
    counts["badges"] = len(_BADGE.findall(body))
    if (criteria or {}).get("badges_declared", True) and counts["badges"] == 0:
        problems.append(
            "criterion 2: no `[FACT]`/`[DEDUCTED]`/`[VIEW]` badge anywhere — the skill "
            "declares that findings are tagged, so an untagged artifact cannot be read "
            "for what is observed and what is inferred")

    # ── criterion 4: a material fact needs its link beside it ───────────────
    # ONE RULE, ONE IMPLEMENTATION (D1) — and this criterion's was the second copy. Until
    # 2026-09-25 it used its own `_FIGURE`, which matched `\b\d{4}\b` and therefore fired on a
    # YEAR, plus a same-line-only window. `check_output.bare_fact_lines` was calibrated against
    # the corpus this standard is about (28 of 50 artifacts, 2026-09-24; `specs/062-.../
    # evidence/output-lint-calibration.md`), so it is the definition that survived measurement,
    # and it is the one imported here. The two also disagreed on `[DEDUCTED]` lines, coverage
    # gaps and methodology notes, which the calibrated rule exempts and this one flagged.
    #
    # THE COUNT CHANGES MEANING WITH THE DEFINITION, recorded rather than smoothed: a count
    # taken before this date includes years and same-line-only misses; one taken after counts
    # material facts with a one-line window. Comparing them compares two rules, not two corpora.
    unlinked = lint.bare_fact_lines(body)
    counts["figures_without_inline_link"] = len(unlinked)
    if unlinked:
        problems.append(
            f"criterion 4: {len(unlinked)} line(s) state a material fact with no `/v/` link "
            f"beside them (same line or one either side). First: {unlinked[0]}")

    # ── criterion 5: a roll-up, IF PRESENT, must be non-duplicative ─────────
    # THIS CRITERION WAS THE ONE PLACE THAT BROKE FR-002, and the repair is a removal.
    #
    # Until 2026-09-25 it REQUIRED a bottom Citations section outright — a rule this script
    # INVENTED rather than derived, so a skill that declared no Citations element was still
    # held to one. In the same tree, `scripts/check_output.py` R3 (spec 062 `FR-034`) REJECTS
    # a trailing roll-up, because the owner's standard is the link beside the fact. Two
    # instruments with opposite verdicts on one shape, and neither read the skill's own text.
    #
    # What is left is the roll-up's own property: a section that repeats its own lines verbatim
    # is duplication by construction, declared or not. EXISTENCE IS NOT CHECKED HERE — a skill
    # that declares the element is covered by the declared-elements check below, which is where
    # "the skill is the authority" already lives. One defect keeps one reporter.
    roll = None
    for cand in ("Coverage Gaps & Citations", "Citations", "Coverage Gaps"):
        roll = section(body, cand)
        if roll is not None:
            break
    counts["has_citations_rollup"] = roll is not None
    if roll is not None:
        items = [l.strip() for l in roll.splitlines() if l.strip()]
        dupes = len(items) - len(set(items))
        counts["rollup_duplicate_lines"] = dupes
        if dupes:
            problems.append(
                f"criterion 5: the Citations roll-up repeats {dupes} line(s) verbatim — "
                f"an index that restates what it already indexes is duplication, not an index")

    # ── criterion 1 + the declared elements ────────────────────────────────
    if criteria:
        headings = _headings(body)
        missing = [e for e in criteria["elements"] if not element_present(e, headings)]
        counts["elements_declared"] = len(criteria["elements"])
        counts["elements_missing"] = len(missing)
        for e in missing:
            problems.append(
                f"declared element absent: `{e}` — the skill's own `## Output Structure` "
                f"lists it, and FR-002 holds an output to the standard its skill declared")
        budget = criteria["exec_words"]
        es = section(body, "Executive Summary")
        if es is not None:
            n = _count_words(es)
            counts["exec_words"] = n
            if n > budget:
                problems.append(
                    f"criterion 1: Executive Summary is {n} words against the declared "
                    f"budget of {budget}"
                    + ("" if criteria.get("exec_words_declared") else
                       " (fallback — the skill declares no budget)"))
    return problems, counts


def check_artifact(path: Path, criteria: dict | None = None) -> tuple[list[str], dict]:
    return check_text(path.read_text(encoding="utf-8", errors="ignore"), criteria=criteria)


def skill_for(artifact: Path, skills_root: Path = ALL_SKILLS_ROOT) -> Path | None:
    """Which skill produced this artifact: the filename's `{date}_{skill}_{affix}.md`
    token, else the frontmatter `skill_pin`. Reported when unresolvable — an artifact
    cannot be held to a standard it cannot be matched to.

    `skills_root` is the vertical-plugins tree by default, so the search covers all 14
    verticals; a caller may narrow it to one vertical for a targeted run."""
    stem = artifact.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}(?:_\d{4})?_(?P<skill>[a-z0-9-]+)", stem)
    candidates = [m.group("skill")] if m else []
    fm = _frontmatter(artifact.read_text(encoding="utf-8", errors="ignore"))
    pin = str(fm.get("skill_pin") or "").split("@")[0].strip()
    if pin:
        candidates.append(pin)
    for cand in candidates:
        for hit in sorted(skills_root.glob(f"*/skills/agentii/{cand}/SKILL.md")):
            return hit.parent
    return None


def check_artifacts(root: Path, skills_root: Path = ALL_SKILLS_ROOT) -> tuple[list[str], dict]:
    problems: list[str] = []
    examined = {"artifacts": 0, "matched_to_a_skill": 0, "unmatched": 0,
                "elements_declared": 0, "elements_missing": 0,
                "figures_without_inline_link": 0}
    for art in sorted(root.rglob("*.md")):
        if "artifacts" not in art.parts and art.parent.name != "_cross":
            continue
        examined["artifacts"] += 1
        skill = skill_for(art, skills_root)
        crit = criteria_for(skill) if skill else None
        if skill:
            examined["matched_to_a_skill"] += 1
        else:
            examined["unmatched"] += 1
            problems.append(
                f"{art}: no skill could be resolved from the filename or `skill_pin`, so "
                f"no declared standard applies — reported rather than scored against a "
                f"default (FR-002: the criteria come from the skill)")
        p, c = check_artifact(art, crit)
        problems += [f"{art}: {x}" for x in p]
        examined["elements_declared"] += c.get("elements_declared", 0)
        examined["elements_missing"] += c.get("elements_missing", 0)
        examined["figures_without_inline_link"] += c.get("figures_without_inline_link", 0)
    return problems, examined


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_output_quality.py",
        description="FR-002 — hold an artifact to its own skill's declared Output Structure.")
    ap.add_argument("paths", nargs="+", type=Path, help="artifact files or directories")
    ap.add_argument("--skills-root", type=Path, default=ALL_SKILLS_ROOT,
                    help="where the skills live")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    problems: list[str] = []
    examined = {"artifacts": 0, "matched_to_a_skill": 0, "unmatched": 0,
                "elements_declared": 0, "elements_missing": 0,
                "figures_without_inline_link": 0}
    for p in a.paths:
        if p.is_dir():
            pr, ex = check_artifacts(p, a.skills_root)
        elif p.is_file():
            skill = skill_for(p, a.skills_root)
            pr, c = check_artifact(p, criteria_for(skill) if skill else None)
            pr = [f"{p}: {x}" for x in pr]
            ex = {"artifacts": 1, "matched_to_a_skill": int(bool(skill)),
                  "unmatched": int(not skill),
                  "elements_declared": c.get("elements_declared", 0),
                  "elements_missing": c.get("elements_missing", 0),
                  "figures_without_inline_link": c.get("figures_without_inline_link", 0)}
        else:
            print(f"FAIL   {p}: not found", file=sys.stderr)
            return 2
        problems += pr
        for k in examined:
            examined[k] += ex.get(k, 0)

    if a.json:
        print(json.dumps({"problems": problems, "examined": examined}, indent=2))
    else:
        for m in problems:
            print(f"FAIL   {m}", file=sys.stderr)

    if examined["artifacts"] == 0:
        print("FAIL   no artifact examined — the path matched nothing, which is not a pass",
              file=sys.stderr)
        return 1
    if problems:
        if not a.json:
            print(f"FAIL — {len(problems)} finding(s) across {examined['artifacts']} "
                  f"artifact(s); {examined['elements_missing']} of "
                  f"{examined['elements_declared']} declared element(s) absent, "
                  f"{examined['figures_without_inline_link']} figure(s) without an inline "
                  f"link", file=sys.stderr)
        return 1
    print(f"OK — {examined['artifacts']} artifact(s), "
          f"{examined['matched_to_a_skill']} matched to a skill, "
          f"{examined['elements_declared']} declared element(s) all present, 0 findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
