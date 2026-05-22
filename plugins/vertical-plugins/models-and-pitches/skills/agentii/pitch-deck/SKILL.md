---
name: pitch-deck
description: Investment pitch deck, investment committee presentation, buy-side pitch, sell-side pitch, investment thesis slides, executive summary presentation, financial presentation, board deck, investor presentation, strategy deck
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - get_company_financials
  - get_company_profile
  - search_earnings_calendar
  - search_documents
retrieval_scope: structured_only
min_tool_diversity: 5
---

# pitch-deck

## Triggers

- Investment pitch deck
- investment committee presentation
- buy-side pitch
- sell-side pitch
- investment thesis slides
- executive summary presentation
- financial presentation
- board deck
- investor presentation
- strategy deck

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **structured_only**. Minimum tool diversity: 5 distinct tools.

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
