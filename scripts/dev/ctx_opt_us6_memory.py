#!/usr/bin/env python3
"""US6 T034-T037 + US8 T054: wire memory/snapshot/output-frontmatter + TUI summary.

Inserts a consolidated `## Memory & Snapshot` block and a `## Final Summary (TUI)`
section (pointers to the shared contracts) into every SKILL.md, immediately before
the `## Error Handling` section (present in all skills). Idempotent.

References:
  - contracts/memory-load.md            (FR-090 pre-flight memory load)
  - contracts/output-frontmatter-schema.md (FR-090 structured output block)
  - contracts/snapshot-synthesis.md     (FR-091/092 two-tier + FACT/DEDUCTED/VIEW)
  - contracts/session-format.md         (FR-095 session archival)
  - contracts/citation-and-memory.md    (US8 Key Citations TUI block)

Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us6_memory.py
"""
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)

BLOCK = """## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

"""

MARKER = "## Final Summary (TUI)"


def migrate(text: str) -> str:
    if MARKER in text:
        return text  # idempotent
    idx = text.find("\n## Error Handling")
    if idx == -1:
        # append at end if no Error Handling (shouldn't happen)
        return text.rstrip() + "\n\n" + BLOCK
    insert_at = idx + 1  # keep the leading newline before ## Error Handling
    return text[:insert_at] + BLOCK + text[insert_at:]


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
