---
name: technical-execution
description: Technical execution timing, entry exit signals, price action analysis, volume profile, market structure, support resistance levels, trend identification, Wyckoff method, auction market theory, trade management timing, position entry exit optimization
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 2
  max_quarters: 8
  description: "2 quarters for entry/exit timing analysis; 8 for market structure context."
allowed_tools: [search_knowledge_entries, get_knowledge_entry, search_by_analogue, get_realtime_quote]
retrieval_scope: structured_only
min_tool_diversity: 3
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



# Technical Execution (Entry/Exit Timing)

**CRITICAL CONSTRAINT (FR-021)**: Technical analysis is NOT a trade initiator. Investment ideas originate from L1 (macro), L2 (fundamental), or L3 (strategy). This skill serves ONLY entry/exit timing — when to buy, when to sell, how to manage the position. Never use technical patterns as the primary reason to enter a trade.

## Preflight
Run the canonical pre-flight sequence. See `contracts/preflight.md`. Verify the analysis request has an existing investment thesis from L1/L2/L3 before proceeding.

## Protocol
1. **Thesis Anchoring** — identify the originating investment thesis (which L1/L2/L3 skill produced it)
2. **Entry Timing** — apply L4 frameworks (Wyckoff, Market Profile, volume analysis) to optimize entry
3. **Exit Planning** — define profit targets and stop levels based on market structure
4. **Trade Management** — scaling in/out plan, position adjustment triggers

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
`{ticker}/{YYYY-MM-DD_HHMM}_technical-execution_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Framework Analysis** — applied frameworks with specific findings
3. **Quantitative Metrics** — relevant calculations and benchmarks
4. **Historical Analogues** — matched cases with citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags
1. Originating Thesis Reference 2. Entry Analysis 3. Exit Plan 4. Trade Management 5. Risk Controls

## Error Handling
| No originating thesis from L1/L2/L3 | HALT — do not proceed; technical analysis is not a trade initiator |

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
