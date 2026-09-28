#!/usr/bin/env python3
"""run_surface_ablation_sweep.py — `T080` part (ii) across the eight remaining ERC skills.

WHY A SWEEP AND NOT EIGHT RUNS BY HAND. The `turnaround` result came from a method — write candidates at
three analytical framings, CALIBRATE for headroom, then ablate on what moves — and a method applied by
hand eight times is eight chances to change it. This drives that method per skill, through the same
functions `run_surface_ablation.py` uses, so there is one implementation.

THE SELECTION FILTER IS FIXED HERE, and the fix is stated because the first one had a bug: `turnaround`'s
filter matched on the `(mode, ticker)` PAIR, so the `A-describe` controls sharing a pair came in with the
discriminating questions. This one matches on the **exact question text**.

THE TAG MAPPING IS A CHOICE, NOT A MEASUREMENT, and every row carries which kind it is:

  own-name  the skill's own name is the tag (only `turnaround`)
  inferred  the skill's declared modes name the situation closely
  weak      no mode carries situation semantics; the tag is the closest available

**The distinction is what makes a result readable.** A `weak` row's outcome holds *for that tag*, and must
not be read as "this skill does or does not need the surface" — the tag was picked for it.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_surface_ablation as abl  # noqa: E402 — one implementation

EVIDENCE = pathlib.Path("/Users/frank/A/agenzym/specs/062-page-retrieval-evaluation/evidence")
TICKERS = ["AMZN", "AMBA", "CGNX", "ISRG", "NVDA", "PH", "SPCX"]

#: `skill -> (axis, tag, choice_kind, modes, tickers)`. The modes are the skills' own `essentials_modes`.
SKILLS = {
    "growth-strategy": ("company_situation", "compounder", "inferred",
                        ["growth-strategy-assessment", "organic-growth-drivers-analysis",
                         "organic-growth-driver-execution-assessment"], ["AMZN", "NVDA", "ISRG"]),
    "recent-quarter": ("event_type", "earnings-miss", "inferred",
                       ["consolidated-p-and-l", "margin-analysis", "earnings-vs-consensus"],
                       ["AMZN", "NVDA", "CGNX"]),
    "risk": ("event_type", "regulatory-shock", "inferred",
             ["general-risk-factors-identification-assessment", "technology-disruption-risk-analysis",
              "regulatory-compliance-risk-assessment"], ["PH", "ISRG", "SPCX"]),
    "valuation-methods": ("company_situation", "undervalued", "inferred",
                          ["analyst-valuation-methods-comparison", "comprehensive-valuation-summary-analysis",
                           "valuation-assumptions-extraction"], ["AMZN", "PH", "NVDA"]),
    "business-model": ("company_situation", "pricing-power", "weak",
                       ["business-model-classification", "distribution-channel-analysis",
                        "revenue-composition-and-concentration"], ["AMZN", "NVDA", "CGNX"]),
    "competitive": ("company_situation", "pricing-power", "weak",
                    ["direct-competitor-identification-and-analysis", "market-share-dynamics-analysis",
                     "market-share-evolution-and-competitive-benchmarking"], ["NVDA", "ISRG", "SPCX"]),
    "secular-trends": ("event_type", "sector-rotation", "weak",
                       ["evaluate-company-s-exposure-to-major-secular-technology-trends",
                        "deep-dive-ai-trend-assessment-for-companies-with-identified-ai-exposure",
                        "deep-dive-data-value-trend-assessment-for-companies-with-identified-data-exposure"],
                       ["AMZN", "NVDA", "AMBA"]),
    "earnings-sentiment": ("event_type", "earnings-miss", "weak",
                           ["analyst-sentiment-assessment-current-quarter", "fy0-analyst-estimates-extraction",
                            "current-quarter-fiscal-year-analyst-estimates"], ["AMZN", "CGNX", "NVDA"]),
}

#: THE FRAMINGS, AND WHICH ONE CARRIES THE INSTRUMENT. Measured over 27 candidate questions across the
#: nine skills, 2026-09-25 — headroom, i.e. how often the without-arm failed at least one rule:
#:
#:     A-describe     0 of 27   (0%)   INERT — it never once produced a question the rubric could act on
#:     B-verdict     14 of 24  (58%)   the discriminating framing
#:     C-disconfirm   1 of 24   (4%)   almost never fires, despite being the stricter ask
#:
#: So the sweep's first pass used two framings that cannot discriminate out of three, gave each mode
#: exactly ONE live question, and then reported five skills as unscoreable. **That thinness was partly the
#: question set's composition, not the skills'.** `FRAMINGS_SWEEP` is the corrected set: `B-verdict` only,
#: varied across tickers so a mode yields n>=3.
FRAMINGS = {
    "A-describe": "You are answering the `{mode}` question for {ticker} as an equity analyst. Produce the "
                  "deliverable for that question class.",
    "B-verdict": "For {ticker}, answer the `{mode}` question as something only a judgement can settle — "
                 "make the call the mode names, and defend it against the other reading.",
    "C-disconfirm": "For {ticker}, answer the `{mode}` question by stating the reading the evidence best "
                    "supports, then setting out what would have to be true for that reading to be WRONG, "
                    "and whether any of it is already observable.",
}
#: The corrected sweep set. `C-disconfirm` is dropped as well as `A-describe`: 1 of 24 is not a framing
#: worth spending a third of every mode's budget on, and keeping it would re-introduce the dilution this
#: exists to remove. It stays in `FRAMINGS` because the finding above is *about* it.
FRAMINGS_SWEEP = {"B-verdict": FRAMINGS["B-verdict"]}


def candidates(skill: str, modes: list[str], tickers: list[str],
               framings: dict | None = None) -> list[dict]:
    """One question per (mode, ticker, framing). The CROSS of tickers is what buys `n>=3` per mode."""
    framings = framings or FRAMINGS_SWEEP
    out = []
    for mode in modes:
        for ticker in tickers:
            for framing, tmpl in framings.items():
                out.append({"mode": mode, "ticker": ticker, "framing": framing,
                            "question": tmpl.format(mode=mode, ticker=ticker)})
    return out


def main() -> int:
    results = {}
    for skill, (axis, tag, kind, modes, tickers) in SKILLS.items():
        print(f"\n=== {skill}  ({axis}={tag}, {kind}) ===", flush=True)
        # `V2` SUFFIX: the first sweep's files are referenced by the evidence and must not be
        # overwritten. Re-running a measurement must not erase the one it corrects.
        #
        # AND THE SAME RULE APPLIES TO REPLICATES. Hardening a single-run result means running it again
        # with the SAME questions and the SAME frozen context and letting only the draw differ — so each
        # replicate needs its own suffix or the second run erases the first and the "hardening" is one
        # run wearing three names.
        V2 = sys.argv[1] if len(sys.argv) > 1 else "-b2"
        ctx_path = EVIDENCE / f"erc-surface-ablation-context-{skill}.json"
        if ctx_path.is_file():
            ctx = json.loads(ctx_path.read_text())      # reuse: the surface has not changed
        else:
            ctx = abl.fetch_context(axis, tag, page_size=6)
            ctx_path.write_text(json.dumps(ctx, indent=2))
        cpath = EVIDENCE / f"erc-surface-ablation-candidates-{skill}{V2}.json"
        cpath.write_text(json.dumps({
            "_provenance": {"skill": skill, "tag_axis": axis, "tag": tag, "choice_kind": kind,
                            "modes_source": f"{skill}/SKILL.md, `essentials_modes`",
                            "framings": FRAMINGS, "registered": "2026-09-25, before the run"},
            "_integrity_constraint":
                "No question mentions the rubric or tells the model how to satisfy a rule. What varies is "
                "how much the question ITSELF forces a judgement. A set written to fail the without-arm "
                "would manufacture the result it claims to measure.",
            "questions": candidates(skill, modes, tickers)}, indent=2))

        # 1. calibrate (without arm only)
        cal_path = EVIDENCE / f"erc-surface-ablation-calibration-{skill}{V2}.json"
        abl.main(["--skill", skill, "--modes", "x", "--tickers", tickers[0], "--calibrate",
                  "--questions", str(cpath), "--context", str(ctx_path), "--out", str(cal_path)])
        cal = json.loads(cal_path.read_text())
        # Match on the EXACT QUESTION TEXT. `turnaround`'s selector matched on the `(mode, ticker)` PAIR,
        # which the three framings share — so six controls came in with five findings. The calibration
        # payload now carries the question for exactly this reason.
        wanted = {d["question"] for d in cal["calibration"]["discriminating_questions"]}
        src = json.loads(cpath.read_text())
        keep_qs = [q for q in src["questions"] if q["question"] in wanted]
        assert len(keep_qs) == len(wanted), (
            f"{skill}: {len(wanted)} discriminating questions but {len(keep_qs)} matched — the "
            f"calibration's question text does not appear in the candidate file")
        sel_path = EVIDENCE / f"erc-surface-ablation-selected-{skill}{V2}.json"
        sel_path.write_text(json.dumps({**src, "questions": keep_qs,
                                        "_selection": {"rule": "the without-arm failed >=1 rule in the "
                                                               "calibration sample",
                                                       "matched_on": "exact question text",
                                                       "n": len(keep_qs),
                                                       "weakness": "ONE sample; the without-arm is "
                                                                   "re-drawn and temperature=0 does not "
                                                                   "make DeepSeek reproducible"}},
                                       indent=2))
        print(f"    calibrated: {len(keep_qs)} of {len(src['questions'])} have headroom", flush=True)
        if len(keep_qs) < 3:
            print(f"    THIN (n={len(keep_qs)}) — reported with its n, never scored", flush=True)
            results[skill] = {"choice_kind": kind, "tag": f"{axis}={tag}", "n": len(keep_qs), "thin": True}
            continue

        # 2. ablate on them
        out_path = EVIDENCE / f"erc-surface-ablation-{skill}{V2}.json"
        abl.main(["--skill", skill, "--modes", "x", "--tickers", tickers[0],
                  "--questions", str(sel_path), "--context", str(ctx_path), "--out", str(out_path)])
        d = json.loads(out_path.read_text())
        results[skill] = {"choice_kind": kind, "tag": f"{axis}={tag}", "n": d["delta"]["n"],
                          "delta": d["delta"], "arms": d["arms"], "thin": False}

    (EVIDENCE / f"erc-surface-ablation-sweep{V2}.json").write_text(json.dumps(results, indent=2))
    print("\n=== sweep ===")
    for s, r in results.items():
        if r.get("thin"):
            print(f"  {s:20} {r['choice_kind']:8} n={r['n']}  THIN")
        else:
            d = r["delta"]
            print(f"  {s:20} {r['choice_kind']:8} n={d['n']:>2}  "
                  f"+{d['with_better']} · ={d['tie']} · -{d['with_worse']}  mean {d['mean']:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
