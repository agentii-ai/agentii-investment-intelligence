# Pipeline Medicines — Knowledge Frameworks

Static grounding for `pipeline-medicines` (spec 055). Runtime records are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the phase ladder, POS discipline, status-diff taxonomy, competitor mapping, and failure modes. Shared regulatory scaffolding (scrutiny axes) lives in `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## Phase Ladder and Evidence Bar

- **Phase I**: safety and dosing in small N; no efficacy claim.
- **Phase II**: efficacy signal in a target population; proof-of-concept gate.
- **Phase III**: registrational, randomized, controlled; success is necessary but not sufficient — FDA review re-analyzes sponsor data.
- **Filed / approved**: post-Phase III, the asset graduates to the catalyst-calendar skills; pipeline tracking ends at the filing.

## POS Discipline (the core habit)

- **The modeled number is always unadjusted peak x POS.** A bare risk-adjusted figure hides the assumption; both terms are shown.
- **POS starts from published phase-transition ranges** and is adjusted only with a logged reason: trial data, competitor data, discontinuation, dose change.
- **Every POS change is logged with its reason.** Silent POS drift is a defect.
- **Scenario brackets**: bull/base/bear per asset with a named-driver grid (enrollment speed, endpoint choice, competitor events); never a single point number.
- **Explicit abstention**: "no view on likelihood" is a valid entry where the evidence is unquantifiable.

## Status-Diff Taxonomy (trial re-timing as data)

Eleven status categories: New / Suspended / Withdrawn / Terminated / Recruiting / Recruitment-Complete / Completed / Ahead / Delayed / Upsized / Downsized. The discipline is the previous-value columns: previous primary-completion, previous status, previous enrollment shown next to the new values. Risk signals: Terminated plus Downsized (enrollment collapse) is a red flag; Ahead/Delayed re-times the catalyst; Recruitment-Complete starts the readout clock.

## Competitor Mapping

- `search_drugs_by_target` — every drug mapped to the same molecular target: same-target crowding is the sharpest competitive read.
- `search_drugs_by_indication` — every drug mapped to the disease term: same-indication crowding discounts peak sales, not just POS.
- Class risk: mechanism overlap means safety findings travel; an unrelated-indication asset can still be hit by class-wide signals.

## Commercial Context (P1 launch board, applied forward)

For late-stage assets, build the forward launch board: consensus sales ÷ net price per script ÷ script duration → required weekly scripts → linear path vs at least two named same-class launch curves. LOE erosion: entrant share series and branded year-over-year decay side by side. This is the exit lens for every Phase III asset in the model.

## Failure Modes

- **Risk-adjusted numbers without the unadjusted peak**: impossible to audit; rejected.
- **POS drift without logged reasons**: the most common pipeline-model error.
- **Ignoring competitor crowding**: peak sized in a vacuum survives first contact with the competitor map.
- **Double-counting overlap**: shared platforms counted twice across indications.
- **Ignoring runway**: cash gates which catalysts the company can reach; funding risk is pipeline risk.
- **Unlabeled holiday weeks**: script comps across holidays are noise.

## Structured Data Surfaces

- `get_company_drugs` / `search_universe_drugs` — asset inventory and owner joins.
- `search_drug_knowledge` / `get_drug_knowledge` — mechanism, targets, indications, phase, bioactivity, provenance per drug.
- `search_clinical_trials` / `get_clinical_trial` — status, enrollment, primary-completion dates.
- `search_fda_approvals` — registration history.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; the client-question pattern — answer the most common question directly (e.g. "why did you change the POS here?"); per-asset bull/bear pivot conditions.
- **Living-thesis loop**: estimates move first, ratings last; append exhibits to the prior note, never rewrite; the POS change log persists across updates.
- **Badge mapping (FR-092)**: verifiable facts `[FACT]`, derived arithmetic `[DEDUCTED]` (the peak x POS products), judgments `[VIEW]` (the POS inputs) — with a Category/Count/% summary table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_investment_cases` / `search_knowledge_entries` and cite with /v/ URLs.
