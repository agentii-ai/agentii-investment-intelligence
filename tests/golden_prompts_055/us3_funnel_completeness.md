# US3 — Patient-Flow Funnel Completeness

## Prompt

Run the med-market-sizing skill for the obesity-drug market and produce the sizing: build the patient-flow funnel (prevalence → diagnosed → interested → affordable → covered → treated → persistent) with every stage rate named and cited or coverage_gap, apply price × duration per cohort, check the capacity constraint and state whether the market is supply-constrained or demand-limited (with the flip condition), anchor penetration to named historical analogs, and present bull/base/bear scenarios with named drivers — never a single point number.

## Rubric

- [ ] All seven funnel stages present in order, none skipped silently
- [ ] Every intermediate rate named AND cited or coverage_gap — no uncited rates
- [ ] Capacity check present: plants × units/yr, API kg/patient/yr, or fill-finish lead times, with supply-constrained vs demand-limited state and the flip condition
- [ ] ≥1 named historical analog for penetration/adoption (statin-style penetration or tech S-curve), cited
- [ ] Bull/base/bear grid with a named driver per scenario — no single point number anywhere in the output
- [ ] Derived arithmetic labeled [DEDUCTED], judgments [VIEW]; zero fabricated citations
