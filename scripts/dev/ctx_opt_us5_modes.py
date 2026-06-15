#!/usr/bin/env python3
"""US5 T028-T031: progressive disclosure — move verbose `### Mode:` blocks to references/.

The 9 equity-research-core skills carry their analyst-mode definitions as
`### Mode:` subsections under `## Methodology`; these dominate the body word
count. This moves the mode block (from the first `### Mode:` line up to the next
level-2 `## ` header) into `references/modes.md` and leaves a compact pointer
subsection, preserving the 5 required methodology subsections that precede it.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us5_modes.py
"""
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)

POINTER = """### Analyst Modes

This skill exposes addressable analysis modes (`--mode=<slug>` / `--modes=<s1>,<s2>` / `--mode=all`; see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The full mode definitions and their output templates live in `references/modes.md`. The default invocation runs the essentials subset.

"""


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    # find first '### Mode:' line
    first = None
    for i, ln in enumerate(lines):
        if ln.startswith("### Mode:"):
            first = i
            break
    if first is None:
        return False
    # find next level-2 header after `first`
    end = len(lines)
    for j in range(first, len(lines)):
        if lines[j].startswith("## ") and j > first:
            end = j
            break
    mode_block = "\n".join(lines[first:end]).rstrip() + "\n"

    refs = path.parent / "references"
    refs.mkdir(exist_ok=True)
    modes_md = refs / "modes.md"
    skill_name = path.parent.name
    header = f"# {skill_name} — Analyst Mode Definitions\n\nExtracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.\n\n"
    modes_md.write_text(header + mode_block, encoding="utf-8")

    new_lines = lines[:first] + [POINTER.rstrip("\n"), ""] + lines[end:]
    new = "\n".join(new_lines)
    while "\n\n\n" in new:
        new = new.replace("\n\n\n", "\n\n")
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for f in FILES:
        if migrate(Path(f)):
            changed += 1
    print(f"extracted modes from {changed} skills")


if __name__ == "__main__":
    main()
