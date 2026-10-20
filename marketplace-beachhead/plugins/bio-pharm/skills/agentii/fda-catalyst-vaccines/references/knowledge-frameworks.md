# FDA Catalyst Vaccines — Knowledge Frameworks

Static grounding for `fda-catalyst-vaccines` (spec 055). Runtime records are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the two-gate pathway ladder, failure modes, and the pattern disciplines. Shared regulatory scaffolding (scrutiny axes, binary-event sizing) lives in `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## The Two-Gate Pathway Ladder

1. **CBER BLA filing**: vaccines are biologics — review sits at CBER, with VRBPAC as the advisory committee.
2. **FDA approval**: necessary but not sufficient. The approval catalyzes the stock, not the market.
3. **ACIP review**: the Advisory Committee on Immunization Practices convenes on product, population, and schedule questions; the status ladder runs scheduled → voted → adopted.
4. **CDC Director sign-off + MMWR publication**: distinct steps from the vote — a voted recommendation becomes policy only after adoption and publication.
5. **Lot release**: each manufactured lot is released by CBER before shipment — a recurring operational gate that can delay a launch.
6. **Procurement + campaign**: government stockpiles and purchase contracts (doses/serials, procurement value), seasonal campaign timing.
7. **Cohort uptake**: ACIP-cohort uptake against the recommendation category sets the commercial trajectory.

## ACIP Recommendation Categories (the uptake ceiling)

- **Routine**: full age-based recommendation — the widest commercial gate.
- **Catch-up**: populations that missed the routine window.
- **Risk-based**: restricted to at-risk groups — a materially smaller market.
- **Shared-clinical-decision-making**: provider-patient discretion — the narrowest ceiling.

The category, not the vote count, is the commercial data point.

## Failure Modes

- **Treating FDA approval as commercial availability**: the ACIP row is the gate data; skipping it inflates the near-term revenue path.
- **Conflating the vote with adoption**: CDC Director sign-off and MMWR publication are separate, delayable steps.
- **Ignoring procurement timing**: government purchasing is lumpy; a stockpile order is a one-time catalyst, not a run-rate signal.
- **Underweighting the healthy-population bar**: safety signals in large healthy cohorts get outsized regulatory scrutiny; the efficacy bar is prevention, not treatment.
- **Missing pediatric bridging**: pediatric and age-cohort recommendations re-open the catalyst window after launch.
- **Unlabeled holiday weeks**: campaign-week comps across holidays are noise without labels.

## Methodology Patterns (original paraphrase of publicly taught practice)

### Vaccine vocabulary (P1, cross-cutting)

Doses/serials, procurement value, ACIP-cohort uptake. Launch tracking: consensus sales ÷ dose price ÷ campaign window → required doses → linear path vs actuals, overlaid with at least two named same-category uptake curves.

### Event-takeaway anatomy (P4)

Headline verdict → per-stock takeaways → KOL distillation → vote data and category reads → modeled deltas vs consensus → what's-changed vectors → risk bullets. Conflicting committee reads surfaced verbatim and rated by materiality.

### POS / scenario discipline (cross-cutting)

Unadjusted peak x POS = modeled number; the ACIP gate is a POS input, not an afterthought. Bull/base/bear with named-driver grids (category outcome, procurement size, campaign timing); explicit abstention where unquantifiable.

## Structured Data Surfaces

- `search_acip_events` / `get_acip_event` — the CDC ACIP calendar with the status ladder and vote counts per vaccine + meeting date.
- `get_upcoming_pdufa` / `search_fda_approvals` — CBER BLA dates and history.
- `search_adcom_meetings` — VRBPAC meeting records and briefing inventories.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; the client-question pattern — answer the most common question directly (e.g. "which recommendation category will the ACIP vote land?"); per-name bull/bear pivot conditions tied to the category outcome.
- **Living-thesis loop**: estimates move first, ratings last; append exhibits to the prior note, never rewrite; campaign-week labels persist.
- **Badge mapping (FR-092)**: verifiable facts `[FACT]`, derived arithmetic `[DEDUCTED]`, judgments `[VIEW]` — with a Category/Count/% summary table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_investment_cases` / `search_by_analogue` and cite with /v/ URLs.
