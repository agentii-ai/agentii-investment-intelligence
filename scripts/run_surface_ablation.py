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


MCP_ENDPOINT = os.environ.get("AGENTII_MCP_ENDPOINT", "https://mcp.agentii.ai/mcp")


def fetch_context(tag_axis: str, tag: str, page_size: int = 6) -> dict:
    """The surface's own answer, fetched live. `(axis, tag)` → the payload `_context_block` consumes.

    CALLED OVER THE MCP ENDPOINT because the v1 REST route is not usable with the key that was on hand:
    `agentii-investment-intelligence/.env.local` answers `401 INVALID_API_KEY` ("Invalid or inactive")
    while a key-less request answers a DIFFERENT code, `API_KEY_REQUIRED` — so the server sees a key and
    rejects it. **Measured 2026-09-25: there are TWO keys and the file holds the dead one.** The
    environment's `AGENTII_API_KEY` is a *different* value (51 chars vs 56) and it works — v1 returns 200
    with data, and the MCP endpoint accepts it. So this reads the credential from the ENVIRONMENT and
    never from that file; `_load_env` uses `setdefault`, so a real environment value is never overwritten.

    **The first version of this function looked like it worked and did not**: a curl probe printed the
    SSE envelope and I read `data: {"jsonrpc"...` as success, when the payload inside was
    `{"error":{"code":"API_KEY_REQUIRED"}}`. The error was nested one level below what I looked at.

    The response is SSE-framed (`data: {...}`) and nests its payload as a JSON string inside
    `result.content[0].text`; both layers are unwrapped here rather than by the caller, **and the
    unwrapped payload is checked for an `error` key** so a refusal cannot be mistaken for an answer.
    """
    import urllib.request
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": "search_by_analogue",
                                  "arguments": {tag_axis: tag, "page_size": page_size}}}).encode()
    headers = {"content-type": "application/json", "accept": "application/json, text/event-stream"}
    key = os.environ.get("AGENTII_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(MCP_ENDPOINT, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode("utf-8", "replace")
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:].strip()
            break
    payload = json.loads(json.loads(raw)["result"]["content"][0]["text"])
    if "error" in payload:
        raise RuntimeError(f"the surface refused: {payload['error']} — NOT an empty result. "
                           f"A refusal read as a result is the defect this whole spec is about.")
    payload["_fetched"] = {"axis": tag_axis, "tag": tag, "page_size": page_size,
                           "endpoint": MCP_ENDPOINT, "when": "2026-09-25"}
    return payload


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
    ap.add_argument("--context", type=pathlib.Path, default=None,
                    help="a frozen context file; omit it and pass --fetch-tag to fetch live")
    ap.add_argument("--fetch-tag", default=None, metavar="AXIS=VALUE",
                    help="fetch the surface live, e.g. event_type=earnings-miss")
    ap.add_argument("--context-out", type=pathlib.Path, default=None,
                    help="write the fetched payload here, so the run is re-runnable from it")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--model", default=os.environ.get("ABLATION_MODEL", "deepseek/deepseek-chat"))
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--env", type=pathlib.Path,
                    default=pathlib.Path("/Users/frank/A/agenzym/packages/data-pipeline/.env.local"))
    ap.add_argument("--limit", type=int, default=0, help="stop after N questions (smoke test)")
    ap.add_argument("--questions", type=pathlib.Path, default=None,
                    help="a JSON list of {mode, ticker, question} to use instead of the generic form")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the WITHOUT arm only, to measure which questions discriminate")
    args = ap.parse_args(argv)

    _load_env(args.env)
    if args.context:
        ctx = json.loads(args.context.read_text())
    elif args.fetch_tag:
        axis, _, value = args.fetch_tag.partition("=")
        ctx = fetch_context(axis, value)
        if args.context_out:
            args.context_out.write_text(json.dumps(ctx, indent=2))
    else:
        print("ERROR: pass --context (frozen) or --fetch-tag AXIS=VALUE (live)", file=sys.stderr)
        return 2
    block = _context_block(ctx)

    rows = []
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ablation-"))
    if args.questions:
        # Accepts a bare list AND `{"questions": [...]}` — the evidence file carries its own provenance
        # alongside the list, and a loader that only understood the bare form would make the provenance
        # impossible to keep next to what it describes.
        qd = json.loads(args.questions.read_text())
        qlist = qd["questions"] if isinstance(qd, dict) else qd
        qs = [(q["mode"], q["ticker"], q["question"]) for q in qlist]
    else:
        qs = [(m, t, f"You are answering the `{m}` question for {t} as an equity analyst. "
                      f"Produce the deliverable for that question class.")
              for m in args.modes for t in args.tickers]
    if args.limit:
        qs = qs[:args.limit]
    arms = ("without",) if args.calibrate else ("without", "with")

    for i, (mode, ticker, question) in enumerate(qs, 1):
        system = f"You are an equity research analyst. {SHAPE}"
        r = {"skill": args.skill, "mode": mode, "ticker": ticker, "question": question, "arms": {}}
        for arm in arms:
            ans, usage = _ask(args.model, args.temperature, system,
                              question + "\n\n" + (block if arm == "with" else ""))
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
        if not args.calibrate:
            r["delta"] = r["arms"]["with"]["passed"] - r["arms"]["without"]["passed"]
            r["token_delta"] = (r["arms"]["with"]["usage"]["total_tokens"]
                                - r["arms"]["without"]["usage"]["total_tokens"])
        rows.append(r)
        w = r["arms"]["without"]
        tail = (f"delta {r['delta']:+d}" if not args.calibrate
                else f"failed rules: {sum(1 for v in w['verdicts'].values() if v is False)}")
        print(f"[{i}/{len(qs)}] {mode} · {ticker}: without {w['passed']}/{w['scored']} · {tail}",
              flush=True)

    out = {
        "bar": {"registered": "2026-09-25, before the run; erc-surface-ablation.md 1a",
                "instrument": f"one completion per arm, {args.model}, temperature={args.temperature}",
                "tie_rule": "a tie is INCONCLUSIVE, not a rejection — the stronger instrument has not run",
                "scoring": "check_output_rubric.py (T083), four verdicts reported per arm"},
        "skill": args.skill, "n_questions": len(rows),
        "mode": "calibrate (without arm only)" if args.calibrate else "ablation (both arms)",
        "arms": {a: {"mean_passed": round(sum(r["arms"][a]["passed"] for r in rows) / len(rows), 2),
                     "total_tokens": sum(r["arms"][a]["usage"]["total_tokens"] for r in rows)}
                 for a in arms},
        "rows": rows,
    }
    if args.calibrate:
        # CALIBRATION IS NOT A VERDICT, and the output must not look like one. It measures whether a
        # question can tell the arms apart at all: a question the without-arm passes on every rule has
        # no room to show an effect, so a tie on it says nothing about the surface. Which is the whole
        # reason this mode exists — the first run's 20-of-21 ties were partly a property of the
        # questions, not of the surface.
        discrim = [r for r in rows
                   if any(v is False for v in r["arms"]["without"]["verdicts"].values())]
        out["calibration"] = {"n": len(rows), "discriminating": len(discrim),
                              "flat": len(rows) - len(discrim),
                              # The QUESTION TEXT is in here because `(mode, ticker)` is not unique — the
                              # three framings share a pair. Its absence is what let the first selector
                              # pull six controls in with five findings: a caller could not tell the
                              # discriminating question from its siblings.
                              "discriminating_questions": [
                                  {"mode": r["mode"], "ticker": r["ticker"], "question": r["question"],
                                   "failed": [k for k, v in r["arms"]["without"]["verdicts"].items()
                                              if v is False]}
                                  for r in discrim]}
        args.out.write_text(json.dumps(out, indent=2))
        print(f"\n{len(rows)} questions: {len(discrim)} discriminate (the without-arm fails ≥1 rule), "
              f"{len(rows) - len(discrim)} are flat.\n"
              f"**A flat question cannot show an effect** — a tie on it is about the question, not the "
              f"surface.\nwrote {args.out}")
        return 0

    deltas = [r["delta"] for r in rows]
    out["delta"] = {"mean": round(sum(deltas) / len(deltas), 3), "n": len(deltas),
                    "with_better": sum(1 for d in deltas if d > 0),
                    "tie": sum(1 for d in deltas if d == 0),
                    "with_worse": sum(1 for d in deltas if d < 0)}
    args.out.write_text(json.dumps(out, indent=2))
    print(f"\nn={len(rows)}  mean delta {out['delta']['mean']:+.3f}  "
          f"(better {out['delta']['with_better']} · tie {out['delta']['tie']} · "
          f"worse {out['delta']['with_worse']})\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
