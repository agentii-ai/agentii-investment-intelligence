#!/usr/bin/env python3
"""US3 T020-T023: reconcile retrieval_scope + allowed_tools for the 4 model skills.

dcf / comps / 3-statement / lbo declare `retrieval_scope: structured_only` but
their Protocol/Tool-Fallbacks bodies drive the three-layer document protocol and
name document-retrieval tools absent from `allowed_tools`. This sets the scope to
`unstructured_document_search` and appends exactly the document tools each body
references (union is identical across the four), preserving existing entries and
order.

Idempotent. Source of truth = vertical-plugins.

Usage: python3 scripts/dev/ctx_opt_us3_scope.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "plugins/vertical-plugins/models-and-pitches/skills/agentii"
SKILLS = ["dcf", "comps", "3-statement", "lbo"]

# document tools referenced by all four bodies (verified via grep)
DOC_TOOLS = [
    "search_documents",
    "search_sec_filings",
    "read_source_outline",
    "read_source_deep_outline",
    "read_source_pages",
    "search_keyword_in_source",
    "search_cross_period",
    "batch_search",
    "get_statement_structure",
]


def migrate(text: str) -> str:
    lines = text.split("\n")
    # locate allowed_tools block and retrieval_scope line within frontmatter
    at_start = None
    rs_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "allowed_tools:":
            at_start = i
        if ln.startswith("retrieval_scope:") and rs_idx is None:
            rs_idx = i
            break
    if at_start is None or rs_idx is None:
        raise SystemExit("frontmatter shape unexpected")

    # collect existing tool tokens between at_start+1 and rs_idx
    existing = []
    indent = " "
    for ln in lines[at_start + 1:rs_idx]:
        st = ln.strip()
        if st.startswith("- "):
            existing.append(st[2:].strip())
            indent = ln[: len(ln) - len(ln.lstrip())]

    missing = [t for t in DOC_TOOLS if t not in existing]
    insert_lines = [f"{indent}- {t}" for t in missing]

    new = lines[:rs_idx] + insert_lines + lines[rs_idx:]
    out = "\n".join(new)
    out = out.replace("retrieval_scope: structured_only",
                      "retrieval_scope: unstructured_document_search")
    return out


def main() -> None:
    for s in SKILLS:
        f = BASE / s / "SKILL.md"
        s0 = f.read_text(encoding="utf-8")
        s1 = migrate(s0)
        if s1 != s0:
            f.write_text(s1, encoding="utf-8")
            print(f"reconciled {s}")
        else:
            print(f"{s} already reconciled")


if __name__ == "__main__":
    main()
