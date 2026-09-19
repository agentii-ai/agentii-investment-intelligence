#!/usr/bin/env python3
"""check_disclaimer.py — spec 046 Q139 self-check.

`disclaimer.md` is the single source for the disclaimer text. This script proves
it, instead of trusting a comment that says so:

  1. disclaimer.md carries exactly one ```markdown block and one ```html block.
  2. thesis-report.html carries NO copy of the block — it is injected at assembly
     time by synthesize_report.build_html from disclaimer.md.
  3. dashboard.html's footer body equals the canonical block, modulo the
     placeholder token style ([WORKSPACE] canonical, __WORKSPACE__ in HTML).
  4. Every output named in disclaimer.md's Placement table is reported as
     template-present or template-absent, with the reason a gate can or cannot
     run. (Q105: an output with no producer has a VACUOUS gate, and saying so is
     the point — a silent "0 problems" is the failure this spec keeps finding.)
  5. (T202) The two outputs with no template — `pitch-deck` and `earnings-preview`
     — are gated at their CONTRACT: the skill must still bind `disclaimer.md` and
     must not have authored a second copy of the clauses. "Nothing to gate yet" is
     honest but it is not the end of what is checkable, and a requirement recorded
     only in prose can be edited away by someone who never read Q139.
  6. (T202) `dashboard.html` is reported as HALF-live rather than wholly VACUOUS:
     its footer IS drift-checked on every run (item 3). Grouping a live check with
     a dead one made a working gate look absent.
  7. (T204) `README.md` still carries its `## Disclaimer` section. The README is the
     project's landing page and its single most-read document, and it had **no
     disclaimer at all** — zero occurrences of the word — while the four generated
     outputs were gated. Human-facing docs were outside every rule here; a section
     added once is a section that can be edited away once.

**Was invoked by nothing until 2026-09-19.** Q139 named this script as the
disclaimer's enforcement point, it was correct, and no test and no CI step ran it
— the defect the spec calls "a declared mechanism that silently returns empty
success", inside the machinery written to end it. It is now a CI step and Check 48
fails if any `check_*.py` is reachable from nowhere again.

Exit codes: 0 = consistent, 1 = drift or malformed source.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
SOURCE = TEMPLATES / "disclaimer.md"

# Outputs named in disclaimer.md's Placement table, and where a template would be.
PLACEMENT_OUTPUTS = ["thesis-report.html", "dashboard.html", "pitch-deck", "earnings-preview"]

_FENCE_RE = {
    "markdown": re.compile(r"^```markdown\n(.*?)^```", re.DOTALL | re.MULTILINE),
    "html": re.compile(r"^```html\n(.*?)^```", re.DOTALL | re.MULTILINE),
}
# The canonical placeholders vs. this template's HTML-native spelling.
_PLACEHOLDER_STYLE = [(r"\[WORKSPACE\]", "__WORKSPACE__"),
                      (r"\[AS_OF\]", "__AS_OF__"),
                      (r"\[GENERATED\]", "__GENERATED__")]


def _normalise(block: str) -> str:
    """Collapse whitespace and unify the placeholder spelling, so the comparison
    is about the clause set — the thing that is actually the contract (Q139 rule
    3) — not about line wrapping (Q139 rule 1's 'verbatim' is about clauses)."""
    for canonical, html_style in _PLACEHOLDER_STYLE:
        block = re.sub(canonical, html_style, block)
    return re.sub(r"\s+", " ", block).strip()


def _canonical(problems: list[str]) -> dict[str, str]:
    if not SOURCE.is_file():
        problems.append(f"missing single source: {SOURCE}")
        return {}
    src = SOURCE.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for kind, rx in _FENCE_RE.items():
        found = rx.findall(src)
        if len(found) != 1:
            problems.append(
                f"{SOURCE.name} must carry exactly one ```{kind} block (found {len(found)})")
        elif found:
            out[kind] = found[0].strip()
    return out


def _element_body(html: str) -> str | None:
    """Inner HTML of the disclaimer element, wrapper stripped. The wrapper differs
    by output — <section> in the canonical block, <section class="page …"> in the
    report, <footer> in the dashboard — so the comparison is inner-to-inner."""
    m = re.search(r'<(section|footer)\b[^>]*class="[^"]*\bdisclaimer\b[^"]*"[^>]*>(.*?)</\1>',
                  html, re.DOTALL)
    return m.group(2).strip() if m else None


# ── T202: the contract-level gate for outputs that have no template ─────────

# Q139's closed set has four members; `pitch-deck` and `earnings-preview` have no
# template and no producer. The honest report was "nothing to gate yet" — but that
# is not the same as "nothing is checkable". The requirement IS recorded, in each
# skill's `## Disclaimer` section, and a requirement that exists only as prose is a
# requirement that can be edited away by someone who never read Q139.
#
# So while a template is absent, the CONTRACT is what is gated:
#   1. the skill still binds the single source (it names `disclaimer.md`), and
#   2. it has NOT authored a second copy of the clauses.
# (2) is the one that matters. "Do not restate, paraphrase or fork it" is Q139's
# rule 1 and the only way to obey it is to keep pointing at the source; a skill
# that inlines the text has forked it whether or not the wording matches today.
_CONTRACTS = {
    "pitch-deck": ROOT / "plugins" / "vertical-plugins" / "models-and-pitches"
                  / "skills" / "agentii" / "pitch-deck" / "SKILL.md",
    "earnings-preview": ROOT / "plugins" / "vertical-plugins" / "models-and-pitches"
                        / "skills" / "agentii" / "earnings-preview" / "SKILL.md",
}

# Lines that make a claim the disclaimer says, i.e. authored text rather than a
# pointer. Matched loosely on purpose: the failure being prevented is a COPY, and a
# copy usually reuses most of the original's substance.
_CLAUSE_TEXT = re.compile(
    r"not investment advice|not an offer or solicitation|do their own due diligence|"
    r"accept no liability|past performance is not indicative", re.I)


def _contract_of(output: str) -> Path | None:
    p = _CONTRACTS.get(output)
    return p if p and p.is_file() else None


def _check_contract_bindings(canonical: dict[str, str]) -> list[str]:
    """Gate the output contract where no template exists (T202)."""
    problems: list[str] = []
    for output, path in sorted(_CONTRACTS.items()):
        if not path.is_file():
            problems.append(
                f"{output}: its output contract is missing ({path.relative_to(ROOT)}) — "
                f"the requirement it recorded is gone with it")
            continue
        text = path.read_text(encoding="utf-8")
        if "## Disclaimer" not in text:
            problems.append(
                f"{output}: `{path.name}` no longer carries a `## Disclaimer` section. "
                f"It is the only place this output's obligation is recorded — with no "
                f"template to mount the block on, deleting the section deletes the "
                f"requirement.")
        if "templates/disclaimer.md" not in text:
            problems.append(
                f"{output}: `{path.name}` no longer names `templates/disclaimer.md`, so "
                f"it does not bind the single source (Q139 rule 1).")
        # Forbidden: an authored copy of the clauses (Q139 rule 1 — no fork).
        for n, line in enumerate(text.splitlines(), 1):
            if _CLAUSE_TEXT.search(line) and "disclaimer.md" not in line:
                problems.append(
                    f"{output}: `{path.name}`:{n} restates the disclaimer's own words "
                    f"({line.strip()[:60]!r}). Q139 rule 1 forbids restating, "
                    f"paraphrasing or forking; the skill must POINT at the source.")
    return problems


# ── T204: the human-facing documents ────────────────────────────────────────

# Everything above this line governs MACHINE-GENERATED outputs. The repository's
# own landing page was outside every rule: README.md contained zero occurrences of
# the word "disclaimer" while four generated document types were gated, and the only
# advice-adjacent text on it was an unpoliced `[!IMPORTANT]` callout.
#
# The README must NOT paste the canonical block. That block says the document is
# "research and analysis, produced by an automated research system for internal
# use" — true of a research report, false of a software README — and Q139 rule 1
# forbids forking it. So the rule here is weak ON PURPOSE: the section must exist,
# it must say the thing that matters, and it must POINT at the canonical source
# rather than restate it. Checking the wording would turn a disclaimer into a
# template and make the next honest edit a build failure.
_HUMAN_DOCS = {
    "README.md": {
        "section": "## Disclaimer",
        # The two obligations a software-reader disclaimer cannot drop.
        "must_say": ["not investment advice", "due diligence"],
        # …and it must not become a second authored copy of the report block.
        "must_point": "templates/disclaimer.md",
    },
}


def _check_human_docs() -> list[str]:
    """Gate the disclaimer on the repo's own human-facing documents (T204)."""
    problems: list[str] = []
    for name, rule in sorted(_HUMAN_DOCS.items()):
        path = ROOT / name
        if not path.is_file():
            problems.append(f"{name}: missing — it is the project's landing page")
            continue
        text = path.read_text(encoding="utf-8")
        if rule["section"] not in text:
            problems.append(
                f"{name}: no `{rule['section']}` section. The four generated outputs are "
                f"gated; this is the document the most people read, and a section added "
                f"once is a section that can be edited away once.")
            continue
        low = text.lower()
        missing = [s for s in rule["must_say"] if s.lower() not in low]
        if missing:
            problems.append(
                f"{name}: its Disclaimer section no longer states {missing}. These are the "
                f"obligations, not decorations.")
        if rule["must_point"] not in text:
            problems.append(
                f"{name}: its Disclaimer no longer points at `{rule['must_point']}`. "
                f"Generated research outputs carry THAT block; this document must not "
                f"become a second authored copy of it (Q139 rule 1).")
    return problems


def main() -> int:
    problems: list[str] = []
    canonical = _canonical(problems)
    html_block = canonical.get("html", "")

    # 2. The report template must not carry a copy.
    report = TEMPLATES / "thesis-report.html"
    if report.is_file() and html_block:
        rtext = report.read_text(encoding="utf-8")
        # Strip HTML comments first: a comment that *describes* the block is not a copy.
        live = re.sub(r"<!--.*?-->", "", rtext, flags=re.DOTALL)
        if _normalise(html_block) in _normalise(live):
            problems.append(
                "thesis-report.html carries a copy of the disclaimer block — it must be "
                "injected at assembly (synthesize_report.build_html), not baked in")
        if 'class="disclaimer"' in live and "<style" not in live.split('class="disclaimer"')[0]:
            pass  # CSS mention only; the CSS selector is expected.
    else:
        problems.append(f"missing template: {report}")

    # 3. The dashboard copy must match the clause set, inner-to-inner.
    dash = TEMPLATES / "dashboard.html"
    canonical_body = _element_body(html_block) if html_block else None
    if dash.is_file():
        body = _element_body(re.sub(r"<!--.*?-->", "", dash.read_text(encoding="utf-8"),
                                    flags=re.DOTALL))
        if body is None:
            problems.append("dashboard.html has no element with class=\"disclaimer\" (Q139)")
        elif canonical_body and _normalise(body) != _normalise(canonical_body):
            problems.append(
                "dashboard.html's disclaimer body has DRIFTED from disclaimer.md — the "
                "clause set is the contract; re-copy it or read it at build time")
    else:
        problems.append(f"missing template: {dash}")

    # 4. Report the placement-table outputs honestly.
    # 5. (T202) The two outputs with no template: gate the CONTRACT instead.
    #    Q139's closed set has four members and three had no place to mount the
    #    block. "Nothing to gate yet" is honest, but it is not the end of what is
    #    checkable: the requirement IS recorded — in each skill's output contract —
    #    and a requirement recorded in prose is a requirement that can be edited
    #    away. So the contract itself is gated: the skill must still bind the
    #    canonical source, and must not have authored a second copy of the clauses.
    contract_problems = _check_contract_bindings(canonical)
    problems += contract_problems

    # 7. (T204) The repo's own landing page. See `_check_human_docs`.
    problems += _check_human_docs()

    # 6. (T202) The dashboard's gate is HALF-live and used to be reported as wholly
    #    VACUOUS. Its footer is drift-checked above on every run; what has no
    #    producer is the placeholder filling. Reporting both as one thing made a
    #    live check look dead.
    dash_live = (TEMPLATES / "dashboard.html").is_file() and not any(
        "dashboard.html" in p for p in problems)

    print("Q139 placement-table coverage:")
    for name in PLACEMENT_OUTPUTS:
        present = (TEMPLATES / name).is_file()
        if name == "thesis-report.html":
            note = "template + producer (synthesize_report.py) — gate LIVE"
        elif name == "dashboard.html":
            note = ("template; footer drift-checked here — LIVE · placeholder fill has "
                    "no producer — VACUOUS (Q105)" if dash_live
                    else "template present, DRIFT — see failures")
        elif present:
            note = "template present, NO producer — gate VACUOUS (Q105)"
        else:
            bound = _contract_of(name) is not None
            note = ("no template/producer — contract-bound, gated here (T202)"
                    if bound else "no template, no producer, NO contract — nothing to gate")
        print(f"  {'ok ' if (present or name in _CONTRACTS) else '-- '} {name:20s} {note}")

    if problems:
        print("\nFAIL:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("\nOK — disclaimer.md is the single source; no drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
