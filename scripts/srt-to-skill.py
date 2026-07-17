#!/usr/bin/env python3
"""srt-to-skill.py — course SRT → spec-023-contract draft SKILL.md (spec 039 US6, T067/T068).

Reads trading-course SRT transcripts, extracts methodology/framework/rules, and emits a
draft SKILL.md that conforms to the spec-023 section contract. IP-safe (R6):
- SRT files are read from an EXTERNAL path and NEVER written into the repo.
- A paraphrase-guard rejects long verbatim spans from the source.
- Every draft carries an attribution line ("methodology inspired by …"), never verbatim quotes.

This module does the deterministic scaffolding + guards. The actual methodology
*summarization* (summary_points) is produced by an LLM at author time and passed in;
build_draft_skill assembles the contract-conformant document around it.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

_TS_RE = re.compile(r"^\d+\s*$|^\d{2}:\d{2}:\d{2},\d{3}\s*-->")


def parse_srt(path: Path) -> list[str]:
    """Return the text segments of an SRT, stripping indices + timestamps."""
    segments, buf = [], []
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s:
            if buf:
                segments.append(" ".join(buf).strip())
                buf = []
            continue
        if _TS_RE.match(s):
            continue
        buf.append(s)
    if buf:
        segments.append(" ".join(buf).strip())
    return [seg for seg in segments if seg]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def has_verbatim_span(candidate: str, sources: list[str], max_run: int = 12) -> bool:
    """True if `candidate` contains a run of >= max_run consecutive tokens that appears
    verbatim in any source segment (IP-safety paraphrase-guard, R6)."""
    cand = _tokens(candidate)
    if len(cand) < max_run:
        source_join = " ".join(_tokens(" ".join(sources)))
        return " ".join(cand) in source_join and len(cand) >= max_run
    source_join = " ".join(_tokens(" ".join(sources)))
    for i in range(len(cand) - max_run + 1):
        run = " ".join(cand[i:i + max_run])
        if run in source_join:
            return True
    return False


ATTRIBUTION = (
    "> Methodology inspired by publicly taught trading frameworks; all text is an "
    "original paraphrase. No verbatim course content is reproduced."
)


def build_draft_skill(skill_name: str, vertical: str, srt_paths: list[Path],
                      summary_points: list[str], *, description: str = "") -> str:
    """Assemble a spec-023-contract-conformant draft SKILL.md. summary_points are
    author/LLM-produced paraphrases; this function guards + frames them."""
    sources = []
    for p in srt_paths:
        sources.extend(parse_srt(p))
    # guard each summary point; drop any that trip the verbatim detector
    safe_points = [pt for pt in summary_points if not has_verbatim_span(pt, sources, max_run=8)]
    if not safe_points:
        safe_points = ["Framework summary pending author paraphrase (verbatim-guard removed all inputs)."]

    desc = description or f"{skill_name.replace('-', ' ')} — course-derived methodology skill"
    methodology_steps = "\n".join(f"### Step {i+1}\n{pt}" for i, pt in enumerate(safe_points))
    triggers = "\n".join(f"- {skill_name} trigger phrase {i+1}" for i in range(10))

    return f"""---
name: {skill_name}
description: {desc}
multi_ticker_semantics: single_target
retrieval_scope: structured_only
allowed_tools:
 - search_knowledge_entries
 - search_by_analogue
---

{ATTRIBUTION}

## Defaults
Parameter-free unless a ticker/context is supplied.

## Preflight
Works zero-key. See contracts/data-tool-preflight.md for optional API keys.

## Methodology
{methodology_steps}

## Output File
`{skill_name}/{{ticker}}-{skill_name}.md`

## Output Structure
1. Summary
2. Framework application
3. Signals / levels
4. Risks
5. Sources & attribution

## Error Handling
- No data: state so, do not fabricate.
- Coverage gap: annotate and proceed with partial analysis.

## Triggers
{triggers}

## References
Derived from course material (paraphrased). See attribution above.
"""


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="SRT → draft SKILL.md (spec 039 US6)")
    p.add_argument("--srt", action="append", type=Path, required=True, help="external SRT path (repeatable)")
    p.add_argument("--skill-name", required=True)
    p.add_argument("--vertical", required=True)
    p.add_argument("--summary-point", action="append", default=[], help="paraphrased framework point (repeatable)")
    p.add_argument("--dry-run", action="store_true", help="print draft, write nothing")
    p.add_argument("--out", type=Path, help="write draft here (must be inside repo skills dir)")
    args = p.parse_args(argv)

    draft = build_draft_skill(args.skill_name, args.vertical, args.srt, args.summary_point or [])
    if args.dry_run or not args.out:
        print(draft)
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(draft, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
