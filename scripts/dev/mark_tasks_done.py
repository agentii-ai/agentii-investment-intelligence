#!/usr/bin/env python3
"""Mark completed task checkboxes [x] in tasks-context-optimization.md.

Sets `- [ ] TNNN` -> `- [x] TNNN` for the DONE task ids. Leaves the genuinely
incomplete / not-applicable tasks unchecked:
  T002  create working branch (intentionally skipped — staying on main)
  T003  append manifest to plan (superseded by the recorded delta appendix)
  T040  edit references/prompts/1/essentials.yaml (file does not exist in package)
  T051  live /equity-research-core:business-model NVDA run (needs live MCP)
  T068  commit/merge per AGENTS.md rebase workflow (staying on main, no merge)
  T082  live /models-and-pitches:xlsx-financials NVDA run (needs live MCP)

Usage: python3 scripts/dev/mark_tasks_done.py
"""
import re
from pathlib import Path

TASKS = Path("/Users/frank/A/agenzym/specs/023-agentii-financial-analysis/tasks-context-optimization.md")

NOT_DONE = {2, 3, 40, 51, 68, 82}
DONE = sorted(set(range(1, 85)) - NOT_DONE)
DONE_IDS = {f"T{n:03d}" for n in DONE}


def main() -> None:
    text = TASKS.read_text(encoding="utf-8")
    marked = 0

    def repl(m: re.Match) -> str:
        nonlocal marked
        tid = m.group(2)
        if tid in DONE_IDS:
            marked += 1
            return f"- [x] {tid}"
        return m.group(0)

    new = re.sub(r"- \[ \] (\*\*)?(T\d{3})", lambda m: repl_full(m), text)
    TASKS.write_text(new, encoding="utf-8")
    print(f"marked {marked} tasks [x]; left {len(NOT_DONE)} unchecked: {sorted(NOT_DONE)}")


def repl_full(m: re.Match) -> str:
    tid = m.group(2)
    if tid in DONE_IDS:
        # preserve any leading bold marker captured
        prefix = m.group(1) or ""
        return f"- [x] {prefix}{tid}"
    return m.group(0)


if __name__ == "__main__":
    # recompute marked count deterministically
    text = TASKS.read_text(encoding="utf-8")
    count = 0

    def _r(m: re.Match) -> str:
        global count
        tid = m.group(2)
        if tid in DONE_IDS:
            count += 1
            prefix = m.group(1) or ""
            return f"- [x] {prefix}{tid}"
        return m.group(0)

    new = re.sub(r"- \[ \] (\*\*)?(T\d{3})", _r, text)
    TASKS.write_text(new, encoding="utf-8")
    print(f"marked {count} tasks [x]; left unchecked: {sorted(NOT_DONE)}")
