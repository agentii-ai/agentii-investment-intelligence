#!/usr/bin/env python3
"""US5 T028-T032: move reference-y level-2 sections out of large skill bodies.

Moves `## Production Grounding` and `## xlsx-author Conventions` (background /
convention material, not primary operational guidance) into
references/methodology.md for skills still over the word threshold, leaving a
one-line pointer.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us5_extras.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)
THRESHOLD_WORDS = 900

SECTIONS = {
    "## Production Grounding": "Production data-plane grounding (scale, locators) is in `references/methodology.md`.",
    "## xlsx-author Conventions": "Excel formatting conventions are in `references/methodology.md` and `contracts/office-tooling.md`.",
}


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if len(text.split()) <= THRESHOLD_WORDS:
        return False
    moved = []
    for header, pointer in SECTIONS.items():
        pat = re.compile(r"(\n" + re.escape(header) + r"\s*\n)(.*?)(?=\n## )", re.DOTALL)
        m = pat.search(text)
        if not m:
            continue
        body = m.group(2).strip()
        if not body or pointer in body:
            continue
        moved.append((header.lstrip("# "), body))
        text = text[:m.start()] + m.group(1) + "\n" + pointer + "\n" + text[m.end():]
        if len(text.split()) <= THRESHOLD_WORDS:
            break
    if not moved:
        return False
    refs = path.parent / "references"
    refs.mkdir(exist_ok=True)
    meth = refs / "methodology.md"
    skill_name = path.parent.name
    if meth.exists():
        chunks = [meth.read_text(encoding="utf-8").rstrip() + "\n"]
    else:
        chunks = [f"# {skill_name} — Methodology Detail\n\nExtracted from SKILL.md for progressive disclosure (US5).\n"]
    for header, body in moved:
        chunks.append(f"\n## {header}\n\n{body}\n")
    meth.write_text("".join(chunks), encoding="utf-8")
    text = re.sub(r"\n{3,}", "\n\n", text)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for f in FILES:
        if migrate(Path(f)):
            changed += 1
    print(f"moved extra sections for {changed} skills")


if __name__ == "__main__":
    main()
