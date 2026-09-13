# US1 — Launch Board with Consensus-Implied Trajectory

## Prompt

Run the market-share-tracking skill on a launched GLP-1 product with at least three quarters of disclosed sales and produce the launch board: actual trajectory versus at least two named same-class analog curves, plus the consensus-implied trajectory with the required-TRx arithmetic and every assumption stated. Annotate every data caveat on the numbers shown, and where a number has no retrievable source, emit a coverage_gap rather than a value.

## Rubric

- [ ] Launch-curve comparison against ≥2 named same-class analogs (names and launch dates given; not a generic "class average")
- [ ] Consensus-implied trajectory computed with stated assumptions: consensus sales, net price per script, script duration → required TRx → linear weekly path vs actuals
- [ ] Every number carries a source line or a coverage_gap annotation
- [ ] ≥1 caveat annotation present (restricted scripts, rounding, indication-mixed, IV-invisibility, holiday week) where the underlying data warrants it
- [ ] Zero fabricated script numbers — no source means coverage_gap, not an estimate presented as fact
- [ ] Derived values labeled [DEDUCTED]/[VIEW] per the badge convention, with the summary table
