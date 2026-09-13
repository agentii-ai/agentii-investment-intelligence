---
name: peer-bench-med
description: "Med peer benchmarking: select actual biotech/pharma peers via the med universe (drug/indication overlap where possible) and compare med-relevant metrics — pipeline depth, catalyst density, cash position, margins, valuation multiples."
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - peer-selection
  - mechanism-overlap
  - analogs
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Benchmark window default 4 quarters; up to 12 for multi-year pipeline comparisons."
allowed_tools:
  - search_companies
  - get_company_profile
  - search_xbrl_facts
  - get_financial_ratios
  - get_peer_comparison
  - get_company_drugs
  - search_drugs_by_target
  - search_drugs_by_indication
  - search_investment_cases
  - get_investment_case
  - search_investment_strategies
  - get_investment_strategy
  - search_by_analogue
  - search_knowledge_entries
  - get_knowledge_entry
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught peer-comparison frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| peer_count | 4-6 | Comparable-set size standard for comps |
| peer_logic | indication/drug overlap first | Med peers are defined by science, not SIC codes |
| include_med_metrics | true | Pipeline depth, catalyst density, cash runway |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

Never fabricate a peer metric when the data surface is absent — annotate `coverage_gap` instead (spec 055 FR-B02 discipline).

## Triggers

- "Who are the closest peers to [biotech ticker]?"
- "Benchmark [ticker] against its biotech comp set."
- "How does [ticker]'s valuation compare to peers?"
- "Which names compete with [ticker]'s pipeline?"
- "Build a peer table with pipeline depth and cash."
- "Is [ticker] expensive relative to its med peers?"
- "Compare margins across the pharma peer group."
- "What are the catalyst-dense names in this peer set?"
- "Peer analysis for [ticker] with indication overlap."
- "Which peers have the strongest balance sheets?"
- "Which same-mechanism competitors matter for [ticker]'s pipeline?"

## Production Grounding

- Med peers are science-defined: use `get_company_drugs` to find indication/therapy overlap before financial comparison.
- Launch-analog selection: for commercial-stage names, match same-class (mechanism/indication class) + same-channel (specialty/retail/hospital/device-rep/vaccine-procurement) analogs so launch trajectories compare like-for-like.
- Mechanism-overlap scoring: rank candidate peers by shared targets/indications via the drug-knowledge reverse lookups; where sources conflict, keep both values with provenance.
- Med-relevant metrics: pipeline assets by phase, catalyst density (PDUFA/AdCom/trial readouts), cash runway (quarters), R&D productivity; generic margins only as secondary.
- Grounding frameworks: `references/knowledge-frameworks.md` (道/法 review knowledge + valuation lenses).

## Data Source Priority

1. `get_company_drugs` / `search_companies` — peer discovery by drug/indication overlap.
2. `search_drugs_by_target` / `search_drugs_by_indication` — mechanism competitor mapping + overlap scoring (054 silver reverse lookups).
3. `get_financial_ratios` / `search_xbrl_facts` — financial comparison data.
4. `get_peer_comparison` — platform pre-computed peer metrics.
5. Knowledge layer: `search_investment_cases`/`search_by_analogue` for historical peer dynamics + launch analogs.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Resolve the target via `get_company_profile`; pull its drugs (`get_company_drugs`).
2. Find peers by indication/therapy overlap + med industry membership (`search_companies`).
3. Map mechanism competitors: `search_drugs_by_indication` / `search_drugs_by_target` per key indication/target; score peers by shared targets/indications (conflicting sources shown with provenance).
4. Match launch analogs for commercial-stage names: same-class + same-channel; retrieve analog launch history via knowledge tools.
5. Pull per-peer financials (`get_financial_ratios`) + valuation context.
6. Ground with historical cases/analogues via knowledge tools.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Target profile
2. Science-based peer selection (indication/drug overlap)
3. Mechanism-overlap scoring (reverse lookups)
4. Launch-analog matching (same-class, same-channel)
5. Med-metric comparison
6. Valuation & risk synthesis

## Modes

- **Science-based** (default): indication/drug-overlap peers.
- **Launch-analog** (commercial-stage): same-class, same-channel analog peers with launch-trajectory context.
- **Financial**: margin/valuation peers within the same industry.
- **Catalyst**: peers ranked by upcoming FDA events.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_drugs empty | Fall back to industry peers via `search_companies`; annotate |
| Reverse lookups empty | Score overlap from `get_company_drugs` classes only; annotate mechanism mapping unavailable |
| get_peer_comparison empty | Build comparison manually from `get_financial_ratios` |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_peer-bench-med_{affix}.md`

## Output Structure

1. **Executive Summary** — relative standing in 2-3 sentences
2. **Peer Selection** — peers + selection logic (science overlap)
3. **Mechanism Overlap** — target/indication overlap matrix from reverse lookups, scored by shared mechanisms; conflicting source values shown with provenance
4. **Launch-Analog Match** — same-class, same-channel analogs (commercial-stage names)
5. **Comparison Table** — med metrics + financials + valuation
6. **Historical Context** — cases/analogues with /v/ citations
7. **Risk Assessment** — concentration/catalyst risks
8. **Coverage Gaps** — missing data flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No indication overlap found | Widen to same-industry peers; flag science-overlap unavailable |
| Mechanism data missing | Score from indication overlap only; flag reverse-lookup coverage gap |
| Missing financials | Mark N/A in table; do not fabricate |

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
