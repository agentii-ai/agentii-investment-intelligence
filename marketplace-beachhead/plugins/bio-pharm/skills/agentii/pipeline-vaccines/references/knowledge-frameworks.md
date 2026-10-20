# Pipeline Vaccines — Knowledge Frameworks

Static grounding for `pipeline-vaccines` (spec 055). Runtime records are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the vaccine evidence ladder, cohort-bridging discipline, the ACIP gate in the value path, and failure modes. Shared regulatory scaffolding (scrutiny axes) lives in `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## Vaccine Evidence Ladder

1. **Immunogenicity / seroconversion studies**: antibody response as a correlate — evidence, but not efficacy. Never presented as efficacy.
2. **Efficacy trials**: healthy-population designs (large N, safety-first); endpoints prevent infection or disease. Power comes from N, and placebo arms shrink post-licensure.
3. **Lot-consistency trials**: immunogenicity equivalence across three manufacturing lots — a licensure gate, not a formality; without it, approval stalls regardless of efficacy data.
4. **Age-cohort bridging**: pediatric and elderly populations bridged from the pivotal cohort via immunogenicity or dedicated efficacy studies — each bridge extends the label.
5. **Booster and variant updates**: re-vaccination cycles re-open the market and shorten development timelines vs first-generation programs.

## Cohort-Bridging Discipline

- Track the pivotal population per asset and every bridged cohort separately: each age cohort carries its own study, its own timeline, and its own ACIP recommendation.
- Pediatric bridging is a separate gate: approval for adults does not imply pediatric licensure or recommendation.
- Booster cycles are recurring catalysts: model the re-vaccination interval as part of peak sales, not a one-time event.

## The ACIP Gate in the Value Path

- FDA approval is not commercial availability; the ACIP row (scheduled → voted → adopted, then CDC Director sign-off and MMWR publication) is a pipeline milestone, not a post-launch detail.
- Recommendation categories set the uptake ceiling: routine / catch-up / risk-based / shared-clinical-decision-making.
- A Phase III vaccine without a plausible ACIP path carries an unmodeled commercial step — the POS applies to licensure, and a second probability applies to the recommendation category.

## POS / Scenario Discipline (cross-cutting)

Unadjusted peak x POS = the modeled number; both terms shown; POS changes logged with reasons. For vaccines the POS chain is two-step: licensure probability, then recommendation-category outcome. Bull/base/bear with named-driver grids (category outcome, cohort expansion, procurement size); explicit abstention where unquantifiable.

## Commercial Context (P1 launch board, applied forward)

Consensus sales ÷ dose price ÷ campaign window → required doses → linear path vs at least two named same-category uptake curves. The vocabulary: doses/serials, procurement value, ACIP-cohort uptake. Procurement is lumpy: stockpile orders are one-time catalysts, not run-rate signals.

## Failure Modes

- **Presenting seroconversion as efficacy**: correlates are evidence, not endpoints.
- **Ignoring lot consistency as a gate**: the manufacturing milestone can stall licensure on schedule.
- **Missing cohort bridging value**: peak sized on the pivotal population alone understates the label.
- **Dropping the ACIP gate**: a pipeline model without the recommendation-category outcome overstates near-term revenue.
- **Treating procurement as run-rate**: stockpiles are one-time; campaign demand is recurring.
- **Underweighting the healthy-population bar**: safety-first review means safety signals re-time the whole ladder.

## Structured Data Surfaces

- `get_company_drugs` / `search_universe_drugs` — vaccine asset inventory and owner joins.
- `search_clinical_trials` / `get_clinical_trial` — design type, cohorts, status, enrollment.
- `search_acip_events` / `get_acip_event` — the gate path with vote counts per vaccine + meeting date.
- `search_fda_approvals` — BLA history.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; the client-question pattern — answer the most common question directly (e.g. "is the lot-consistency trial on the critical path?"); per-asset bull/bear pivot conditions.
- **Living-thesis loop**: estimates move first, ratings last; append exhibits to the prior note, never rewrite; cohort and booster timelines persist across updates.
- **Badge mapping (FR-092)**: verifiable facts `[FACT]`, derived arithmetic `[DEDUCTED]`, judgments `[VIEW]` — with a Category/Count/% summary table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_knowledge_entries` and cite with /v/ URLs.
