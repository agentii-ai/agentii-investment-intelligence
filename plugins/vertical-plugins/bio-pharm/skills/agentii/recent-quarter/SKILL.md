---
name: recent-quarter
description: "Med-adapted recent-quarter review: last print financials, pipeline-milestone awareness, and FDA-event context — reads the quarter through the med lens (milestones moved, runway, regulatory updates) rather than generic financials alone."
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 1
  max_quarters: 8
  description: "Review window defaults to the most recent quarter; extend to 8 for milestone trajectories."
allowed_tools:
  - search_xbrl_facts
  - get_statement
  - search_documents
  - read_source_outline
  - read_source_pages
  - get_company_profile
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

> Methodology inspired by publicly taught quarter-review frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| review_quarters | 1 | Recent quarter focus |
| include_milestones | true | Pipeline milestones are med quarter content |
| include_regulatory | true | CRL/approval/AdCom updates belong in the review |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Triggers

- "Review [biotech ticker]'s most recent quarter."
- "What happened at [ticker]'s last earnings?"
- "Summarize [ticker]'s latest 10-Q."
- "How did [ticker]'s pipeline progress last quarter?"
- "Any regulatory updates for [ticker] recently?"
- "Quarterly review with milestone tracking for [ticker]."
- "What did management say about the pipeline?"
- "Runway update for [ticker] after the last print."
- "What moved for [ticker] last quarter?"
- "Quarter in review: financials + catalysts for [ticker]."

## Production Grounding

- A med quarter is judged on BOTH reported financials and pipeline/regulatory progress; milestone slips and CRLs are first-class quarter content.
- Cash runway (quarters of cash) is a primary metric for clinical-stage names.
- Grounding frameworks: `references/knowledge-frameworks.md` (道/法 review knowledge).

## Data Source Priority

1. `search_xbrl_facts` / `get_statement` — reported financials.
2. `search_documents` / `read_source_*` — management commentary, pipeline updates.
3. `get_company_profile` — company context.
4. Knowledge layer: `search_investment_cases` for similar quarter dynamics.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Pull the latest statements via `get_statement` + key facts via `search_xbrl_facts`.
2. Read management commentary (`read_source_outline`/`read_source_pages`) for milestones/regulatory.
3. Assess runway + milestone trajectory.
4. Ground with historical cases via knowledge tools.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Financial review
2. Milestone & regulatory review
3. Runway assessment
4. Quarter synthesis

## Modes

- **Standard** (default): financials + milestones + regulatory.
- **Pre-revenue**: runway-focused review.
- **Regulatory-heavy**: quarter framed around FDA events.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_statement unavailable | Reconstruct from `search_xbrl_facts`; annotate |
| No commentary found | Note coverage gap; use filings only |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_recent-quarter_{affix}.md`

## Output Structure

1. **Executive Summary** — quarter verdict in 2-3 sentences
2. **Financial Review** — key line items + trends
3. **Milestone & Regulatory Review** — pipeline progress, FDA updates
4. **Runway & Cash** — runway assessment
5. **Historical Context** — cases with /v/ citations
6. **Coverage Gaps** — degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No recent filings | Flag stale coverage; use latest available |
| Milestone data missing | Note explicitly; do not infer |

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
