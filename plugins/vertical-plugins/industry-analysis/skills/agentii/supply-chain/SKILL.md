---
name: supply-chain
description: Supply chain mapping, supplier dependency analysis, customer concentration, geographic concentration, bottleneck identification, supply chain risk, logistics network, sourcing strategy, inventory management, vertical integration analysis
temporal_scope:
  default_quarters: 4
  max_quarters: 10
  description: "Typical lookback: 4 quarters, max: 10"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - search_documents
  - search_sec_filings
  - get_company_financials
  - list_coverage
  - read_source_outline
  - list_xbrl_concepts
  - read_source_pages
  - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 6
---

# supply-chain


**Agent Call Tracing (FR-106)**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- Supply chain mapping
- supplier dependency analysis
- customer concentration
- geographic concentration
- bottleneck identification
- supply chain risk
- logistics network
- sourcing strategy
- inventory management
- vertical integration analysis

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **unstructured_document_search**. Minimum tool diversity: 6 distinct tools.

## Output Structure

1. Executive Summary
2. Data Sources (with agentii://source/ citation watermarks)
3. Analysis Results
4. Coverage Gaps (if any)

## Error Handling

| Error | Action |
|-------|--------|
| Ticker not found | Suggest checking spelling or trying list_coverage |
| No data available | Flag in Coverage Gaps, proceed with available data |
| API key invalid | Direct user to agentii.ai/api-keys |
| MCP server unreachable | Retry once; if persistent, halt with AGENTII_MCP_UNREACHABLE |
