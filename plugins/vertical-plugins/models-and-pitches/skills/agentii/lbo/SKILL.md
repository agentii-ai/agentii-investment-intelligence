---
name: lbo
multi_ticker_semantics: target_with_optional_peers
description: LBO model, leveraged buyout, private equity acquisition, sources and uses, debt schedule, returns waterfall, sponsor IRR, MOIC calculation, PE exit analysis, LBO valuation
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

- analyze lbo model
- run lbo model analysis
- produce lbo model report
- lbo model breakdown
- lbo model deep dive
- build a lbo model
- assess lbo model
- quantify lbo model
- compare lbo model across peers
- review lbo model for
- generate lbo model on
- lbo model for investment decision

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
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
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

## Deliverable Chain

```
[search_xbrl_facts + get_company_financials] → xlsx_build(spec: lbo) → xlsx_recalc → xlsx_audit → [.xlsx output]
```

## Validation Gates

1. **sources vs uses**: sources = uses within 0.1% tolerance. *If failed*: If unbalanced: refuse delivery.
2. **sponsor IRR**: >= 20% at exit. *If failed*: If IRR < 20%: flag in assumptions.
3. **debt schedule**: mandatory repayments present for each tranche. *If failed*: If missing: refuse delivery.
4. **calculation arc cross-validation **: cross-statement balancing verified against `gold.xbrl_calculations` weights — the LBO model's financial projections MUST align with the filer's reported accounting relationships. Call `get_statement_structure/{ticker}?statement_type=balance_sheet&include_calculations=true`. Flag discrepancies ≥1% of parent concept value. *If failed*: If material discrepancy (≥1%): flag in audit findings.

5. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (5). *If failed*: flag as depth-insufficient in Coverage Gaps, listing which tool categories were unused (structured data / document retrieval / company metadata / earnings calendar / coverage). This gate does NOT block analysis completion — it is a quality signal for your review.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_deep_outline` | PROXY_ERROR / 404 | Use lightweight `read_source_outline` and flag `deep_outline_degraded: true` | "deep outline unavailable; used lightweight page map instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output File

Write the final deliverable to `{ticker}/{{YYYY-MM-DD_HHMM}}_lbo_{{affix}}.md` .

## Output Structure

1. **Executive Summary** — sponsor IRR, MOIC, exit year, key value creation drivers (EBITDA growth, debt paydown, multiple expansion)
2. **Transaction Assumptions** — entry EBITDA, entry multiple, purchase price, debt/equity split, management equity rollover, transaction fees
3. **Sources & Uses** — sources (debt tranches, sponsor equity, management rollover) = uses (purchase price, fees, cash to B/S) within 0.1% (Validation Gate 1)
4. **Debt Schedule** — term loan, senior notes, subordinated notes, revolver: opening balance, mandatory repayments, optional repayments, interest rate, interest expense, closing balance per period (Validation Gate 3: mandatory repayments present for each tranche)
5. **Pro Forma Income Statement** — revenue, EBITDA, D&A, EBIT, interest expense, pre-tax income, net income per projection year
6. **Pro Forma Balance Sheet** — assets, debt tranches, equity accounts; calculation arc cross-validation per
7. **Cash Flow & Debt Paydown** — EBITDA → operating CF → total debt service → ending debt balances → cash generation
8. **Returns Waterfall** — enterprise value at exit → net debt at exit → equity value → sponsor equity return → IRR and MOIC
9. **Sensitivity Analysis** — 2-way table: entry multiple (rows) × exit multiple (columns) → IRR/MOIC matrix
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
