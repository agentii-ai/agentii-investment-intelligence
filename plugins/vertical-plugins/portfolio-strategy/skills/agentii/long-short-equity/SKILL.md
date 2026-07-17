---
name: long-short-equity
description: long short equity strategy, pair trade construction, market neutral portfolio, net exposure management, factor neutrality, equity long short, hedge fund strategy, alpha generation, stock picking portfolio construction, long short position management
multi_ticker_semantics: target_with_optional_peers
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "8 quarters for portfolio construction; 20 for strategy backtesting."
allowed_tools: [search_knowledge_entries, get_knowledge_entry, search_by_analogue, get_realtime_quote, search_xbrl_facts]
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



# long-short-equity | sed 's/-/ /g; s/\b\(.\)/\u\1/g'

Portfolio strategy analysis powered by spec 037 L3 knowledge base.

## Preflight
Run the canonical pre-flight sequence. See `contracts/preflight.md`.

## Data Source Priority
1. Knowledge entries (L3 strategy frameworks) → 2. `search_by_analogue` for strategy cases → 3. XBRL facts (position/portfolio context)

## Protocol
1. **Strategy Framework** — apply L3 frameworks from `references/knowledge-frameworks.md`
2. **Analogue Retrieval** — query historical cases matching the strategy pattern
3. **Quantitative Analysis** — compute relevant metrics using XBRL + knowledge frameworks

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
`{ticker}/{YYYY-MM-DD_HHMM}_long-short-equity_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Framework Analysis** — applied frameworks with specific findings
3. **Quantitative Metrics** — relevant calculations and benchmarks
4. **Historical Analogues** — matched cases with citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags
1. Executive Summary 2. Strategy Framework 3. Quantitative Analysis 4. Historical Analogues 5. Risk Assessment 6. Scenarios

## Error Handling
| No L3 frameworks available | Proceed with standard analysis; flag `knowledge_coverage: degraded` |

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
