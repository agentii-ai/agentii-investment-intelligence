#!/usr/bin/env python3
"""US2 T018 + US4 T026 + US8 T052-T054: collapse citation/memory prose to one pointer.

In every SKILL.md, remove the standalone boilerplate lines that restate the
citation-density rule, the clickable link format, and the agentii.md-append
instruction, then ensure a single canonical "Citations & memory" pointer line is
present at the end of the `## Output Structure` section (or `## Output File` if no
Output Structure section exists).

The pointer references `contracts/citation-and-memory.md`, which holds the
density rule, the deployed clickable `/v/` link format, the Citation Placement
Policy (inline-after-fact + TUI Key Citations), and the agentii.md append.
Per-mode `- **Citation density**` bullets inside `## Modes` are preserved
(they start with "- ", not "**").

**THE POINTER NO LONGER MENTIONS A BOTTOM ROLL-UP AS THE SHAPE** (changed 2026-09-25, spec 062
`T084`). It used to say `a bottom **Citations** section provides a non-duplicative roll-up
index`, which read as a required element; the owner's standard is the link BESIDE the fact, and
spec 062's lint rejects a trailing roll-up against the same tree. The roll-up is now stated as
optional. **The substring must stay byte-equal to the line in each SKILL.md**: this script drops
an existing pointer by exact match and re-inserts this constant, so a drift of one space makes it
insert a SECOND pointer rather than replace the first.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_citation_pointer.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)

POINTER = (
    "**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation "
    "per 200 words; every material fact, table row, and metric is immediately followed "
    "by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; "
    "citations belong inline, a bottom roll-up index is optional and never a repeat of "
    "a link already given; the closing TUI reply includes a compact **Key Citations** "
    "list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to "
    "`agentii.md` per `contracts/agentii-md-schema.md`."
)

DROP_PREFIXES = (
    "**Citation density",
    "**Citation link format",
    "**agentii.md append",
)


def migrate(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    for ln in lines:
        st = ln.strip()
        if st == POINTER:
            continue  # will re-insert canonically
        if any(st.startswith(p) for p in DROP_PREFIXES):
            continue
        out.append(ln)

    # Re-insert the pointer at the end of ## Output Structure (else ## Output File)
    def insert_at_section(section: str, body: list[str]) -> bool:
        idx = None
        for i, ln in enumerate(body):
            if ln.strip() == section:
                idx = i
                break
        if idx is None:
            return False
        # find end of section (next "## " header or EOF)
        end = len(body)
        for j in range(idx + 1, len(body)):
            if body[j].startswith("## "):
                end = j
                break
        # trim trailing blanks within the section, then insert
        insert_pos = end
        while insert_pos - 1 > idx and body[insert_pos - 1].strip() == "":
            insert_pos -= 1
        body.insert(insert_pos, "")
        body.insert(insert_pos + 1, POINTER)
        return True

    if not insert_at_section("## Output Structure", out):
        insert_at_section("## Output File", out)

    new = "\n".join(out)
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new


def main() -> None:
    changed = 0
    for f in FILES:
        s0 = Path(f).read_text(encoding="utf-8")
        s1 = migrate(s0)
        if s1 != s0:
            Path(f).write_text(s1, encoding="utf-8")
            changed += 1
    print(f"updated {changed} files")


if __name__ == "__main__":
    main()
