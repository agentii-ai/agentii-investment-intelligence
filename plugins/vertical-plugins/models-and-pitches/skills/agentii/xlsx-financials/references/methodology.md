# xlsx-financials — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

1. **Fetch statement structure**: call `get_statement_structure/{ticker}?statement_type=<type>&fiscal_year=<YYYY>&include_calculations=true` to retrieve the hierarchical concept tree from `gold.xbrl_presentation` (3.8M rows) with `order_in_parent` and calculation arc weights .
2. **Fetch rendered statement**: call `get_statement/{ticker}?statement_type=<type>&fiscal_year=<YYYY>` for the period-column-formatted financial data.
3. **Structure for Excel**: map the hierarchical concept tree to Excel rows with proper indentation levels, parent-child grouping, and subtotal rows.
4. **Build workbook**: write a Python script using `openpyxl` (following Anthropic FSI xlsx-author conventions) and execute via Bash.

## Protocol

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
5. **Inject calculation arcs**: when `include_calculations=true`, add a hidden "Validation" sheet with the calculation arc cross-check: parent expected value vs sum of weighted children .
6. **Write the `.xlsx` workbook** (see `contracts/office-tooling.md`):
   a. Write a self-contained `.py` script (`_build_{ticker}_{type}.py`) using `openpyxl` that creates a Workbook with sheets Cover, IS, BS, CF, Ratios, Segments, ArcCheck, NamedRanges; applies formatting per `style.md`; injects the calculation-arc cross-validation per `## Validation Gates`; and follows Anthropic FSI conventions (blue=input, black=formula, green=cross-sheet link).
   b. Execute: `Bash: python3 _build_{ticker}_{type}.py`.
   c. Verify: `Bash: ls -la {ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx` — confirm the file exists and size > 0.
   d. Write the companion `.md` summary with validation results + key citations.
   e. If step (b) fails with `ModuleNotFoundError: No module named 'openpyxl'`: output the `.md` summary with full data tables, annotate `data_availability: degraded` and `openpyxl_missing: true`, and report `pip install openpyxl`.

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
