---
name: audit-xls
description: Audit spreadsheet, formula error detection, hardcoded cell finder, cross-sheet reference audit, workbook auditor, Excel model audit, financial model QA, spreadsheet review, cell dependency trace, formula integrity check
temporal_scope:
  default_quarters: 1
  max_quarters: 1
  description: "Typical lookback: 1 quarters, max: 1"
allowed_tools:
  - search_companies
  - get_company_financials
retrieval_scope: simple_lookup
min_tool_diversity: 3
---

# audit-xls

## Triggers

- Audit spreadsheet
- formula error detection
- hardcoded cell finder
- cross-sheet reference audit
- workbook auditor
- Excel model audit
- financial model QA
- spreadsheet review
- cell dependency trace
- formula integrity check

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 1 | Standard lookback for this skill type |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **simple_lookup**. Minimum tool diversity: 3 distinct tools.

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
