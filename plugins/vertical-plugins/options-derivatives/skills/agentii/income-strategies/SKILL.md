---
name: income-strategies
description: options income, covered call strategy, cash secured puts, credit spreads, iron condor, wheel strategy, premium selling, yield enhancement, defined risk income, monthly income options
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters for option position analysis; 12 for volatility regime comparison."
allowed_tools: [search_knowledge_entries, get_knowledge_entry, search_by_analogue, get_realtime_quote, get_options_chain]
retrieval_scope: structured_only
min_tool_diversity: 4
parameter_free: true
---

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| parameter_free | true | This skill has no tunable parameters; analysis scope set by temporal_scope frontmatter |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for relevant frameworks; query search_by_analogue for historical cases.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
See ## Protocol section below.



# income-strategies | sed 's/-/ /g; s/\b\(.\)/\u\1/g'

Options analysis powered by spec 037 L3/L4 knowledge base (K7).

## Preflight
Run the canonical pre-flight sequence. See `contracts/preflight.md`.

## Data Source Priority
1. Knowledge entries (K7 options frameworks) → 2. Options chain (live data) → 3. `search_by_analogue` for relevant cases

## Protocol
1. **Framework Application** — apply K7 frameworks from `references/knowledge-frameworks.md`
2. **Option Chain Analysis** — retrieve and analyze current option data
3. **Analogue Retrieval** — query historical options/volatility cases

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query gold.knowledge_entries for frameworks; query search_by_analogue for historical cases.

### Temporal Scope
See frontmatter temporal_scope.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
See ## Protocol section below.

## Output File
`{ticker}/{YYYY-MM-DD_HHMM}_income-strategies_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Framework Analysis** — applied frameworks with specific findings
3. **Quantitative Metrics** — relevant calculations and benchmarks
4. **Historical Analogues** — matched cases with citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags
1. Executive Summary 2. Framework Analysis 3. Option Greeks & Metrics 4. Historical Analogues 5. Risk Profile 6. Scenarios

## Error Handling
| Options chain unavailable | Proceed with framework-only analysis; flag `options_data: degraded` |

## Final Summary (TUI)
Include `### Key Citations` block (0–10 /v/ URLs).

## Memory Load

Load prior context before retrieval. See `contracts/memory-load.md`.

## Snapshot

Post-session synthesis. See `contracts/snapshot-synthesis.md`.

## Output Frontmatter

Structured output per `contracts/output-frontmatter-schema.md`.

## References
`references/knowledge-frameworks.md`, `contracts/citation-and-memory.md`
