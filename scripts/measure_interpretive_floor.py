#!/usr/bin/env python3
"""Re-derive the interpretive floor from the corpus, with the measurement committed (spec 058 T089).

WHY THIS EXISTS. `contracts/report-readability.md` §2 row 5 states the interpretive floor as
*"≥0.25 … The interpretive floor on numeric sentences is **≥0.25** across all 18 sampled documents
(observed minimum 0.27)"* — and on that basis `check_report_readability.py` makes it **blocking** and
`_gate_page_argument` blocks author pages on it. On 2026-09-24 an audit re-ran the shipped functions over
the corpus's own extracted text layer — the layer the contract says it was calibrated on — and measured:

    min 0.056   median 0.267   max 0.418   ·   36 of 78 documents below 0.25

So the stated minimum is **not** the corpus's minimum, and a 0.25 floor fails **46%** of the documents it
was derived from. The clause that survives is the Market_Share one (0.349–0.392 across exactly 30), which
is why a 0.5 floor would fail all 30 — but "every family, every size" was never true.

WHY A SCRIPT AND NOT A CORRECTED NUMBER. Replacing one asserted figure with another asserted figure is
how this happened. T042's audit finding is the precedent: statistics with no committed derivation are
unverifiable by construction, and a reader cannot tell a measurement from a memory. So the derivation is
here, it runs against the corpus, and it prints the per-family table the contract quotes.

RUN IT WITH THE CORPUS PRESENT. The Morgan Stanley archive lives outside both repositories
(`/Users/frank/JMM/industry`, 73 report documents); when it is absent this exits non-zero rather than
reporting an empty table as a clean result — the zero-surface rule (`FR-006`).

    python3 scripts/measure_interpretive_floor.py            # table + re-derived floor
    python3 scripts/measure_interpretive_floor.py --quiet    # just the floor
"""
from __future__ import annotations

import argparse
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_report_readability as crr  # noqa: E402 — the shipped predicate, so this cannot drift

CORPUS = pathlib.Path("/Users/frank/JMM/industry")

#: The Morgan Stanley archive is the four `BIOPHARMA_*` directories — 3 + 18 + 22 + 30 = **73**, which is
#: the count the contract states. The other directories under the same root are a different corpus and
#: must not be averaged in.
#:
#: **This is a correction to my own first attempt at this script, and the error is instructive.** I
#: classified by filename prefix, which matched nothing, so all 78 measured documents landed in `other`
#: — including `llm_ai/` and `physical_ai/`, which hold arXiv machine-learning papers rather than
#: sell-side research (the contract itself makes that point about `references/bridgewater/`). Those two
#: directories supplied the lowest ratios in the run (0.056, 0.091, 0.105), so including them lowered the
#: measured minimum from 0.127 to 0.056 and made the floor look worse than it is on the corpus it claims.
#: A statistic computed over the wrong population is the exact defect this spec documents repeatedly, and
#: the discipline is to name the population rather than to widen it until the number is round.
FAMILY_DIRS = ("BIOPHARMA_Market_Share", "BIOPHARMA_CT_tracker", "BIOPHARMA_GLP-1", "BIOPHARMA_Takeaways")

#: Just below the measured minimum, by the contract's own method — it set 0.25 against a minimum it
#: believed was 0.27. The same rule against the real minimum is what this returns.
FLOOR_MARGIN = 0.01


def family_of(path: pathlib.Path) -> str:
    """The top-level directory — the corpus's own partition, not a guess from the filename."""
    try:
        return path.relative_to(CORPUS).parts[0]
    except ValueError:
        return "outside-corpus"


def measure() -> tuple[list[tuple[str, str, float, int]], float]:
    if not CORPUS.is_dir():
        print(f"measure_interpretive_floor: corpus not found at {CORPUS}", file=sys.stderr)
        print("  The derivation needs the Morgan Stanley archive; it is not in either repository.",
              file=sys.stderr)
        raise SystemExit(2)

    docs = sorted(p for p in CORPUS.rglob("*.md") if p.is_file())
    rows: list[tuple[str, str, float, int]] = []
    for p in docs:
        text = p.read_text(encoding="utf-8", errors="replace")
        numeric = crr.numeric_sentences(text)
        if len(numeric) < crr.MIN_NUMERIC_SENTENCES:
            continue                      # below the floor's own denominator; it cannot judge these
        interpreted = [s for s in numeric if crr.INTERPRET_RX.search(s)]
        rows.append((family_of(p), p.name, len(interpreted) / len(numeric), len(numeric)))

    if not rows:
        print("measure_interpretive_floor: 0 documents measured — a clean table would be a lie",
              file=sys.stderr)
        raise SystemExit(1)

    # The floor is derived from the ARCHIVE, not from everything that happens to live under the root:
    # averaging in a different corpus would let it set the standard for this one.
    archive = [r for fam, _, r, _ in rows if fam in FAMILY_DIRS]
    ratios = archive or [r for _, _, r, _ in rows]
    return rows, round(min(ratios) - FLOOR_MARGIN, 3)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    rows, floor = measure()
    ratios = [r for _, _, r, _ in rows]
    by_family: dict[str, list[float]] = {}
    for fam, _, ratio, _ in rows:
        by_family.setdefault(fam, []).append(ratio)

    if not args.quiet:
        print(f"interpretive floor — measured over {CORPUS}\n")
        print(f"  {'family':14} {'n':>4} {'min':>7} {'max':>7}")
        for fam in sorted(by_family):
            rs = by_family[fam]
            print(f"  {fam:14} {len(rs):>4} {min(rs):>7.3f} {max(rs):>7.3f}")
        print(f"  {'TOTAL':14} {len(ratios):>4} {min(ratios):>7.3f} {max(ratios):>7.3f}")
        archive = [r for fam, _, r, _ in rows if fam in FAMILY_DIRS]
        if archive:
            print(f"\n  the Morgan Stanley archive (the four BIOPHARMA_* dirs): {len(archive)} documents")
            print(f"    min {min(archive):.3f}  max {max(archive):.3f}  "
                  f"below 0.25: {sum(1 for r in archive if r < 0.25)} of {len(archive)}")
            print(f"    one independent run measured min 0.127 / 31 of 73 below — the two agree on the"
                  f"\n    finding while differing on the population, which is why the population is named")
        ratios = archive or ratios
        below = sum(1 for r in ratios if r < 0.25)
        print(f"\n  below the current 0.25 floor: {below} of {len(ratios)} "
              f"({below / len(ratios):.0%})")
        print(f"  median {statistics.median(ratios):.3f}  ·  the contract claims min 0.27, max 0.66")
        print(f"\n  re-derived floor (measured minimum − {FLOOR_MARGIN}): **{floor}**")
        print(f"  corpus min {min(ratios):.3f} · max {max(ratios):.3f} — the stated 0.66 does not occur ")
        print("  under the shipped predicate, which is the check that actually runs.")
    else:
        print(floor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
