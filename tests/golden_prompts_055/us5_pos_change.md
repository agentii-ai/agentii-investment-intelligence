# us5_pos_change — US5: POS change logged with reason (uncertainty discipline over the mechanism map)

## Prompt

Revisit the probability-of-success for a drug whose competitive landscape just changed — for example, a same-target competitor's phase 3 failed or succeeded. Use the drug-knowledge reverse lookups to enumerate the mechanism/indication competitor set, then revise the asset's POS: log the previous POS, the new POS, and the reason for the change. Show the modeled peak-sales times POS arithmetic and the resulting model-vs-consensus delta.

## Rubric Checks

- [ ] POS change is logged with previous value, new value, and an explicit reason (cross-cutting habit: POS changes logged with reasons).
- [ ] Modeled number is shown as unadjusted peak sales x POS — the arithmetic, not just the product (uncertainty discipline at asset level).
- [ ] Model-vs-consensus delta is stated explicitly, signed, with the driver named; where no consensus value exists, a coverage_gap is annotated instead of a fabricated comparison.
- [ ] Competitor set is derived from the reverse lookups (search_drugs_by_target / search_drugs_by_indication) with tickers, and conflicting mechanism annotations are shown with provenance.
- [ ] Explicit abstention where a likelihood is unquantifiable ("no view on likelihood").
- [ ] Zero fabricated citations: every factual claim traces to a tool result or an approved /v/ knowledge record.
