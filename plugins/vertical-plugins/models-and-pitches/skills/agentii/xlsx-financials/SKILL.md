---
name: xlsx-financials
multi_ticker_semantics: single_target
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
 - Bash
retrieval_scope: structured_only
min_tool_diversity: 2
---

# xlsx-financials

Shared skill for producing formatted Excel workbooks from XBRL financial statement data. Invoked as a sub-skill by financial modeling and analysis skills. Centralizes formatting, formula auditing, and calculation arc cross-validation in one place.

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

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default: latest fiscal year (max 12). Users can request specific fiscal years for multi-year comparison.

### Tool Allowlist

- `get_statement`: fetches rendered financial statement data with period columns
- `get_statement_structure`: fetches hierarchical concept tree with `order_in_parent`
- `search_xbrl_facts`: fallback for individual concept values
- `list_xbrl_concepts`: concept discovery when structure tree is unavailable
- **Excel generation**: uses `Bash` to execute a Python script with `openpyxl` (following Anthropic FSI xlsx-author conventions)

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

## Deliverable Chain

**Inputs** → **Build** → **Validate** → **Output** → **Next**

1. **Inputs**: resolved ticker + structured facts (`search_xbrl_facts`, `get_company_financials`) and any filing pages from the three-layer protocol.
2. **Build**: write a self-contained Python script using `openpyxl` that creates the workbook per `## Output Structure`; execute via `Bash: python3 script.py`; verify the `.xlsx` exists at the output path. If `import openpyxl` fails, fall back to the `.md` summary with `data_availability: degraded` (see `contracts/office-tooling.md`).
3. **Validate**: run the calculation-arc cross-check in the workbook Checks tab and the `## Validation Gates` below.
4. **Output**: write the artifact path per `## Output File`.
5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.

## Output File

Primary deliverable: `{ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx` — the formatted Excel workbook (the primary artifact).

Companion summary: `{ticker}/{YYYY-MM-DD_HHMM}_xlsx-financials_summary.md` — validation report with calculation-arc results, coverage gaps, and key citations. The `.md` summary is a companion, NOT a substitute for the `.xlsx`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## xlsx-author Conventions

Excel formatting conventions are in `references/methodology.md` and `contracts/office-tooling.md`.

## Validation Gates

1. **calculation arc cross-validation **: parent concept values MUST equal the weighted sum of children per `gold.xbrl_calculations`. Discrepancies ≥1% flagged in Checks tab. *If failed*: If ≥5% discrepancy: mark Checks tab cell red, add comment with the XBRL-expected value.
2. **statement structure integrity**: all concepts in the rendered statement MUST exist in the presentation tree (`gold.xbrl_presentation`). Missing concepts flagged. *If failed*: list missing concepts in a "Coverage Notes" sheet.
3. **period alignment**: all period columns MUST have data for the same set of concepts. Gaps flagged. *If failed*: fill empty cells with "N/R" (not reported) and note in Coverage Notes.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.

## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|-------------|-----------|--------|---------------------|
| No XBRL data for ticker | `get_statement` returns empty | Halt; suggest checking coverage | "No XBRL statement data for {ticker} in fiscal year {year}." |
| Statement type not available | `get_statement_structure` returns empty tree | Try alternative statement types | "{type} not available; available types: {available_types}." |
| Non-USD currency | `unit` field is not USD | Annotate with ISO 4217 code; apply currency label to all values | "⚠ {ticker} reports in {currency}. Values NOT converted to USD." |
| Calculation arc mismatch | Checks tab shows ≥5% discrepancy | Flag in Checks tab with red cell; note in output | "Calculation arc validation found {n} discrepancies ≥5%." |
