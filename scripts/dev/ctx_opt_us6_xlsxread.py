#!/usr/bin/env python3
"""US6 T038: add `xlsx-read` to allowed_tools for dcf/comps/3-statement/audit-xls.

These model/audit skills consume existing `.xlsx` workbooks (contract:
contracts/xlsx-read-tool.md). Adds the tool to each skill's allowed_tools list
(before the retrieval_scope line), idempotently.

Usage: python3 scripts/dev/ctx_opt_us6_xlsxread.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "plugins/vertical-plugins/models-and-pitches/skills/agentii"
SKILLS = ["dcf", "comps", "3-statement", "audit-xls"]
TOOL = "xlsx-read"


def migrate(text: str) -> str:
    lines = text.split("\n")
    at_start = rs_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "allowed_tools:":
            at_start = i
        if ln.startswith("retrieval_scope:") and rs_idx is None:
            rs_idx = i
            break
    if at_start is None or rs_idx is None:
        raise SystemExit("frontmatter shape unexpected")
    existing = [ln.strip()[2:].strip() for ln in lines[at_start + 1:rs_idx] if ln.strip().startswith("- ")]
    if TOOL in existing:
        return text
    indent = " "
    for ln in lines[at_start + 1:rs_idx]:
        if ln.strip().startswith("- "):
            indent = ln[: len(ln) - len(ln.lstrip())]
            break
    new = lines[:rs_idx] + [f"{indent}- {TOOL}"] + lines[rs_idx:]
    return "\n".join(new)


def main() -> None:
    for s in SKILLS:
        f = BASE / s / "SKILL.md"
        s0 = f.read_text(encoding="utf-8")
        s1 = migrate(s0)
        if s1 != s0:
            f.write_text(s1, encoding="utf-8")
            print(f"added {TOOL} to {s}")
        else:
            print(f"{s} already has {TOOL}")


if __name__ == "__main__":
    main()
