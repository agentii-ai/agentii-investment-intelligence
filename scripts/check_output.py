#!/usr/bin/env python3
"""check_output.py — the structural lint for a single-skill artifact (spec 062 FR-034 iii, T082).

WHY THIS EXISTS. The nine `equity-research-core` skills already carry an `output format`, and it was
not being met. Measured 2026-09-24 over the held-out workspace's **50 artifacts**
(`B/agentii-physical-ai/theses/00{1,2,3}/artifacts/{TICKER}/*.md`, one per skill class):

    49 of 50 artifacts carry a duplicated trailing roll-up (`## Coverage Gaps & Citations` + a
       numbered list of `/v/` links) while ALSO carrying inline links — so the roll-up is duplication,
       not the only citation channel. **The first reading of this said 5–7**, because the pattern that
       looked for the links could not see the `page{N}` form (see `LINK_RX` below): one broken scanner
       moved the headline figure by 7×.
    1 artifact cites nothing inline in 1,756 words — density 0.0 against a floor of 1
       (`003-.../artifacts/PH/2026-09-17_1647_supply-chain_default.md`, the T082 red case: its only
       citations are in the frontmatter's machine list)
    28 of 50 artifacts carry at least one material-fact line with no link beside it
    corpus citation density: 0.0 – 8.77, median 6.24 — so the standard is not uniform

**The owner's requirement, in their words**: *"要求事实的后面有 agentii.ai/v 引用定位到页的链接（往往不需要
在最后再输出 citation list，人们更希望看到事实或者数据旁边紧挨着的位置的链接）"* — the link belongs BESIDE
the fact, and a trailing roll-up is what replaces that with a hop. So the roll-up is not merely
redundant, it is the shape the standard exists to reject.

WHAT IT CHECKS, AND WHAT IT DELIBERATELY DOES NOT.

  R1  frontmatter block present, and carrying the five pins
  R2  citation density ≥ 1 per 200 words of body
  R3  no duplicated trailing Citations roll-up
  R4  a line that states a MATERIAL FACT carries a link on that same line

  NOT checked: whether the links resolve, whether they are the *right* page, or whether the prose is any
  good. The first two need the network and the corpus; the third is `T083`'s rubric, and structure cannot
  see it. A lint that tried to judge quality would be the fifth blocking check wearing a rubric's clothes.

R4 IS THE ONE RULE THAT CAN FAIL A GOOD ARTIFACT, SO IT IS CALIBRATED AGAINST THE CORPUS, NOT GUESSED.
"Material fact" is a line carrying a **currency amount, a percentage, or a quoted span**; "beside" is the
same line or **one line either side** (the owner's word is *"紧挨着"*, and the first version read it as
same-line-only, which flagged 41 of 50). Three line classes are excluded by name because they
legitimately have no source — derived lines (`[DEDUCTED]`/`[VIEW]`), coverage-gap statements ("No X
disclosure"), and methodology notes ("Structured verification:"). **Measured in both directions before
this shipped**: it fires on 28 of 50 in the corpus as it stands, and those 28 are the T084 backlog rather
than a false-positive set — which is why this lint ships **advisory** and only gates under `--strict`.

ADVISORY BY DEFAULT, `--strict` TO GATE. The default run reports and exits 0; `--strict` exits 1 on a
finding. That is `FR-050`'s split applied to a second surface: a defect is wrong at any size, a
below-standard artifact may be a shorter document. **T082's red case is the first artifact listed under
`--strict` in the evidence run**, which is what makes this a test rather than a preference.

Usage:
    python3 scripts/check_output.py <artifact.md> [more.md ...] [--json] [--strict] [--min-density 1.0]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

#: The five pins every output artifact must declare (spec 046; they are universal — 206 of 206).
REQUIRED_PINS = ("as_of", "constitution_pin", "assumption_pin", "corpus_version", "skill_pin")

#: A trailing roll-up: a heading naming citations whose section is a list of /v/ links. The standard
#: rejects it because the link belongs beside the fact; the list is the shape that replaces proximity.
ROLLUP_RX = re.compile(r"(?im)^#{1,6}\s*[^\n]*citations[^\n]*$")
#: ⚠️ BOTH LINK FORMS EXIST IN THE CORPUS, AND MATCHING ONE OF THEM COST ME A FALSE 96% FAILURE RATE.
#: Measured over the held-out workspace 2026-09-24: **2,244** citations use the bare `/{N}` tail
#: (`agentii.ai/v/AMZN/sec131/23`) and **948** use `/page{N}` (`agentii.ai/v/ISRG/sec166/page77`). The
#: first version of this pattern accepted only the bare form, so it read every `page{N}` citation as
#: absent — 21 artifacts failed the density rule and 46 failed the proximity rule, against a corpus whose
#: real density floor is 3.2. **This is the defect this specification documents most often**: a scanner
#: that finds nothing because it looks for the wrong shape, reporting a confident wrong number. The
#: `(?:page)?` and the trailing `\\b` are both load-bearing: without the group, 948 real citations are
#: invisible; without the boundary, a sentence-ending period is captured into the page number.
LINK_RX = re.compile(r"agentii\.ai/v/([A-Za-z0-9.\-]+)/([A-Za-z0-9_\-]+)/(?:page)?(\d+)\b")

#: A MATERIAL FACT, narrowed to the three forms the standard's own examples use. Deliberately not
#: "a line with any digit" — that would fire on section numbering, years and metric names, and a rule
#: that fires on those is a rule that gets turned off.
FACT_RX = re.compile(
    r"[$€£¥]\s?\d"                      # a currency amount
    r"|\b\d+(?:\.\d+)?\s?%"             # a percentage
    r"|“[^”]{15,}”"      # a quoted span (the filing's own words)
    r"|\"[^\"\n]{15,}\""                # the same, with straight quotes
)


def _split(text: str) -> tuple[str, str, list[str]]:
    """(frontmatter, body, frontmatter lines). A file without `---` has an empty frontmatter."""
    if not text.startswith("---"):
        return "", text, []
    end = text.find("\n---", 3)
    if end == -1:
        return "", text, []
    fm = text[3:end]
    return fm, text[end + 4:], fm.splitlines()


def check(path: pathlib.Path, min_density: float = 1.0) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    fm, body, fm_lines = _split(raw)
    findings: list[dict] = []

    # R1 — the frontmatter block and its pins.
    if not fm:
        findings.append({"rule": "R1-frontmatter", "detail": "no `---` frontmatter block"})
    else:
        missing = [p for p in REQUIRED_PINS if not re.search(rf"(?m)^{p}\s*:", fm)]
        if missing:
            findings.append({"rule": "R1-pins", "detail": f"missing pin(s): {', '.join(missing)}"})

    # R2 — citation density. Counted on the BODY: frontmatter links are the machine list, not the
    # proximity the standard asks for, and counting them would let a roll-up satisfy a density rule.
    words = len(re.findall(r"\S+", re.sub(r"<[^>]+>", " ", body)))
    links = len(LINK_RX.findall(body))
    density = links / (words / 200) if words else 0.0
    if density < min_density:
        findings.append({
            "rule": "R2-density",
            "detail": f"{density:.2f} citations per 200 words ({links} in {words} words) — floor {min_density}",
        })

    # R3 — the duplicated roll-up, detected STRUCTURALLY: a standalone block of consecutive
    # citation-only lines. The first version keyed on a heading matching /citations/, which missed the
    # roll-ups that sit under a differently-named heading — measured: `AMZN/supply-chain` carries a
    # numbered 6-line block of `/v/` links under a heading the pattern did not match. What the standard
    # rejects is a citation LIST standing alone, whatever it is called.
    run = 0
    rollup_at = None
    for i, line in enumerate(body.splitlines()):
        s_ = line.strip()
        # A CITATION-ONLY LINE, and the precision here is the whole rule: the line must be a LIST ITEM
        # THAT BEGINS WITH THE LINK. Consecutive prose lines that each carry an inline link are what the
        # standard WANTS, and the first version of this detector flagged them — it reported all 50
        # artifacts, which is the failure mode this repository names ("a gate that fails good pages gets
        # disabled"). What marks a roll-up is that the link IS the line: a marker, then a URL, then a
        # gloss. Anything with prose in front of the link is a citation in its right place.
        is_cite = bool(re.match(r"^\s*(?:[-*+]|\d+[.)])\s*\[?https?://", s_))
        run = run + 1 if is_cite else 0
        if run >= 3:
            rollup_at = i - run + 1
            break
    heading_hit = ROLLUP_RX.search(body)
    if rollup_at is not None or heading_hit:
        where = f"a {run}-line citation block" if rollup_at is not None else "a heading named Citations"
        findings.append({"rule": "R3-rollup", "detail": f"duplicated roll-up: {where} stands alone instead of the link sitting beside the fact"})

    # R4 — a material fact must carry a link BESIDE it. "Beside" is the owner's own word
    # (*"紧挨着的位置"*), and the first version of this rule read it as "on the same line", which is
    # stricter than the standard: an artifact that cites on the line beneath is citing beside the fact.
    # One line of tolerance, in both directions, and no more — a link two paragraphs away is a roll-up
    # in disguise, and the roll-up is exactly what R3 rejects.
    lines = body.splitlines()
    bare: list[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("---"):
            continue                       # headings, tables and rules are checked elsewhere / not prose
        if not FACT_RX.search(s):
            continue
        # THREE LINE CLASSES LEGITIMATELY CARRY NO SOURCE, and the first version flagged all three —
        # measured on the corpus, its hits were dominated by them. A rule that fires on these is the
        # "gate that fails good pages" this programme keeps warning about, so they are excluded by name:
        #   · derived lines (`[DEDUCTED]` / `[VIEW]`) — the platform's own reasoning, sourced from other
        #     lines, not from a page;
        #   · coverage-gap lines ("No X disclosure", "not disclosed", "unavailable") — a statement that
        #     the source does NOT say something has no page to cite, by construction;
        #   · methodology lines (`Structured verification:`, `Keyword scan`) — a description of how the
        #     search was done.
        if re.match(r"\s*[-*\d.\s]*(\[(DEDUCTED|VIEW|INFERENCE)\])", s):
            continue
        # A gap line is a NEGATION plus a source-verb ANYWHERE on the line, not within one sentence:
        # the real lines read "**No BOM or per-system cost stack.** The issuer discloses product margin
        # only", and a sentence-bounded window stops at that first period and misses `discloses`.
        if (re.search(r"(?i)\b(no|not|none|never|without|absent|unavailable|gap|omit)\b", s)
                and re.search(r"(?i)(disclos|discoverab|availab|reported|stated|found|present|filed|broken out)", s)):
            continue
        if re.search(r"(?i)^(structured verification|keyword scan|methodology|method)\b", s) or "Structured verification:" in s:
            continue
        window = " ".join(lines[max(0, i - 1):i + 2])
        if not LINK_RX.search(window):
            bare.append(f"L{i + 1}: {s[:90]}")
    if bare:
        findings.append({
            "rule": "R4-bare-fact",
            "detail": f"{len(bare)} material-fact line(s) carry no link beside them",
            "lines": bare[:5],
        })

    return {
        "artifact": str(path),
        "words": words,
        "links": links,
        "density_per_200w": round(density, 2),
        "findings": findings,
        "verdict": "PASS" if not findings else "FINDINGS",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on a finding; the default reports and exits 0")
    ap.add_argument("--min-density", type=float, default=1.0)
    args = ap.parse_args(argv)

    results = [check(pathlib.Path(p), args.min_density) for p in args.artifacts]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            mark = "PASS" if r["verdict"] == "PASS" else "FINDINGS"
            print(f"{mark:9} {r['density_per_200w']:>6}/200w  {r['artifact']}")
            for f in r["findings"]:
                print(f"            {f['rule']}: {f['detail']}")
                for ln in f.get("lines", []):
                    print(f"              · {ln}")
        fired = sum(1 for r in results if r["verdict"] != "PASS")
        print(f"\n{len(results)} artifact(s), {fired} with findings. "
              f"This lint judges STRUCTURE only — it cannot see whether the prose is any good (T083).")

    return 1 if (args.strict and any(r["verdict"] != "PASS" for r in results)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
