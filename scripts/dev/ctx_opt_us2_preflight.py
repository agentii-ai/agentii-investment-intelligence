#!/usr/bin/env python3
"""US2 (T016+T017): de-duplicate the inline Preflight boilerplate.

**SUPERSEDED for the tracing pointer (2026-09-23) — do not re-run this script.** Its `TRACE_PTR` still
holds the header-only pointer and it re-inserts its `PREFLIGHT_PTR` unconditionally, so a re-run would
(a) write the pointer back without the `_run_id` carry Check 18 now requires and (b) duplicate the
pre-flight line in the 30 skills that carry the longer wording. The pointer now lives in
`scripts/dev/trace_instruction_v1_1.py` (idempotent, sentence-level, dry-run by default), and the
sentence itself is declared once in `contracts/skill-methodology-template.md`; the constant below is
kept in step with it so that this file, if it is ever revisited, cannot disagree with the repository.


Within each SKILL.md `## Preflight` section, replace the four canonical
boilerplate pieces (MCP curl probe, generic ticker-resolution paragraph,
workspace style.md override paragraph, and the Agent Call Tracing paragraph)
with one-line pointers to the shared contracts. Skill-specific Preflight notes
(e.g. ratio-analysis's get_realtime_quote note) are preserved.

Idempotent. Source of truth = vertical-plugins; run sync-agent-skills.py +
assemble-agentii-namespace.sh afterwards to propagate.

Usage: python3 scripts/dev/ctx_opt_us2_preflight.py
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True)

CURL = ('!curl -s -o /dev/null -w "%{http_code}" --max-time 2 '
        'https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"')
PREFLIGHT_PTR = (
    "Run the canonical pre-flight sequence — MCP health probe, ticker resolution, "
    "workspace `style.md` override, memory load, and coverage check. "
    "See `contracts/preflight.md`."
)
TRACE_PTR = "Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md` — carry the `_run_id` from your first tool result and name yourself (and your parent, if you were spawned)."


def migrate(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    in_pf = False
    for ln in lines:
        if ln.strip() == "## Preflight":
            out.append(ln)
            out.append("")
            out.append(PREFLIGHT_PTR)
            in_pf = True
            continue
        if in_pf and ln.startswith("## "):
            in_pf = False
            out.append(ln)
            continue
        if in_pf:
            st = ln.strip()
            if st == CURL:
                continue
            if st.startswith("**Ticker resolution"):
                continue
            if st.startswith("**Workspace style.md override"):
                continue
            if st.startswith("**Agent Call Tracing**"):
                out.append(TRACE_PTR)
                continue
            # drop a Preflight pointer if a previous run already inserted one
            if st == PREFLIGHT_PTR:
                continue
        out.append(ln)
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
