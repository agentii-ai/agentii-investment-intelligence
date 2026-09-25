#!/usr/bin/env python3
"""check_output_rubric.py — the buy-side rubric: what the other two instruments cannot see
(spec 062 `FR-034` iii, `T083`).

THE BAR IS REGISTERED BEFORE THE EVALUATION (`FR-016`), and this docstring IS the registration.
Everything below — the four questions, their thresholds, and the thin-sample rule — was written
before any artifact was scored. The corpus rate is reported NEXT TO each bar, in the evidence file,
so a reader can judge the bar itself rather than only the artifacts against it.

WHY A THIRD INSTRUMENT. Two already exist and neither can say anything about content:

  `scripts/check_output.py`          structure only — and its own docstring says so: it cannot see
                                     whether a link RESOLVES, whether it is the RIGHT page, or
                                     whether the prose is any good
  `scripts/check_output_quality.py`  each skill's declared elements, budget, badges, pins by value

So a well-formed artifact carrying a false or empty conclusion passes both. That is the failure
mode this specification documents ("a well-formed artifact carrying a false claim"), and it is the
owner's actual complaint about the current output: *"当前输出的报告是大量facts和数据的堆砌，而非
满足人类报告的可读的水平"* — a pile of facts rather than a report a human wants to read.

Each question is therefore about **interpretation and shape of argument**, not formatting:

  Q1  Did the Executive Summary interpret anything at all?   binary — the summary carries ≥1
      `[DEDUCTED]` or `[VIEW]`. A summary of pure `[FACT]`s is a table with prose around it.
  Q2  Is the interpretation a real share of the work?        `[DEDUCTED]`+`[VIEW]` ≥ **10%** of all
      tagged findings. A single token inference in a document of facts is not analysis.
  Q3  Is the prose a data dump?                              fact-bearing lines ≤ **50%** of prose
      lines. Past half, the document is a fact table; the owner's words are "堆砌".
  Q4  Does it cite its own subject?                          every `/v/{ticker}/...` names the
      artifact's own ticker. A single-ticker artifact citing another issuer is either a
      copy-paste or a fabricated link, and no structural rule can see it because the URL is
      perfectly well-formed.

THE TWO NUMBERS THAT ARE CHOSEN RATHER THAN MEASURED, named as such: **10%** and **50%**. They are
stated here so the corpus rate can be read against them; if the corpus sits far from a bar, that is
a finding about the corpus OR about the bar, and the evidence file says which reading was taken.
Nothing else here is a threshold — Q1 and Q4 are binary.

**AMENDED AFTER THE FIRST READING, and the amendment is a SCOPE rule rather than a threshold.** The
questions above were registered first; running them over a second corpus then produced
`Q1: 0 of 206` and `Q2: 2 of 206`, which is not a finding about 206 artifacts — 204 of them carry no
`[FACT]`/`[DEDUCTED]`/`[VIEW]` tag anywhere and **none** carries an `## Executive Summary` heading,
because they are process artifacts (their headings are `## Sources`, `## Carry-forwards`, `## The
finding`) and not deliverables. A question that cannot be asked of an artifact must not be silently
answered "no", so each question declares whether it APPLIES and `None` is a third state reported as
`n/a`. **`check_output_quality.py`'s docstring had already recorded that this corpus measures 0 of 206
on Executive Summary because its element check matches headings** — this file re-derived that the hard
way, which is the mistake the note exists to prevent. The bars themselves were not moved.

WHAT IT CANNOT SEE, stated because an unreported gap reads as coverage: whether an inference is
CORRECT. Q1-Q3 say an interpretation happened and is not a token; they cannot say it is right.
That is the boundary where a human reads the artifact, and this script must not be described as
having judged quality when it has judged the presence of judgement.

THIN SAMPLES ARE REPORTED, NEVER SCORED (`T054`'s rule applied to artifacts). A skill class with
fewer than `MIN_N` artifacts reports its `n` and no rate — a percentage over two documents is a
percentage over two documents.

Usage:
    python3 scripts/check_output_rubric.py <artifact.md> [...] [--json] [--strict]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_output as lint          # noqa: E402 — FACT_RX / LINK_RX / split_frontmatter, one copy
import check_output_quality as qual  # noqa: E402 — `section`, one copy

#: The bar, in one place, so the evidence file and the code cannot drift.
INTERPRETATION_MIN_SHARE = 0.10   # Q2
FACT_LINE_MAX_SHARE = 0.50        # Q3
MIN_N = 3                         # below this, a class reports its n and no rate

_BADGE_ANY = re.compile(r"\[(?:FACT|DEDUCTED|VIEW)\]")
_BADGE_INFERRED = re.compile(r"\[(?:DEDUCTED|VIEW)\]")


def _prose_lines(body: str) -> list[str]:
    """Body lines that are prose — not headings, table rows or rules. The Q3 denominator."""
    return [l for l in body.splitlines()
            if l.strip() and not l.strip().startswith(("#", "|", "---"))]


def check(path: pathlib.Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    _fm, body, _fml = lint.split_frontmatter(raw)

    summary = qual.section(body, "Executive Summary") or ""
    all_badges = _BADGE_ANY.findall(body)
    inferred = _BADGE_INFERRED.findall(body)
    prose = _prose_lines(body)
    facts = [l for l in prose if lint.FACT_RX.search(l)]

    # Q4 needs the subject, and the subject is in the path: `<theses>/<N>/artifacts/<TICKER>/<file>`.
    ticker = path.parent.name if path.parent.name.isupper() else None
    cited = {m[0] for m in lint.LINK_RX.findall(body)}
    foreign = sorted(t for t in cited if ticker and t.upper() != ticker.upper())

    q1 = bool(_BADGE_INFERRED.search(summary))
    infer_share = len(inferred) / len(all_badges) if all_badges else 0.0
    fact_share = len(facts) / len(prose) if prose else 0.0

    # A QUESTION THAT CANNOT BE ASKED MUST NOT BE SILENTLY ANSWERED "NO" — and getting this wrong is
    # the defect this whole specification documents, committed here first: the initial version scored
    # every artifact on Q1 and Q2 whether or not it carried an Executive Summary or any tag at all.
    # Over the development workspace that produced "Q1: 0 of 206, Q2: 2 of 206", which reads as a
    # finding about 206 artifacts and is in fact a finding about 204 of them not being this kind of
    # document (no `## Executive Summary` heading anywhere; `[FACT]`/`[DEDUCTED]`/`[VIEW]` absent from
    # 204 of 206; their headings are `## Sources`, `## Carry-forwards`, `## The finding` — process
    # artifacts, not deliverables). `check_output_quality.py`'s own docstring had ALREADY recorded that
    # this corpus measures 0 of 206 on Executive Summary *because the element check matches headings*,
    # and that note exists so nobody re-derives it. The first version of this file re-derived it.
    #
    # So each question declares whether it APPLIES. `None` is a third state, reported as `n/a`, never
    # counted as a failure.
    applicable = {
        "Q1-summary-interprets": summary != "",
        "Q2-interpretation-share": bool(all_badges),
        "Q3-not-a-data-dump": bool(prose),
        # Q4 applies to any artifact that NAMES a subject. A single-ticker deliverable citing another
        # issuer is the case it is for; the development corpus's `_methodology.md` files cite five
        # issuers because that is what a comps methodology does, and they are flagged for reading
        # rather than failed (see the evidence file §3).
        "Q4-cites-own-subject": bool(ticker),
    }
    verdicts = {
        "Q1-summary-interprets": q1 if applicable["Q1-summary-interprets"] else None,
        "Q2-interpretation-share": (infer_share >= INTERPRETATION_MIN_SHARE)
                                   if applicable["Q2-interpretation-share"] else None,
        "Q3-not-a-data-dump": (fact_share <= FACT_LINE_MAX_SHARE)
                              if applicable["Q3-not-a-data-dump"] else None,
        "Q4-cites-own-subject": (not foreign) if applicable["Q4-cites-own-subject"] else None,
    }
    return {
        "artifact": str(path),
        "skill": path.stem.split("_", 2)[-1].split("_")[0],
        "affix": path.stem.split("_", 2)[-1].split("_", 1)[1] if path.stem.count("_") >= 3 else "",
        "ticker": ticker,
        "badges_total": len(all_badges),
        "badges_inferred": len(inferred),
        "interpretation_share": round(infer_share, 3),
        "exec_summary_interprets": q1,
        "has_exec_summary": bool(summary),
        "prose_lines": len(prose),
        "fact_lines": len(facts),
        "fact_line_share": round(fact_share, 3),
        "foreign_ticker_citations": foreign,
        "applicable": applicable,
        "verdicts": verdicts,
        "passed": sum(1 for v in verdicts.values() if v is True),
        "scored": sum(1 for v in verdicts.values() if v is not None),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any artifact passes fewer than all four")
    args = ap.parse_args(argv)

    rows = [check(pathlib.Path(p)) for p in args.artifacts]
    by_skill = collections.defaultdict(list)
    for r in rows:
        by_skill[r["skill"]].append(r)

    if args.json:
        print(json.dumps({"bar": {"interpretation_min_share": INTERPRETATION_MIN_SHARE,
                                  "fact_line_max_share": FACT_LINE_MAX_SHARE, "min_n": MIN_N},
                          "rows": rows,
                          "by_skill": {k: {"n": len(v),
                                           "mean_passed": round(sum(x["passed"] for x in v) / len(v), 2),
                                           "mean_scored": round(sum(x["scored"] for x in v) / len(v), 2)}
                                       for k, v in sorted(by_skill.items())}}, indent=2))
        return 0

    for rule in ("Q1-summary-interprets", "Q2-interpretation-share",
                 "Q3-not-a-data-dump", "Q4-cites-own-subject"):
        na = sum(1 for r in rows if r["verdicts"][rule] is None)
        passed = sum(1 for r in rows if r["verdicts"][rule] is True)
        print(f"{rule:26} {passed:>4} of {len(rows) - na:<4} scored   ({na} n/a)")
    print(f"\n{'skill':22} {'n':>3}  {'mean pass':>9}  {'of':>4}")
    for k, v in sorted(by_skill.items()):
        if len(v) < MIN_N:
            print(f"{k:22} {len(v):>3}  thin — reported with its n, never scored")
        else:
            print(f"{k:22} {len(v):>3}  {sum(x['passed'] for x in v) / len(v):>9.2f}  "
                  f"{sum(x['scored'] for x in v) / len(v):>4.1f}")
    print("\nThis rubric judges whether an INTERPRETATION HAPPENED and is not a token. "
          "It cannot judge whether the interpretation is CORRECT.")
    # `--strict` fails on a question that APPLIED and was not passed. An `n/a` is not a pass and not
    # a failure — it is a question that could not be asked of this artifact.
    return 1 if (args.strict and any(False in r["verdicts"].values() for r in rows)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
