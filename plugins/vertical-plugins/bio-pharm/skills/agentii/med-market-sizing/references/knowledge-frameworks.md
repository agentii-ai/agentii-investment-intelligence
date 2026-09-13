# Med Market Sizing — Knowledge Frameworks

Static grounding for `med-market-sizing` (spec 055). Runtime records (approved med strategies/cases) are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the funnel, capacity, and scenario methodology the skill's arithmetic rests on. All content is an original paraphrase of publicly taught market-sizing practice.

## The Patient-Flow Funnel

Seven stages, in order: **prevalence → diagnosed → interested → affordable → covered → treated → persistent**.

- Every stage carries an explicit rate, an explicit assumption label, or a `coverage_gap`. A stage passed over silently invalidates every downstream number.
- Rates are staged per cohort and country, never one global rate applied everywhere.
- The result is priced as **price × duration per cohort** — peak sales follow from the funnel, not from a standalone multiple.

## The Income-Share Rule

- Affordability is capped at roughly 10% of monthly budget for self-pay cohorts: a treatment costing more than that share is assumed unaffordable for that income band.
- The rule is applied by country income distribution; where public coverage absorbs the cost, the covered stage substitutes for the affordability stage.
- The 10% figure is a stated judgment `[VIEW]`, flexed in the scenario grid — never presented as a measured constant.

## Capacity Arithmetic

- Supply-side checks are mandatory: plants × units/yr × $/unit; API kg/patient/yr for biologic/small-molecule supply; fill-finish lead times.
- State explicitly whether the market is **supply-constrained or demand-limited**, and name the condition that flips the state (e.g., new capacity crossing the demand path, or a cohort expansion absorbing the surplus).
- A sizing that ignores capacity quietly overstates a constrained launch; the ceiling is part of the answer, not a footnote.

## Analog Anchoring

- Penetration is anchored to named historical analogs: statin-era penetration curves for chronic oral classes, technology S-curves for adoption ramps, class-specific launch curves for per-year uptake.
- Every anchor is named and cited. An unnamed "industry standard" penetration rate is a defect.
- Device funnels replace script stages with placements/procedures and installed-base stages; vaccine funnels use healthy-population age cohorts with ACIP-gated uptake and procurement value.

## Scenario Discipline

- Output is always **bull / base / bear**, each with a named-driver assumption grid — never a single point number.
- Uncertainty discipline: scenario-flexing at market level, probability-of-success at asset level, model-vs-consensus delta always explicit, and explicit abstention ("no view on likelihood") where something is unquantifiable.
- Scenarios differ by named drivers (penetration rate, price erosion, coverage breadth, capacity timing) — the grid makes the disagreement visible.

## Modality Notes

- **Drugs/biologics**: prevalence-driven funnel; payer and coverage stages dominate.
- **Devices**: placements/procedures and installed base replace script volume; utilization drives recurring revenue.
- **Vaccines**: healthy-population efficacy framing; ACIP recommendation is the uptake gate, not FDA approval alone.

## Authoring-time citations

Med strategies/cases extracted in spec 052 are linked below as they reach `approved` status (enriched per FR-005):
<!-- /v/knowledge/{citation_id} citations appended by the spec-052 enrichment step -->
