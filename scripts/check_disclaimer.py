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
    print("Q139 placement-table coverage:")
    for name in PLACEMENT_OUTPUTS:
        present = (TEMPLATES / name).is_file()
        if name == "thesis-report.html":
            note = "template + producer (synthesize_report.py) — gate LIVE"
        elif present:
            note = "template present, NO producer — gate VACUOUS (Q105)"
        else:
            note = "no template, no producer — nothing to gate yet"
        print(f"  {'ok ' if present else '-- '} {name:20s} {note}")

    if problems:
        print("\nFAIL:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("\nOK — disclaimer.md is the single source; no drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
