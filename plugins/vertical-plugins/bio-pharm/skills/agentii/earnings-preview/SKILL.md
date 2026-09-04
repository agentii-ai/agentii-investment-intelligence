---
name: earnings-preview
description: "Med-adapted earnings preview: consensus estimates, historical surprises, guidance sensitivities, and the FDA-catalyst overlay (PDUFA/AdCom/trial readouts near the print) for biotech/pharma names."
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Preview window default 4 quarters; up to 8 for guidance trajectories."
allowed_tools:
  - search_earnings_calendar
  - search_xbrl_facts
  - get_company_profile
  - search_documents
  - read_source_outline
  - read_source_pages
  - search_investment_cases
  - get_investment_case
  - search_investment_strategies
  - get_investment_strategy
  - search_by_analogue
  - search_knowledge_entries
  - get_knowledge_entry
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught earnings-preview frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| surprise_window | 8 quarters | Standard surprise history window |
| include_catalysts | true | Med prints move on catalysts as much as EPS |
| guidance_sensitivity | true | Guidance is the swing factor for pharma |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Triggers

- "Preview [biotech ticker]'s upcoming earnings."
- "What should I expect at [ticker]'s next print?"
- "How has [ticker] surprised historically?"
- "Which catalysts land near [ticker]'s earnings date?"
- "Build an earnings preview with consensus estimates."
- "What's the guidance risk for [ticker] this quarter?"
- "Summarize the last few quarters for [ticker]."
- "Earnings + FDA calendar overlap for [ticker]."
- "What are the swing factors for [ticker]'s print?"
- "Historical reaction to [ticker]'s earnings surprises."

## Production Grounding

- Med prints have TWO drivers: financials (revenue/EPS/guidance) and catalysts (PDUFA/AdCom/readouts). The catalyst overlay is mandatory — a clean quarter can be undone by a CRL days earlier.
- For pre-revenue biotechs, the print is mostly about cash runway + pipeline updates; consensus EPS is secondary.
- Grounding frameworks: `references/knowledge-frameworks.md` (道/法 review knowledge).

## Data Source Priority

1. `search_earnings_calendar` — estimates, actuals, surprise history, next date.
2. `search_xbrl_facts` — revenue/EPS/margin trends.
3. `search_documents`/`read_source_*` — prior-quarter commentary and guidance.
4. Knowledge layer: `search_investment_cases` for historical print reactions.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve the earnings event: `search_earnings_calendar` for dates/estimates/surprises.
2. Pull fundamentals trend: `search_xbrl_facts` key line items.
3. Catalyst overlay: nearest PDUFA/AdCom/readout vs print date.
4. Ground with historical cases (print reactions) via knowledge tools.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Event & estimates
2. Fundamental trend
3. Catalyst overlay
4. Swing-factor synthesis

## Modes

- **Standard** (default): estimates + surprises + guidance.
- **Pre-revenue**: runway + pipeline + readout framing.
- **Catalyst-overlap**: print framed around nearby FDA events.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| search_earnings_calendar empty | Use filings (`search_documents`) for dates; annotate coverage_gap |
| No catalyst data | Flag "catalyst overlay unavailable" |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_earnings-preview_{affix}.md`

## Output Structure

1. **Executive Summary** — setup for the print in 2-3 sentences
2. **Consensus & Surprise History** — estimates table + surprise record
3. **Guidance & Swing Factors** — guidance risk analysis
4. **Catalyst Overlay** — FDA events near the print
5. **Historical Context** — cases with /v/ citations
6. **Coverage Gaps** — degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| Estimates missing | Present fundamentals trend only; flag |
| Date uncertain | Use calendar's best estimate + annotate |

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
