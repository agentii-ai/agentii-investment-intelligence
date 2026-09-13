---
name: med-market-sizing
description: Patient-flow market sizing for med products — prevalence → diagnosed → interested → affordable → covered → treated → persistent, priced as price × duration per cohort, with capacity constraints, named historical analog anchoring, and always bull/base/bear named-driver grids. Use to size a therapy area or product market before any valuation or share work.
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - market-sizing
  - patient-flow
  - tam
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Sizing horizon default 4 quarters; up to 12 for capacity and launch ramps."
allowed_tools:
  - search_companies
  - search_documents
  - search_sec_filings
  - list_sources
  - read_source_outline
  - read_source_pages
  - search_universe_drugs
  - search_universe_devices
  - search_drug_knowledge
  - search_drugs_by_indication
  - search_investment_cases
  - search_investment_strategies
  - search_knowledge_entries
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught patient-flow sizing approaches; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| funnel_stages | 7 | prevalence → diagnosed → interested → affordable → covered → treated → persistent |
| affordability_rule | ~10% monthly budget | Income-share rule per cohort and country |
| scenario_grid | bull/base/bear | Never a single point number |
| analog_anchors | named | Statins for penetration, tech S-curves for adoption |
| capacity_state | explicit | Supply-constrained vs demand-limited + flip condition |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before market queries.

## Triggers

- "What is the TAM for [therapy area]?"
- "Size the market for [drug/device] in [indication]."
- "What has to be true for the bear case in [class]?"
- "Walk me through the patient funnel for [indication]."
- "Is [class] supply-constrained or demand-limited?"
- "What capacity ceiling do [company]'s plants impose?"
- "Anchor [class] adoption to a historical analog."
- "Bull/base/bear sizing for [indication] with drivers."
- "How does the income-share rule cap affordability?"
- "What penetration rate is realistic for [class]?"
- "How much API does [class] need per patient-year?"

## Production Grounding

- Funnel: prevalence → diagnosed → interested → affordable (income-share rule, ~10% of monthly budget) → covered → treated → persistent; every stage carries an explicit rate or a `coverage_gap`. Price as price × duration per cohort and country; never skip a stage silently.
- Capacity check is mandatory: plants × units/yr, API kg/patient/yr, fill-finish lead times. State whether the market is supply-constrained or demand-limited and the condition that flips it.
- Analog anchoring: named historical analogs (statins for penetration, tech S-curves for adoption); every anchor carries its citation.
- Scenario discipline: bull/base/bear with a named-driver assumption grid; uncertainty at market level, POS at asset level; model-vs-consensus delta always explicit; abstain where unquantifiable.
- Badges: `[FACT]`/`[DEDUCTED]`/`[VIEW]` with the summary table.

## Data Source Priority

1. Prevalence/epidemiology: `search_documents` (epidemiology sources) + `read_source_outline` / `read_source_pages`.
2. Universe + mechanism: `search_universe_drugs` / `search_universe_devices`; `search_drug_knowledge` / `search_drugs_by_indication` (spec 054 silver).
3. Pricing/coverage: `search_sec_filings` (net price, GTN) + payer coverage via `search_documents`.
4. Capacity: filings and transcripts (plants, API supply, fill-finish).
5. Knowledge: `search_investment_strategies` / `search_investment_cases` (sectors=med) for sizing frameworks and prior TAM cases.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve indication and product scope via `search_companies` + `search_universe_drugs` / `search_universe_devices`.
2. Collect prevalence/diagnosis rates from epidemiology documents; cite each stage rate.
3. Pull pricing (net price, GTN) and coverage evidence from filings and payer documents.
4. Pull capacity evidence (plants, API supply, fill-finish) from filings/transcripts.
5. Anchor penetration to named analogs; retrieve prior TAM cases (sectors=med); cite /v/ records.
6. Build the bull/base/bear grid.

### Temporal Scope
See frontmatter temporal_scope block. Ramp and capacity paths may extend to max_quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Indication framing
2. Funnel build (stage rates cited or coverage_gap)
3. Cohort pricing (price × duration)
4. Capacity check + constraint state
5. Analog anchoring
6. Bull/base/bear grid

## Modes

- **Drug / biologic** (default): prevalence-based funnel with payer/coverage stages.
- **Device**: placements/procedures and installed-base stages replace script stages.
- **Vaccine**: healthy-population cohorts, ACIP-gated uptake, procurement value.
- **Single indication**: one indication × country with full cohort splits.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| Prevalence source absent | coverage_gap at the stage; list required inputs — never fabricate a rate |
| No pricing disclosure | Bracket net price from filings; label [DEDUCTED] / [VIEW] |
| Drug absent from silver layer | Universe + filings; annotate knowledge coverage_gap |
| Capacity undisclosed | State the flip-condition logic qualitatively [VIEW] |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_med-market-sizing_{affix}.md` (market-level: `_sector/{YYYY-MM-DD_HHMM}_med-market-sizing_{affix}.md`)

## Output Structure

1. **Executive Summary** — TAM stance + constraint state, 2-3 sentences
2. **Patient-Flow Funnel** — stage-by-stage rates, each cited or coverage_gap
3. **Cohort Pricing** — price × duration per cohort/country
4. **Capacity Check** — ceiling + supply-constrained vs demand-limited + flip condition
5. **Analog Anchors** — named penetration/adoption analogs with citations
6. **Scenario Grid** — bull/base/bear with named-driver assumptions
7. **Coverage Gaps** — missing sources and degraded stages

## Error Handling

| Error | Fallback |
|-------|----------|
| Missing prevalence data | coverage_gap at the stage; state the required input — never fabricate a rate |
| Conflicting prevalence sources | Show both with provenance; use the range in the scenario grid |
| No consensus comparator | State model vs consensus as unavailable; keep the bull/base/bear internal consistency |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `references/knowledge-frameworks.md`
