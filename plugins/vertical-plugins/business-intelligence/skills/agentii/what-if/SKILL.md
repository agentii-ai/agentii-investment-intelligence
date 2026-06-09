---
name: what-if
description: What-if scenario analysis, scenario tree construction, base bull bear case, sensitivity to macro variables, revenue scenario modeling, cost scenario analysis, margin impact scenarios, interest rate sensitivity, currency impact scenarios, commodity price scenarios
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Typical lookback: 4 quarters, max: 12"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - get_company_financials
  - search_earnings_calendar
  - get_company_profile
  - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 6
---

# what-if


**Agent Call Tracing (FR-106)**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- What-if scenario analysis
- scenario tree construction
- base bull bear case
- sensitivity to macro variables
- revenue scenario modeling
- cost scenario analysis
- margin impact scenarios
- interest rate sensitivity
- currency impact scenarios
- commodity price scenarios

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **structured_only**. Minimum tool diversity: 6 distinct tools.

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
