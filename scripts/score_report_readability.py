#!/usr/bin/env python3
"""The SCORED readability tier for a synthesize report (spec 058 FR-065, T088).

THE OTHER HALF OF A SPLIT, AND THE SPLIT IS THE POINT. `check_report_readability.py` blocks a merge on
four conventions that text can decide. This file holds everything readability needs that structure
**cannot** see — whether the argument is any good, whether the lede is the *right* call, whether the
prose explains or merely describes — and it must never block anything. A reader must not be able to read
"passes the gate" as "reads well", which is why the two are separate programs rather than two sections
of one report.

WHY THE AUTHOR SCORES, AND WHAT THIS PROGRAM DOES INSTEAD. `FR-065` is explicit: *"The author scores
against the rubric as part of the authoring step."* An LLM judge cannot gate a merge, and a mechanical
proxy scored automatically would be a fifth blocking check wearing a rubric's clothes. So this program
does the two things a machine can honestly do:

  1. **Makes the rubric concrete** — it prints each criterion with the objective evidence a scorer needs
     to judge it (prose-to-figure ratio, takeaway lengths, count of claim-bearing sentences). The
     judgement stays with the author; the measurement does not.
  2. **Records the number and notices a regression** — `--score N` records it, `--previous M` compares.
     The consequence is `FR-065`'s: a score below the previous release's MUST be explained in the
     deliverable itself. The trigger is a **regression, not an absolute threshold**, so no score is
     chosen in advance and the first report sets its own baseline.

THE SCORE HAS A NAMED CONSUMER, WHICH IS WHY IT IS ALLOWED TO EXIST. `FR-040` requires that a field
recording a condition either triggers an action or is removed, and a score nobody reads is that defect.
The consumer is the **human reviewer**; the consequence is the explanation above; the record lives in the
report's frontmatter beside the pins (`T091`). There is no threshold, because a threshold with a warning
is what `check_disclaimer.py` was before Check 48 — described in its own comments as the enforcement
point, and invoked by nothing.

EXIT CODES. `0` always, except `2` for a usage error. This tier has no failing state — that is what
"non-blocking" means, and a non-zero exit here would quietly become a gate.

Usage:
    python3 scripts/score_report_readability.py <content.html>
    python3 scripts/score_report_readability.py <content.html> --score 4 --previous 5
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_report_readability as gate  # noqa: E402

#: The rubric. Each entry is (key, question the author answers, what the evidence column shows).
#: The questions are deliberately answerable by a human reading the report and deliberately NOT by this
#: program — that is the test of whether a criterion belongs in this tier.
RUBRIC: tuple[tuple[str, str, str], ...] = (
    (
        "argument",
        "Does each key argument state a call an analyst could disagree with — or merely describe?",
        "claim-bearing sentences per page",
    ),
    (
        "lede",
        "Does the opening state the RIGHT call — the one the evidence actually supports?",
        "length and position of the opening paragraph",
    ),
    (
        "exhibits",
        "Do the exhibit takeaways interpret the figures, or restate them?",
        "words per takeaway, and whether it names the pattern rather than the values",
    ),
    (
        "balance",
        "Is the report prose with evidence in it, or evidence with prose attached?",
        "share of visible text that is prose rather than figure or table",
    ),
    (
        "read-through",
        "Read end to end, does the conclusion follow from the evidence presented?",
        "not measurable — this one is entirely the reviewer's",
    ),
)


def evidence(content: str) -> dict[str, object]:
    """The objective measurements a scorer needs, and nothing that pretends to be a verdict."""
    pages = gate.PAGE_RX.findall(content)
    prose_words = figure_paras = 0
    claim_sentences = 0
    takeaway_lengths: list[int] = []

    for page in pages:
        for para_html in gate.PARA_RX.findall(page):
            text = gate.text_of(para_html)
            if not text:
                continue
            if gate.is_machine_annotation(text):
                continue
            if gate.is_numbers_only(text):
                figure_paras += 1
                continue
            ws = gate.words(text)
            prose_words += len(ws)
            claim_sentences += len(gate.CLAIM_RX.findall(text))

        exhibits = list(gate.EXHIBIT_RX.finditer(page))
        for i, ex in enumerate(exhibits):
            seg = page[ex.end(): exhibits[i + 1].start() if i + 1 < len(exhibits) else len(page)]
            para = gate._first_paragraph_after(seg, 0)
            if para:
                takeaway_lengths.append(len(gate.words(para)))

    return {
        "pages": len(pages),
        "prose_words": prose_words,
        "number_only_paragraphs": figure_paras,
        "claim_bearing_sentences": claim_sentences,
        "claims_per_page": round(claim_sentences / len(pages), 1) if pages else 0,
        "exhibits_with_takeaways": len(takeaway_lengths),
        "median_takeaway_words": (sorted(takeaway_lengths)[len(takeaway_lengths) // 2]
                                  if takeaway_lengths else 0),
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    score = previous = None
    if "--score" in argv:
        i = argv.index("--score")
        score = int(argv[i + 1]); del argv[i:i + 2]
    if "--previous" in argv:
        i = argv.index("--previous")
        previous = int(argv[i + 1]); del argv[i:i + 2]

    if len(argv) != 1:
        print("usage: score_report_readability.py <content.html> [--score N] [--previous N]",
              file=sys.stderr)
        return 2

    path = Path(argv[0])
    if not path.is_file():
        print(f"score_report_readability: no such file: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8")
    ev = evidence(content)

    if score is None:
        print("report readability — SCORED tier (non-blocking)\n")
        print("This tier exists because structure cannot see whether a report is any good. Read the")
        print("report, answer each question on a 1–5 scale, and record the total with --score.\n")
        for key, question, shown in RUBRIC:
            print(f"  [{key}] {question}")
            print(f"      evidence: {shown}")
        print("\nMeasured evidence for this report:")
        for k, v in ev.items():
            print(f"  {k}: {v}")
        print("\nPassing the blocking gate does NOT mean this report reads well. That is this tier.")
        return 0

    if not 1 <= score <= 25:
        print(f"score_report_readability: --score must be 1–25 (five criteria, 1–5 each), got {score}",
              file=sys.stderr)
        return 2

    print(f"report readability — SCORED tier: {score}/25 recorded")
    if previous is not None:
        if score < previous:
            print(
                f"\n  ⚠ REGRESSION: {score} is below the previous release's {previous}.\n"
                f"    FR-065: a drop MUST be explained in the deliverable itself. The trigger is a\n"
                f"    regression, not an absolute threshold — no score was chosen in advance, and this\n"
                f"    report's first score sets its own baseline.")
        elif score > previous:
            print(f"  improved on the previous release ({previous} → {score}).")
        else:
            print(f"  unchanged from the previous release ({previous}).")
    print(json.dumps(ev, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
