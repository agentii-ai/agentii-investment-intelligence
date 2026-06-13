---
name: revenue-decomp
description: Revenue decomposition, segment breakdown, geographic revenue split, product-line waterfall, revenue mix analysis, business segment performance, divisional revenue, revenue concentration, customer revenue dependency, channel revenue analysis
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - get_company_financials
 - search_documents
 - get_company_profile
 - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 6
---

# revenue-decomp


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- Revenue decomposition
- segment breakdown
- geographic revenue split
- product-line waterfall
- revenue mix analysis
- business segment performance
- divisional revenue
- revenue concentration
- customer revenue dependency
- channel revenue analysis

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **structured_only**. Minimum tool diversity: 6 distinct tools. **XBRL statement tree navigation **: before querying `search_xbrl_facts`, optionally call `get_statement_structure/{ticker}?statement_type=income_statement&fiscal_year=<YYYY>` to retrieve the hierarchical concept tree from `gold.xbrl_presentation` (3.8M rows) — navigate from root `Revenues` → `RevenueFromContractWithCustomer` → product/region dimension children to discover segment-level concepts.

## Output File

Write the final deliverable to `{ticker}/{{YYYY-MM-DD_HHMM}}_revenue-decomp_{{affix}}.md` .

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
