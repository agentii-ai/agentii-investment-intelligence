#!/usr/bin/env python3
"""run_surface_ablation.py — `T080` part (ii): the question class, with and without a knowledge surface.

THE INSTRUMENT IS THE AMENDED ONE, and it is weaker than the bar's first version. The bar named an
agent-loop run — the skill's question class with the surface *available in its tool set*. What runs here
is **one completion per arm**, the case context injected or withheld. The amendment is registered in
`specs/062-page-retrieval-evaluation/evidence/erc-surface-ablation.md` §1a **before** this script ran,
because substituting a weaker instrument behind a stronger bar is the thing `FR-016` exists to prevent.

WHAT IT DOES NOT MEASURE: retrieval. The case context is a FROZEN file, identical for every question, so
a difference between arms is the *content's* effect and says nothing about whether the surface retrieves
the right thing.

THE TIE RULE IS PRE-DECLARED (same section): at this fidelity a **tie is INCONCLUSIVE, not a rejection**,
because the stronger instrument has not run. Only the with-surface arm scoring **strictly worse** is a
failure.

SCORING is `T083`'s rubric — the term "answer quality" was registered before the run and is not chosen
here. The rubric's `Q4` needs the artifact to cite its own subject and `R2` needs real `/v/` links; a
model given a question and no filing cannot produce either, so those two are reported **per arm** and a
uniform failure across both arms is stated rather than read as a result.

Usage:
    python3 scripts/run_surface_ablation.py --skill turnaround \
        --modes performance-stagnation-detection-and-classification ... \
        --tickers AMZN AMBA CGNX ISRG NVDA PH SPCX \
        --context ../../specs/062-page-retrieval-evaluation/evidence/erc-surface-ablation-context.json \
        --out ../../specs/062-page-retrieval-evaluation/evidence/erc-surface-ablation.json
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_output_rubric as rubric  # noqa: E402 — T083's instrument, one copy

#: The deliverable's declared shape, requested in the prompt so the rubric has something to score. This
#: is the nine skills' `## Output Structure`, not an invention of this script.
SHAPE = """Write the answer as a markdown report with EXACTLY this structure:
---
as_of: <ISO date>
constitution_pin: <string>
assumption_pin: <string>
corpus_version: <string>
skill_pin: <string>
---

## Executive Summary
<= 200 words.

## Analysis
The analysis, tagging every finding `[FACT]`, `[DEDUCTED]` or `[VIEW]`.
"""


def _load_env(path: pathlib.Path) -> None:
    if not path.is_file():
        return
    for ln in path.read_text(errors="ignore").splitlines():
        if "=" in ln and not ln.strip().startswith("#"):
            k, v = ln.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _ask(model: str, temperature: float, system: str, user: str) -> tuple[str, dict]:
    """`(answer, usage)`. Usage comes from the client that produced the answer — never estimated."""
    import litellm
    litellm.suppress_debug_info = True
    r = litellm.completion(model=model, messages=[{"role": "system", "content": system},
                                                  {"role": "user", "content": user}],
                           temperature=temperature, max_tokens=2000)
    u = r.usage
    return (r.choices[0].message.content or ""), {"prompt_tokens": u.prompt_tokens,
                                                  "completion_tokens": u.completion_tokens,
                                                  "total_tokens": u.total_tokens}


def _context_block(ctx: dict) -> str:
    keep = ("case_id", "title", "provenance", "analogue_tags", "tickers_referenced",
            "case_summary", "result_headline", "when_to_recall")
    cases = [{k: c.get(k) for k in keep} for c in ctx["cases"]]
    strats = ctx.get("strategies_returned_by_the_same_call", [])
    return ("## Case precedents and strategies retrieved for this situation\n\n"
            "```json\n" + json.dumps({"cases": cases, "strategies": strats}, indent=1) + "\n```\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--modes", nargs="+", required=True)
    ap.add_argument("--tickers", nargs="+", required=True)
    ap.add_argument("--context", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--model", default=os.environ.get("ABLATION_MODEL", "deepseek/deepseek-chat"))
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--env", type=pathlib.Path,
                    default=pathlib.Path("/Users/frank/A/agenzym/packages/data-pipeline/.env.local"))
    ap.add_argument("--limit", type=int, default=0, help="stop after N questions (smoke test)")
    args = ap.parse_args(argv)

    _load_env(args.env)
    ctx = json.loads(args.context.read_text())
    block = _context_block(ctx)

    rows = []
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ablation-"))
    qs = [(m, t) for m in args.modes for t in args.tickers]
    if args.limit:
        qs = qs[:args.limit]

    for i, (mode, ticker) in enumerate(qs, 1):
        question = (f"You are answering the `{mode}` question for {ticker} as an equity analyst. "
                    f"Produce the deliverable for that question class.")
        system = f"You are an equity research analyst. {SHAPE}"
        r = {"skill": args.skill, "mode": mode, "ticker": ticker, "question": question, "arms": {}}
        for arm, extra in (("without", ""), ("with", block)):
            ans, usage = _ask(args.model, args.temperature, system, question + "\n\n" + extra)
            # The rubric reads the subject from the path, so the artifact must sit in artifacts/<TICKER>/.
            d = tmp / arm / "theses" / "001" / "artifacts" / ticker
            d.mkdir(parents=True, exist_ok=True)
            p = d / f"2026-09-25_1200_{args.skill}_{mode}.md"
            p.write_text(ans, encoding="utf-8")
            sc = rubric.check(p)
            r["arms"][arm] = {"usage": usage, "verdicts": sc["verdicts"],
                              "passed": sc["passed"], "scored": sc["scored"],
                              "fact_line_share": sc["fact_line_share"],
                              "interpretation_share": sc["interpretation_share"]}
        r["delta"] = r["arms"]["with"]["passed"] - r["arms"]["without"]["passed"]
        r["token_delta"] = (r["arms"]["with"]["usage"]["total_tokens"]
                            - r["arms"]["without"]["usage"]["total_tokens"])
        rows.append(r)
        print(f"[{i}/{len(qs)}] {mode} · {ticker}: "
              f"without {r['arms']['without']['passed']}/{r['arms']['without']['scored']} · "
              f"with {r['arms']['with']['passed']}/{r['arms']['with']['scored']} · "
              f"delta {r['delta']:+d}", flush=True)

    deltas = [r["delta"] for r in rows]
    out = {
        "bar": {"registered": "2026-09-25, before the run; erc-surface-ablation.md 1a",
                "instrument": f"one completion per arm, {args.model}, temperature={args.temperature}",
                "tie_rule": "a tie is INCONCLUSIVE, not a rejection — the stronger instrument has not run",
                "scoring": "check_output_rubric.py (T083), four verdicts reported per arm"},
        "skill": args.skill, "n_questions": len(rows),
        "arms": {a: {"mean_passed": round(sum(r["arms"][a]["passed"] for r in rows) / len(rows), 2),
                     "total_tokens": sum(r["arms"][a]["usage"]["total_tokens"] for r in rows)}
                 for a in ("without", "with")},
        "delta": {"mean": round(sum(deltas) / len(deltas), 3), "n": len(deltas),
                  "with_better": sum(1 for d in deltas if d > 0),
                  "tie": sum(1 for d in deltas if d == 0),
                  "with_worse": sum(1 for d in deltas if d < 0)},
        "rows": rows,
    }
    args.out.write_text(json.dumps(out, indent=2))
    print(f"\nn={len(rows)}  mean delta {out['delta']['mean']:+.3f}  "
          f"(better {out['delta']['with_better']} · tie {out['delta']['tie']} · "
          f"worse {out['delta']['with_worse']})\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
