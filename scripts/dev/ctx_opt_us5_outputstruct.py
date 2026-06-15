#!/usr/bin/env python3
"""US5 T028-T032: progressive disclosure for `## Output Structure`.

Moves each skill's detailed `## Output Structure` template into
`references/output-structure.md` and replaces the body section with a compact,
CI-compliant summary (>=5 non-empty lines) that preserves the canonical
`**Citations & memory**:` pointer and states the inline-primary / bottom-rollup
citation policy (US8 T055). Creates a `references/` dir for every skill.

Only processes skills whose total word count exceeds the target threshold, so
already-lean skills are left intact.

Idempotent (re-running detects the pointer marker and skips). Source of truth =
vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us5_outputstruct.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)
THRESHOLD_WORDS = 900
MARKER = "Full section-by-section template"


def build_summary(citation_pointer: str) -> str:
    lines = [
        "## Output Structure",
        "",
        "The deliverable is a structured markdown report written to the path in `## Output File`. "
        "Full section-by-section template (headings, tables, and field definitions) lives in "
        "`references/output-structure.md`. Required elements:",
        "",
        "1. **Executive Summary** — headline conclusions (≤200 words).",
        "2. **Core analysis sections** — per this skill's methodology and analyst modes.",
        "3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.",
        "4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.",
        "5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.",
        "",
    ]
    if citation_pointer:
        lines.append(citation_pointer.strip())
        lines.append("")
    return "\n".join(lines)


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False  # already disclosed
    if len(text.split()) <= THRESHOLD_WORDS:
        return False
    m = re.search(r"\n## Output Structure\s*\n(.*?)(?=\n## )", text, re.DOTALL)
    if not m:
        return False
    body = m.group(1)
    # preserve the canonical citations pointer line if present
    cite = ""
    cm = re.search(r"^\*\*Citations & memory\*\*:.*$", body, re.MULTILINE)
    if cm:
        cite = cm.group(0)

    refs = path.parent / "references"
    refs.mkdir(exist_ok=True)
    out_md = refs / "output-structure.md"
    skill_name = path.parent.name
    header = (f"# {skill_name} — Output Structure (full template)\n\n"
              f"Extracted from SKILL.md for progressive disclosure (US5). The skill body "
              f"keeps a compact summary under `## Output Structure`.\n\n")
    out_md.write_text(header + body.strip() + "\n", encoding="utf-8")

    summary = build_summary(cite)
    new = text[:m.start()] + "\n" + summary + text[m.end():]
    new = re.sub(r"\n{3,}", "\n\n", new)
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for f in FILES:
        if migrate(Path(f)):
            changed += 1
    print(f"disclosed Output Structure for {changed} skills")


if __name__ == "__main__":
    main()
