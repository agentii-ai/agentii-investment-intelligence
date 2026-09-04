# FDA Catalyst Analysis — Knowledge Frameworks

Static grounding for `fda-catalyst-analysis` (spec 052). Runtime records (approved med strategies/cases) are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the regulatory and scrutiny scaffolding those records rest on.

## FDA / EMA Regulatory Process

- **Application types**: NDA (drugs), BLA (biologics), ANDA (generics); devices via PMA / De Novo / 510(k) / HDE.
- **Review tracks**: standard review (~10 months), priority review (~6 months, serious conditions), breakthrough designation (rolling submission), accelerated approval (surrogate endpoints, confirmatory trials required), fast track.
- **PDUFA target date**: the FDA's negotiated decision date — the anchor of catalyst calendars.
- **Decision outcomes**: approval, Complete Response Letter (CRL — deficiencies; sponsors respond with amendments, triggering new target dates), withdrawal.
- **Post-approval**: post-marketing requirements/commitments (PMR/PMC), REMS safety programs, label restrictions.

## AdCom Mechanics (the scrutiny reference)

Advisory committee meetings are convened for **ambiguous approvals**. Key dynamics:
- Committees (ODAC, VRBPAC, MDAC, CRDAC, EMDAC, CTGTAC, BPAC, GIDAC, ...) review briefing docs (FDA reviewer analyses, sponsor slides), hear testimony, and **vote** on benefit-risk questions.
- Vote is advisory but highly predictive; markets often move at vote time, days before the PDUFA date.
- Decision types are **non-binary**: approve / reject / deferral / conditional / restricted indication.

## Scrutiny Axes (what FDA experts examine — apply to ANY trial readout or approval point)

1. **Safety signals** — SAE rates, deaths, DILI/renal/cardiac flags, imbalance vs control.
2. **Statistical adequacy** — power, multiplicity, alpha control, endpoint integrity.
3. **Subgroup analyses** — heterogeneity that hides risk or inflates benefit.
4. **Missing data** — dropout patterns, imputation choices, sensitivity analyses.
5. **Endpoint appropriateness** — surrogate vs clinical benefit, adjudication quality.
6. **Benefit-risk reasoning** — magnitude of benefit vs severity of unmet need and risk.

## Trial Phases & Evidence Bar

- **Phase 1**: safety/dosing (small N). **Phase 2**: signal of efficacy. **Phase 3**: registrational, randomized, controlled.
- Readout ≠ approval: phase-3 success is necessary but not sufficient; FDA review re-analyzes sponsor data.

## Catalyst Sizing (binary-risk logic)

- Position sizing for binary events follows expected value: P(approve) × upside − P(CRL) × downside, sized to max acceptable loss.
- Event clusters (AdCom + PDUFA close together, earnings overlap) concentrate risk.
- Unverified events (`verification_status=unverified`) get discounted sizing; superseded dates indicate a pushed timeline (information in the delay itself).

## Med Sector Metrics

- Cash runway (quarters) dominates for clinical-stage names; pipeline breadth/depth for commercial-stage.
- Sales-per-rep, R&D productivity, patent-cliff exposure for revenue-stage pharma.

## Authoring-time citations

Med strategies/cases extracted in spec 052 are linked below as they reach `approved` status (enriched per FR-005):
<!-- /v/knowledge/{citation_id} citations appended by the spec-052 enrichment step -->

### 道 — approval principles (L1, from the adcom corpus)

- Substantial Evidence Standard (`/v/strategies/med_adcom_taofa__substantial-evidence-standard__p4`)
- Totality of Evidence & Benefit-Risk Balance (`/v/strategies/med_adcom_taofa__totality-of-evidence-benefit-risk-balance__p3`)
- Safety Signal Characterization (`/v/strategies/med_adcom_taofa__safety-signal-characterization__p2`)
- Patient-Centric Risk-Benefit Context (`/v/strategies/med_adcom_taofa__patient-centric-risk-benefit-context__p1`)
- Clinical Meaningfulness of Endpoints (`/v/strategies/med_adcom_taofa__clinical-meaningfulness-of-endpoints__p0`)

### 法/器 — review methods & checklists (L2, from the adcom corpus)

- Comparator Selection Adequacy · Missing Data Sensitivity Evaluation · Subgroup Consistency Analysis · Surrogate Endpoint Validation Review · RWE Credibility Assessment · REMS Effectiveness Critique · Trial Design Integrity Audit · Indication Narrowing Probability Model · Vote Tally Interpretation Matrix · Red Flag Screening Checklist · Post-Market Commitment Verification · Manufacturing and CMC Feasibility Check · Labeling Clarity and Usability Review · Population Diversity & Equity Review · Conflict of Interest Management
  (retrieve at runtime via `search_investment_strategies(sectors=med, layer_tags=L2)`; each carries a `/v/strategies/{citation_id}` link)

### Structured AdCom calendar (runtime tools)

- `search_adcom_meetings` — committee/product/ticker/date/vote-outcome filters over `pipeline.adcom_meetings` (122 meetings, 113 with vote results).
- `get_adcom_meeting` — one meeting + briefing-document inventory; then read pages via `read_source_outline`/`read_source_pages` with the meeting slug.
