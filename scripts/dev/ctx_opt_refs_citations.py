#!/usr/bin/env python3
"""US4 T025/T026 + US8 T053: resolvable refs + canonical clickable citations.

1. T025 — repoint every dangling bare `retrieval.md` reference in skill bodies to
   the resolvable `contracts/retrieval.md` (consistent with the package's
   `contracts/` reference convention).
2. T053 — replace weak citation placeholders in output templates with the
   explicit clickable `/v/` form:
     - `{Citations}` / `{Source(s)}` / `{Source}` table-column tokens
     - the `_(cite source filing in standard agentii citation format at runtime)_`
       hint
   become the canonical clickable link
   `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_refs_citations.py
"""
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)

CLICKABLE = "[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})"
CITE_HINT = "_(cite source filing in standard agentii citation format at runtime)_"

# order matters: longer / more specific first
REPLACEMENTS = [
    ("`retrieval.md`", "`contracts/retrieval.md`"),
    (CITE_HINT, CLICKABLE),
    ("{Citations}", CLICKABLE),
    ("{Source(s)}", CLICKABLE),
    ("{Source}", CLICKABLE),
]


def migrate(text: str) -> str:
    # avoid double-prefixing an already-repointed retrieval ref
    text = text.replace("`contracts/retrieval.md`", "\x00RETR\x00")
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = text.replace("\x00RETR\x00", "`contracts/retrieval.md`")
    return text


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
