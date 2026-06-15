#!/usr/bin/env python3
"""US5 T028-T032: disclose verbose `### Retrieval Strategy` / `### Protocol` prose.

For skills still over the word threshold, moves the detailed content of the
`### Retrieval Strategy` and `### Protocol` methodology subsections into
`references/methodology.md` (appended), keeping the required headers (Check 23 /
FR-064) with a one-line pointer. The canonical retrieval decision tree already
lives in `contracts/retrieval.md`; this captures the skill-specific elaboration.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us5_methodology.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)
THRESHOLD_WORDS = 900

# header label -> (regex for the header line allowing optional 'N. ' ordinal, pointer)
SECTIONS = {
    "Retrieval Strategy": "See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.",
    "Protocol": "Step-by-step execution detail is in `references/methodology.md`.",
    "Ratio Definitions": "Full ratio formula definitions are in `references/methodology.md`.",
}


def extract_section(text: str, header: str):
    # match '### [N. ]<header>' line to next ### or ## header
    pat = re.compile(
        r"(\n###\s+(?:\d+\.\s+)?" + re.escape(header) + r"\s*\n)(.*?)(?=\n#{2,3} )",
        re.DOTALL,
    )
    return pat.search(text)


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if len(text.split()) <= THRESHOLD_WORDS:
        return False
    moved = []
    for header, pointer in SECTIONS.items():
        m = extract_section(text, header)
        if not m:
            continue
        body = m.group(2).strip()
        if not body or body == pointer:
            continue
        moved.append((header, body))
        replacement = m.group(1) + "\n" + pointer + "\n"
        text = text[:m.start()] + replacement + text[m.end():]
        if len(text.split()) <= THRESHOLD_WORDS:
            break
    if not moved:
        return False
    refs = path.parent / "references"
    refs.mkdir(exist_ok=True)
    meth = refs / "methodology.md"
    skill_name = path.parent.name
    chunks = [f"# {skill_name} — Methodology Detail\n\nExtracted from SKILL.md for progressive disclosure (US5).\n"]
    if meth.exists():
        chunks = [meth.read_text(encoding="utf-8").rstrip() + "\n"]
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
    print(f"disclosed methodology detail for {changed} skills")


if __name__ == "__main__":
    main()
