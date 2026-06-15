#!/usr/bin/env python3
"""US5 T028-T032: move `## Tool Fallbacks` tables into references/tool-fallbacks.md.

The Tool Fallbacks table is reference material the agent consults on tool
failure, not primary guidance — a prime progressive-disclosure candidate. Moves
it to references/tool-fallbacks.md and leaves a one-line pointer. Only touches
skills still over the word threshold.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us5_toolfallbacks.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)
THRESHOLD_WORDS = 900
POINTER = "## Tool Fallbacks\n\nPer-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.\n"


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "references/tool-fallbacks.md" in text:
        return False
    if len(text.split()) <= THRESHOLD_WORDS:
        return False
    m = re.search(r"\n## Tool Fallbacks\s*\n(.*?)(?=\n## )", text, re.DOTALL)
    if not m:
        return False
    body = m.group(1).strip()
    if "|" not in body:  # nothing tabular to move
        return False
    refs = path.parent / "references"
    refs.mkdir(exist_ok=True)
    skill_name = path.parent.name
    (refs / "tool-fallbacks.md").write_text(
        f"# {skill_name} — Tool Fallbacks\n\nExtracted from SKILL.md for progressive disclosure (US5).\n\n" + body + "\n",
        encoding="utf-8",
    )
    new = text[:m.start()] + "\n" + POINTER + text[m.end():]
    new = re.sub(r"\n{3,}", "\n\n", new)
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for f in FILES:
        if migrate(Path(f)):
            changed += 1
    print(f"moved Tool Fallbacks for {changed} skills")


if __name__ == "__main__":
    main()
