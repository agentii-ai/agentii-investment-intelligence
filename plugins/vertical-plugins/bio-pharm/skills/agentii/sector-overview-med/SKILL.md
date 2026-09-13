---
name: sector-overview-med
description: "Med-sector overview across med.medicines_biotech and med.medical_devices with med trends, catalysts, FDA-decision context, and a cross-sector ripple map (quantified sign/magnitude per name). Use to frame any biotech/pharma/device analysis before diving into a single name."
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - sector-analysis
  - ripple-maps
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Sector framing default 4 quarters; up to 12 for long-horizon trends."
allowed_tools:
  - search_companies
  - list_coverage
  - get_ticker_coverage
  - search_unified
  - search_documents
  - search_adcom_meetings
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

> Methodology inspired by publicly taught sector-framing approaches; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| taxonomy_level | industry (2 med industries) | Med sector frames at industry granularity |
| include_catalysts | true | FDA decisions are the defining med-sector driver |
| lookback_quarters | 4 | Standard trend window |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Triggers

- "Give me an overview of the biotech sector."
- "How is the pharma industry structured?"
- "What are the main med sector trends right now?"
- "Which med sub-sectors are most catalyst-rich this quarter?"
- "Map the medical-devices landscape for me."
- "What's the regulatory backdrop for healthcare this year?"
- "How do med.medicines_biotech names differ from med.medical_devices?"
- "Summarize the FDA approval environment for the sector."
- "What are the structural drivers of biotech valuations?"
- "Which committees are most active in AdCom reviews lately?"

## Production Grounding

- Med industry scope: `med.medicines_biotech` and `med.medical_devices`; healthcare services and life-sciences tools are out of scope for the bio-pharm vertical (servable by generic skills).
- FDA decisions (approve/CRL/AdCom) are the strongest sector catalysts; sector framing must include the catalyst calendar (`search_adcom_meetings`).
- Cross-sector ripple map: for every sector-level catalyst (FDA decision, pricing action, funding regime, class readout), map the quantified sign and magnitude per covered name — a have/have-not stock map, not a headline. Magnitudes carry sources or `[VIEW]` labels; names with no exposure are listed as have-nots, not omitted.
- Living-exhibit convention: sector exhibits are append-only — new observations append to the existing exhibit, prior entries are never rewritten. Every fact carries its source line.
- Grounding frameworks: `references/knowledge-frameworks.md` (道/法 layered review knowledge).

## Data Source Priority

1. `search_companies` / `list_coverage` — sector membership and data freshness.
2. `search_adcom_meetings` — catalyst calendar by committee/date.
3. Knowledge layer: `search_investment_strategies(sectors=med)` + `search_investment_cases(sectors=med)` for sector-level plays.
4. `search_unified` / `search_documents` — filings/news context.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve sector scope via `search_companies` + taxonomy; count names per industry via `list_coverage`.
2. Pull catalyst density: `search_adcom_meetings` for the window.
3. Ground with med strategies/cases via the knowledge tools (sectors=med).
4. Synthesize trends with cited evidence.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Taxonomy framing
2. Catalyst mapping
3. Knowledge grounding
4. Trend synthesis

## Modes

- **Full sector** (default): both med industries with catalyst overlay.
- **Single industry**: deep-dive one industry (e.g., medicines_biotech).
- **Catalyst-focused**: sector view organized around upcoming FDA events.
- **Ripple map**: one sector catalyst propagated to per-name sign/magnitude, appended to the living exhibit.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| search_companies empty | Use `search_unified` keyword search; annotate coverage_gap |
| search_adcom_meetings empty | Degrade to `search_documents` keyword "AdCom"; flag |
| Knowledge tools empty | Proceed with structured data only; annotate knowledge coverage_gap |

## Output File

`_sector/{YYYY-MM-DD_HHMM}_med-sector-overview-med_{affix}.md`

## Output Structure

1. **Executive Summary** — sector stance in 2-3 sentences
2. **Taxonomy Map** — industries + representative names + coverage stats
3. **Catalyst Calendar** — dated FDA/earnings events shaping the sector
4. **Trends & Structural Drivers** — with evidence
5. **Cross-Sector Ripple Map** — per-name quantified sign/magnitude per sector catalyst (have/have-not stock map), appended to the living exhibit
6. **Knowledge Grounding** — med strategies/cases with /v/ citations
7. **Coverage Gaps** — data limitations and degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No taxonomy matches | Broaden via `search_companies` name search; flag degraded |
| Empty catalyst calendar | Note sector catalysts may be sparse; rely on knowledge layer |

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
