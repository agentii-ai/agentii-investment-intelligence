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
 - get_calculation_tree
 - validate_calculation
 - list_sources
retrieval_scope: simple_lookup
min_tool_diversity: 3
---

# audit-xls


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
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

**Calculation arc audit pattern **: When auditing a financial model workbook, this skill MUST cross-validate workbook computed totals against the XBRL calculation linkbase. The audit pattern:

1. **Retrieve calculation tree**: call `get_calculation_tree/{ticker}?statement_type=<income_statement|balance_sheet|cash_flow>` to get the expected parent-child formula relationships from `gold.xbrl_calculations` (756K rows). Each edge carries a `weight` (+1.0 for additive, -1.0 for subtractive).
2. **Reconstruct expected totals**: for each parent concept, compute `expected_value = Σ(child_value × weight)` per the XBRL calculation linkbase.
3. **Compare workbook vs expected**: for each parent-child relationship in the workbook, compare the workbook's computed total against the XBRL-expected total. Flag discrepancies ≥1% of the parent concept value as audit findings.
4. **Cross-validate with `validate_calculation/{ticker}`**: the endpoint performs automated calculation validation against `gold.xbrl_calculations` — use it as a second pass to catch discrepancies the workbook audit may have missed.

Discrepancies are categorized: (a) **material** (≥5% of parent value) — refuse delivery; (b) **minor** (1-5%) — flag in audit findings with `severity: warning`; (c) **negligible** (<1%) — note in audit trail but do not block delivery.

## Validation Gates

1. **calculation arc cross-validation **: workbook computed totals verified against `gold.xbrl_calculations` weights. Compare `get_calculation_tree/{ticker}` expected values against workbook formulas. Flag discrepancies ≥1% of parent concept value. *If failed*: If material discrepancy (≥5%): refuse delivery. If minor (1-5%): flag in audit findings with `severity: warning`.
2. **hardcoded cell detection**: zero hardcoded values in cells tagged as formulas. Use `xlsx_audit` hardcoded-count output. *If failed*: If hardcoded_count > 0: refuse delivery with audit report listing each hardcoded cell location.
3. **cross-sheet reference integrity**: all cross-sheet references resolve to valid cell ranges. *If failed*: If broken references found: refuse delivery with broken reference map.
4. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (3). *If failed*: flag as depth-insufficient in Coverage Gaps.

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
