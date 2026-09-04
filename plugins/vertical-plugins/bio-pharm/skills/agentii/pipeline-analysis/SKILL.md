---
name: pipeline-analysis
description: "Med pipeline analysis: enumerate a biotech/pharma company's drug/device assets by phase, indication, and next catalyst, with risk-adjusted value framing and cash-runway assessment. The core valuation lens for clinical-stage names."
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Catalyst window default 4 quarters; up to 8 for long-horizon pipeline mapping."
allowed_tools:
  - get_company_drugs
  - get_company_devices
  - search_universe_drugs
  - search_universe_devices
  - search_companies
  - search_sec_filings
  - search_documents
  - read_source_outline
  - read_source_pages
  - search_xbrl_facts
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

> Methodology inspired by publicly taught pipeline-valuation frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| asset_scope | all disclosed assets | Full-pipeline enumeration first |
| include_devices | true | Devices via PMA/De Novo share catalyst logic |
| valuation_frame | risk-adjusted | rNPV-style thinking, not raw NPV |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Triggers

- "Analyze [biotech ticker]'s pipeline."
- "What's in [ticker]'s clinical portfolio?"
- "Map [ticker]'s assets by phase and indication."
- "What are [ticker]'s next catalysts?"
- "How much runway does [ticker] have?"
- "Risk-adjusted view of [ticker]'s pipeline value."
- "Which of [ticker]'s programs matter most?"
- "Pipeline deep-dive for [ticker]."
- "What devices does [ticker] have in the works?"
- "Compare [ticker]'s pipeline to its peers."

## Production Grounding

- Enumerate assets from `get_company_drugs`/`get_company_devices` (049 universes); supplement with filings (`search_sec_filings`, `read_source_*`) for trial phase/status.
- Phase-aware valuation: discovery/preclinical minimal; P1/P2 option-value; P3/registered majority of risk-adjusted value. Apply AdCom-style scrutiny axes when sizing pivotal-stage assets (per `references/knowledge-frameworks.md`).
- Cash runway (quarters) gates which catalysts the company can reach; funding risk is pipeline risk.

## Data Source Priority

1. `get_company_drugs` / `get_company_devices` — asset inventory from the 049 universes.
2. `search_sec_filings` / `read_source_*` — phase, status, trial data, guidance.
3. `search_xbrl_facts` — cash/R&D spend for runway.
4. Knowledge layer: `search_investment_strategies(sectors=med)` + cases for playbook grounding.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Pull asset inventory (`get_company_drugs`/`get_company_devices`).
2. Enrich per-asset phase/status/next-catalyst from filings.
3. Compute runway from balance-sheet facts.
4. Size each asset risk-adjusted; ground in strategies/cases.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Asset enumeration
2. Phase/status enrichment
3. Runway assessment
4. Risk-adjusted synthesis

## Modes

- **Full pipeline** (default): all assets with catalysts.
- **Value-drivers**: only the top risk-adjusted assets.
- **Runway-focused**: funding-requirement analysis.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_drugs empty | Reconstruct from filings keyword search; annotate coverage_gap |
| No cash data | Flag runway unavailable |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_pipeline-analysis_{affix}.md`

## Output Structure

1. **Executive Summary** — pipeline stance in 2-3 sentences
2. **Asset Table** — phase, indication, next catalyst, risk-adjusted sizing
3. **Value Drivers** — top assets with scrutiny-axes assessment
4. **Runway & Funding** — quarters of cash, funding needs
5. **Historical Context** — strategies/cases with /v/ citations
6. **Coverage Gaps** — degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| Phase unknown | Mark "undisclosed"; do not guess |
| No catalysts found | Say so explicitly; note pipeline may be early-stage |

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
