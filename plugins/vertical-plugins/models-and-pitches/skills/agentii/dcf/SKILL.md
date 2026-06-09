---
name: dcf
description: DCF valuation model, discounted cash flow, intrinsic value, WACC calculation, terminal value, free cash flow projection, equity value per share, DCF sensitivity analysis, unlevered free cash flow, present value calculation, build a DCF
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


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze dcf model
- run dcf model analysis
- produce dcf model report
- dcf model breakdown
- dcf model deep dive
- build a dcf model
- assess dcf model
- quantify dcf model
- compare dcf model across peers
- review dcf model for
- generate dcf model on
- dcf model for investment decision

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
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts. **Before querying XBRL facts, optionally call `get_statement_structure/{ticker}?statement_type=income_statement&fiscal_year=<YYYY>` to retrieve the exact line-item hierarchy from `gold.xbrl_presentation` (3.8M rows) — prevents concept-name hallucination and ensures accurate income statement structure for FCF projection .**
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
5. **xlsx-financials output**: invoke `xlsx-financials` as sub-skill to produce formatted `.xlsx` workbook from `get_statement` data for income statement (FCF projection baseline). Output: `{ticker}/{YYYY-MM-DD_HHMM}_statement-income.xlsx` with calculation arc cross-validation .

## Deliverable Chain

```
[search_xbrl_facts + get_company_financials] → xlsx_build(spec: dcf) → xlsx_recalc → xlsx_audit(hardcoded_count==0) → [.xlsx output] → (optional) pptx_build(executive-summary) → xlsx_convert(pdf)
```

## Validation Gates

1. **projection horizon**: ≥ 5 years (10 years for secular-trends analysis). *If failed*: If < 5 years: refuse delivery, report actual horizon.
2. **terminal growth rate**: < risk-free rate proxy (current 10Y UST). *If failed*: If terminal_g ≥ rf: flag in assumptions section, note conservatism violation.
3. **WACC components**: WACC = (E/V × Ke) + (D/V × Kd × (1-T) with all components cited to source data. *If failed*: If components uncited: refuse delivery, list missing citations.
4. **hardcoded_count**: == 0 for all cells tagged projection|margin|discount_factor|pv|sensitivity per xlsx_audit output. *If failed*: If hardcoded_count > 0: per the hardcode gate, refuse delivery. Bounce back to analytical-subagent ONCE with audit report.
5. **calculation arc cross-validation **: cross-statement balancing verified against `gold.xbrl_calculations` weights — the DCF free-cash-flow projection and income statement structure MUST align with the filer's reported concept hierarchy. Call `get_statement_structure/{ticker}?statement_type=income_statement&include_calculations=true`. Flag discrepancies ≥1% as audit findings. *If failed*: If material discrepancy (≥1%): flag in audit findings, refuse delivery for discrepancies ≥5%.

6. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (5). *If failed*: flag as depth-insufficient in Coverage Gaps, listing which tool categories were unused (structured data / document retrieval / company metadata / earnings calendar / coverage). This gate does NOT block analysis completion — it is a quality signal for your review.

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

1. **Executive Summary** — intrinsic value per share, upside/downside vs. current price, key value drivers, WACC used
2. **Key Assumptions** — risk-free rate, equity risk premium, beta, cost of equity (Ke), cost of debt (Kd), target capital structure, WACC, terminal growth rate, projection period (≥5 years per Validation Gate 1)
3. **Unlevered Free Cash Flow Projection** — EBIT → NOPAT → D&A add-back → Capex → Working Capital Changes → UFCF for each projection year with YoY growth rates
4. **Terminal Value** — Gordon Growth Model: TV = UFCF(n+1) / (WACC - g). Terminal growth rate must be < risk-free rate (Validation Gate 2)
5. **Enterprise Value** — PV of projected UFCFs + PV of Terminal Value. Mid-year convention applied where appropriate
6. **Equity Value Bridge** — Enterprise Value - Net Debt + Cash - Minority Interest → Equity Value
7. **Per-Share Value** — Equity Value / Fully Diluted Shares Outstanding → intrinsic value per share
8. **Sensitivity Analysis** — 2-way data table: WACC (rows) × Terminal Growth Rate (columns) → per-share value matrix
9. **Calculation Arc Cross-Validation ** — income statement structure verified against `gold.xbrl_calculations` weights; FCF drivers aligned with historical margins from XBRL
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
