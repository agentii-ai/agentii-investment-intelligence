---
name: 3-statement
description: 3-statement financial model, integrated IS BS CF, income statement projection, balance sheet forecast, cash flow statement, cross-statement balancing, financial model build, operating model, three statement model, integrated financial statements
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Typical lookback: 4 quarters, max: 12"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - get_company_financials
  - get_company_profile
  - search_earnings_calendar
  - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 5
---

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze 3 statement model
- run 3 statement model analysis
- produce 3 statement model report
- 3 statement model breakdown
- 3 statement model deep dive
- build a 3 statement model
- assess 3 statement model
- quantify 3 statement model
- compare 3 statement model across peers
- review 3 statement model for
- generate 3 statement model on
- 3 statement model for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |





## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale across SEC filings (10-K, 10-Q, 8-K). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts. **Before querying XBRL facts, optionally call `get_statement_structure/{ticker}?statement_type=income_statement&fiscal_year=<YYYY>` to retrieve the exact line-item hierarchy from `gold.xbrl_presentation` (3.8M rows) — prevents concept-name hallucination and ensures accurate IS/BS/CF line-item ordering per FR-085.**
- Branch (b) for multi-period unstructured queries via `search_cross_period`.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

### Temporal Scope

Default: 12 fiscal quarters (max 20). Financial modeling: trailing 12 quarters (3 fiscal years) for long-range projection inputs.

### Tool Allowlist

See frontmatter `allowed_tools` — 12 tools declared for this vertical.

### Protocol

1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.
2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.
3. Retrieval: follow the three-layer protocol —
   - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.
   - Layer 2: `read_source_outline` to scan page-level metadata.
   - Layer 2.5 (optional): `search_keyword_in_source` to filter large documents.
   - Layer 3: `read_source_pages` to deep-read only selected pages.
4. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per the evidence-pack output contract.
5. **xlsx-financials output (FR-088)**: invoke `xlsx-financials` as sub-skill to produce formatted `.xlsx` workbook from `get_statement` data for IS, BS, and CF statements. Output: `{ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx` with calculation arc cross-validation per FR-086.

## Deliverable Chain

```
[search_xbrl_facts × 3 years] → xlsx_build(spec: 3-statement) → xlsx_recalc → xlsx_audit(cross-statement checks: BS balances, CF ties to BS, IS flows to CF) → [.xlsx output]
```

## Validation Gates

1. **balance sheet balance**: Assets = Liabilities + Equity within 1% tolerance. *If failed*: If unbalanced > 1%: refuse delivery, report imbalance amount.
2. **cash flow tie-out**: CF ending cash = BS cash for current period. *If failed*: If mismatched: refuse delivery, report discrepancy.
3. **forecast years**: exactly 5 historical + 5 forecast years. *If failed*: If < 5+5: flag in Coverage Gaps, proceed with available data.
4. **calculation arc cross-validation (FR-086)**: cross-statement balancing verified against `gold.xbrl_calculations` weights — each parent concept's value equals the weighted sum of its children per the XBRL calculation linkbase (e.g., `Assets = +1.0 × CurrentAssets + 1.0 × NoncurrentAssets`, `NetIncomeLoss = +1.0 × Revenues - 1.0 × OperatingExpenses + ...`). Call `get_statement_structure/{ticker}?statement_type=<type>&include_calculations=true` to retrieve the weighted parent-child relationships. Flag discrepancies ≥1% of parent concept value as audit findings. *If failed*: If any material discrepancy (≥1% of parent value): flag in audit findings, refuse delivery for discrepancies ≥5%.

5. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (5). *If failed*: flag as depth-insufficient in Coverage Gaps, listing which tool categories were unused (structured data / document retrieval / company metadata / earnings calendar / coverage). This gate does NOT block analysis completion — it is a quality signal for your review.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output Structure

1. **Executive Summary** — key model outputs (revenue CAGR, terminal EBITDA margin, ending cash balance), model integrity check results
2. **Historical Income Statement** (3-5 years) — revenue, COGS, gross profit, operating expenses, operating income, net income, diluted EPS with YoY growth rates
3. **Historical Balance Sheet** (3-5 years) — current assets, non-current assets, current liabilities, non-current liabilities, equity with period-over-period changes
4. **Historical Cash Flow** (3-5 years) — operating CF, investing CF, financing CF, net change in cash, ending cash balance
5. **Key Assumptions** — revenue growth rate, margin assumptions (gross/operating/net), working capital ratios (DSO, DIO, DPO), capex % of revenue, tax rate, dividend payout ratio
6. **Projected Income Statement** (5 forecast years) — same line items as historical with assumption-driven formulas
7. **Projected Balance Sheet** (5 forecast years) — same line items as historical; BS must balance within 1% per Validation Gate 1
8. **Projected Cash Flow** (5 forecast years) — same line items as historical; CF ending cash must tie to BS cash per Validation Gate 2
9. **Cross-Statement Validation** — balance check (A = L + E), cash tie-out, calculation arc cross-validation (FR-086), inter-statement consistency
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
