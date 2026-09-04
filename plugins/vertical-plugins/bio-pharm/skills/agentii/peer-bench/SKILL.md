---
name: peer-bench
description: "Med peer benchmarking: select actual biotech/pharma peers via the med universe (drug/indication overlap where possible) and compare med-relevant metrics — pipeline depth, catalyst density, cash position, margins, valuation multiples."
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

## Production Grounding

- Med peers are science-defined: use `get_company_drugs` to find indication/therapy overlap before financial comparison.
- Med-relevant metrics: pipeline assets by phase, catalyst density (PDUFA/AdCom/trial readouts), cash runway (quarters), R&D productivity; generic margins only as secondary.
- Grounding frameworks: `references/knowledge-frameworks.md` (道/法 review knowledge + valuation lenses).

## Data Source Priority

1. `get_company_drugs` / `search_companies` — peer discovery by drug/indication overlap.
2. `get_financial_ratios` / `search_xbrl_facts` — financial comparison data.
3. `get_peer_comparison` — platform pre-computed peer metrics.
4. Knowledge layer: `search_investment_cases`/`search_by_analogue` for historical peer dynamics.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Resolve the target via `get_company_profile`; pull its drugs (`get_company_drugs`).
2. Find peers by indication/therapy overlap + med industry membership (`search_companies`).
3. Pull per-peer financials (`get_financial_ratios`) + valuation context.
4. Ground with historical cases/analogues via knowledge tools.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Target profile
2. Science-based peer selection
3. Med-metric comparison
4. Valuation & risk synthesis

## Modes

- **Science-based** (default): indication/drug-overlap peers.
- **Financial**: margin/valuation peers within the same industry.
- **Catalyst**: peers ranked by upcoming FDA events.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_drugs empty | Fall back to industry peers via `search_companies`; annotate |
| get_peer_comparison empty | Build comparison manually from `get_financial_ratios` |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md`

## Output Structure

1. **Executive Summary** — relative standing in 2-3 sentences
2. **Peer Selection** — peers + selection logic (science overlap)
3. **Comparison Table** — med metrics + financials + valuation
4. **Historical Context** — cases/analogues with /v/ citations
5. **Risk Assessment** — concentration/catalyst risks
6. **Coverage Gaps** — missing data flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No indication overlap found | Widen to same-industry peers; flag science-overlap unavailable |
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
