---
name: xlsx-financials
description: Produce formatted .xlsx financial statement workbooks from XBRL statement data. Uses Bash + openpyxl (Python) following Anthropic FSI xlsx-author conventions for professional Excel output with calculation arc cross-validation.
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Fiscal years for statement rendering; default latest year"
allowed_tools:
  - search_xbrl_facts
  - get_statement
  - get_statement_structure
  - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 2
---

# xlsx-financials

Shared skill for producing formatted Excel workbooks from XBRL financial statement data. Invoked as a sub-skill by financial modeling and analysis skills. Centralizes formatting, formula auditing, and calculation arc cross-validation (FR-086) in one place.


**Agent Call Tracing (FR-106)**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- Produce Excel financial statements for {ticker}
- Generate .xlsx workbook from XBRL data
- Export income statement to Excel
- Export balance sheet to Excel
- Export cash flow statement to Excel
- Render financial statements as spreadsheet
- Create formatted financial workbook
- Build .xlsx from get_statement output
- Financial model Excel export
- Statement Excel output

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| statement_type | income_statement | income_statement, balance_sheet, cash_flow, equity, oci |
| fiscal_year | (latest available) | Integer year |
| include_calculations | true | Include calculation arc weights for cross-validation |

## Methodology

### Retrieval Scope

`structured_only` — this skill wraps the XBRL `get_statement` endpoint and does not perform document search. It is purely a data-to-Excel rendering pipeline.

### Retrieval Strategy

1. **Fetch statement structure**: call `get_statement_structure/{ticker}?statement_type=<type>&fiscal_year=<YYYY>&include_calculations=true` to retrieve the hierarchical concept tree from `gold.xbrl_presentation` (3.8M rows) with `order_in_parent` and calculation arc weights (FR-085, FR-086).
2. **Fetch rendered statement**: call `get_statement/{ticker}?statement_type=<type>&fiscal_year=<YYYY>` for the period-column-formatted financial data.
3. **Structure for Excel**: map the hierarchical concept tree to Excel rows with proper indentation levels, parent-child grouping, and subtotal rows.
4. **Build workbook**: write a Python script using `openpyxl` (following Anthropic FSI xlsx-author conventions) and execute via Bash.

### Temporal Scope

Default: latest fiscal year (max 12). Users can request specific fiscal years for multi-year comparison.

### Tool Allowlist

- `get_statement`: fetches rendered financial statement data with period columns
- `get_statement_structure`: fetches hierarchical concept tree with `order_in_parent` (FR-085)
- `search_xbrl_facts`: fallback for individual concept values
- `list_xbrl_concepts`: concept discovery when structure tree is unavailable
- **Excel generation**: uses `Bash` to execute a Python script with `openpyxl` (following Anthropic FSI xlsx-author conventions)

### Protocol

1. **Receive request from parent skill**: parent skill (dcf, comps, 3-statement, recent-quarter, earnings-preview) invokes this skill with `ticker`, `statement_type`, and `fiscal_year`.
2. **Fetch statement structure** via `get_statement_structure` — get the hierarchical concept tree with indentation levels.
3. **Fetch statement data** via `get_statement` — get the period-column financial values.
4. **Apply formatting rules** per `style.md`:
   - Currency: $#,##0.0 with B/M/K auto-detection
   - Percentages: 0.0%
   - Frozen header row (row 1)
   - Parent concepts: **bold**
   - Child concepts: indented 2 spaces per level
   - Subtotal rows: bold with top border
5. **Inject calculation arcs**: when `include_calculations=true`, add a hidden "Validation" sheet with the calculation arc cross-check: parent expected value vs sum of weighted children (FR-086).
6. **Write workbook** via `Bash` executing a Python `openpyxl` script: write a self-contained `.py` script, execute with `python3`, output to the path specified by the parent skill. Follow Anthropic FSI conventions: blue=hardcoded input, black=formula, green=cross-sheet link, named ranges, Checks tab.

## Output

### Single-Ticker
```
{ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx
```
Example: `LLY/2026-06-03_1430_statement-income.xlsx`

### Multi-Ticker
```
_cross/{slug}_{YYYY-MM-DD_HHMM}_statement-{type}.xlsx
```
Example: `_cross/LLY-vs-peers_2026-06-03_1430_statement-income.xlsx`

## xlsx-author Conventions

Following Anthropic FSI `xlsx-author` conventions:

- **Blue font** = hardcoded input values (statement data fetched from API)
- **Black font** = formulas (subtotals, growth rates, validation checks)
- **Green font** = links/references to other sheets
- **Named ranges** for key metrics (Revenue, NetIncome, TotalAssets) to enable cross-sheet references
- **Checks tab**: include a "Checks" sheet with TRUE/FALSE validation:
  - BS balance: Assets = Liabilities + Equity
  - Subtotal tie-out: parent = sum of children per calculation arcs
  - Period consistency: all periods have matching concept coverage

## Validation Gates

1. **calculation arc cross-validation (FR-086)**: parent concept values MUST equal the weighted sum of children per `gold.xbrl_calculations`. Discrepancies ≥1% flagged in Checks tab. *If failed*: If ≥5% discrepancy: mark Checks tab cell red, add comment with the XBRL-expected value.
2. **statement structure integrity**: all concepts in the rendered statement MUST exist in the presentation tree (`gold.xbrl_presentation`). Missing concepts flagged. *If failed*: list missing concepts in a "Coverage Notes" sheet.
3. **period alignment**: all period columns MUST have data for the same set of concepts. Gaps flagged. *If failed*: fill empty cells with "N/R" (not reported) and note in Coverage Notes.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `get_statement` | Endpoint unavailable | Use `search_xbrl_facts` with individual concept queries; structure manually from `get_statement_structure` tree | "Statement endpoint unavailable; built from individual XBRL facts" |
| `get_statement_structure` | Timeout | Use `list_xbrl_concepts` for concept discovery; flat structure without hierarchy | "Statement tree unavailable; flat concept list used" |
| `Bash` / openpyxl | Python/openpyxl not installed | Output markdown table as fallback; annotate output with "Excel generation failed; markdown table provided" | "openpyxl unavailable; markdown table provided" |

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|-------------|-----------|--------|---------------------|
| No XBRL data for ticker | `get_statement` returns empty | Halt; suggest checking coverage | "No XBRL statement data for {ticker} in fiscal year {year}." |
| Statement type not available | `get_statement_structure` returns empty tree | Try alternative statement types | "{type} not available; available types: {available_types}." |
| Non-USD currency | `unit` field is not USD | Annotate with ISO 4217 code; apply currency label to all values | "⚠ {ticker} reports in {currency}. Values NOT converted to USD." |
| Calculation arc mismatch | Checks tab shows ≥5% discrepancy | Flag in Checks tab with red cell; note in output | "Calculation arc validation found {n} discrepancies ≥5%." |
