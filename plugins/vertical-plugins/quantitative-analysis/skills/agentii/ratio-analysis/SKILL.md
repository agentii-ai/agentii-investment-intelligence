---
name: ratio-analysis
description: Financial ratio analysis, profitability ratios ROE ROA ROIC, liquidity ratios current quick cash, leverage ratios debt-to-equity interest coverage, efficiency ratios asset turnover inventory turnover DSO, valuation ratios PE PB EV/EBITDA, cross-company ratio comparison, DuPont analysis
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Trailing 4 quarters for current ratios, up to 12 for trend analysis"
allowed_tools:
 - get_financial_ratios
 - search_xbrl_facts
 - search_companies
 - get_realtime_quote
 - search_earnings_calendar
 - get_company_financials
retrieval_scope: structured_only
  - read_source_deep_outline
min_tool_diversity: 7
---

# Financial Ratio Analysis

Quantitative skill computing 6 categories of financial ratios from XBRL financial data. Cross-company comparison within sector. References WallStreetPrep and CFI professional ratio interpretation standards.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides.

**`get_realtime_quote` availability **: If `get_realtime_quote` is not yet deployed in the MCP surface, use `search_earnings_calendar` for PE/earnings data and flag valuation ratios as "current price unavailable — using latest reported data." Prompts user for current stock price as manual fallback.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze financial ratios for {ticker}
- ratio analysis {ticker}
- compute profitability ratios {ticker}
- liquidity analysis {ticker}
- leverage analysis {ticker}
- efficiency ratios {ticker}
- valuation ratios {ticker}
- DuPont analysis {ticker}
- cross-company ratio comparison {ticker}
- compare {ticker} ratios to peers

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| lookback_quarters | 4 | Trailing 4 quarters for current ratios |
| include_peers | true | Cross-company comparison within sector |
| ratio_categories | all | profitability, liquidity, leverage, efficiency, valuation, growth |

## Methodology

### Retrieval Scope

`structured_only` — this skill computes ratios from XBRL financial data and real-time price data. No unstructured document search required. All data sources are queryable via agentii MCP tools.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_companies` / `search_earnings_calendar`.

### Temporal Scope

Default: 4 fiscal quarters (max 12). Ratio analysis uses trailing 4 quarters for current snapshot; up to 12 quarters for trend analysis.

### Tool Allowlist

See frontmatter `allowed_tools` — 5 tools declared for this vertical. `search_xbrl_facts` is the primary data source for financial statement line items. `get_realtime_quote` provides current stock price for valuation ratios (P/E, P/B, P/S). `search_companies` enables peer identification for cross-company comparison.

### Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format, then `get_ticker_coverage/{ticker}` .
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","Assets","Liabilities","Equity","OperatingCashFlow","InventoryNet","ReceivablesNet","CurrentAssets","CurrentLiabilities","InterestExpense","LongTermDebt"], fiscal_year=[latest, latest-1, latest-2, latest-3])` — batch all concepts × 4 years.
3. **Price data**: `get_realtime_quote(ticker)` for current stock price, market cap, PE (TTM).
4. **Peer identification**: `search_companies(sector=<sector>)` to identify peer tickers for cross-company comparison.
5. **Compute ratios** into 6 categories per the Ratio Definitions below.
6. **Cross-company comparison**: for each peer, fetch key ratios and present comparison table with mean/median/high/low.
7. **Output**: per file convention with YAML frontmatter .

### Ratio Definitions

#### Profitability
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| ROE | Net Income / Avg Total Equity | >15% = strong; measures return to shareholders |
| ROA | Net Income / Avg Total Assets | >5% = efficient; asset utilization |
| ROIC | (EBIT × (1 - Tax Rate) / (Total Debt + Equity - Cash) | > WACC = value-creating |
| Gross Margin | Gross Profit / Revenue | Industry-dependent; higher = pricing power |
| Operating Margin | Operating Income / Revenue | >15% = healthy operations |
| Net Margin | Net Income / Revenue | >10% = strong bottom-line efficiency |

#### Liquidity
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Current Ratio | Current Assets / Current Liabilities | >1.5 = healthy; <1.0 = liquidity risk |
| Quick Ratio | (Cash + Receivables) / Current Liabilities | >1.0 = strong; acid test |
| Cash Ratio | Cash / Current Liabilities | Most conservative; >0.5 = adequate |
| Operating CF Ratio | Operating Cash Flow / Current Liabilities | >1.0 = can cover obligations from ops |

#### Leverage
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Debt-to-Equity | Total Debt / Total Equity | <2.0 = conservative; >4.0 = aggressive |
| Interest Coverage | EBIT / Interest Expense | >3x = safe; <1.5x = distress risk |
| Debt-to-EBITDA | Total Debt / EBITDA | <3x = manageable; >5x = highly leveraged |

#### Efficiency
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Asset Turnover | Revenue / Avg Total Assets | Higher = more efficient |
| Inventory Turnover | COGS / Avg Inventory | Higher = faster sales; watch for stockouts |
| Days Sales Outstanding | (Receivables / Revenue) × 365 | Lower = faster collections |
| Days Inventory Outstanding | (Inventory / COGS) × 365 | Lower = leaner operations |

#### Valuation (requires current price from `get_realtime_quote`)
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| P/E (LTM) | Price / LTM EPS | Lower = cheaper; sector-dependent |
| P/E (NTM) | Price / NTM Consensus EPS | Forward-looking; from `search_earnings_calendar` |
| P/B | Price / Book Value Per Share | <1.0 = below book; financials focus |
| EV/EBITDA | Enterprise Value / EBITDA | Capital-structure neutral |
| P/S | Market Cap / Revenue | Growth check; <2.0 = reasonable |
| PEG | P/E / Earnings Growth Rate | <1.0 = undervalued per Peter Lynch |

#### Growth
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Revenue CAGR (3yr) | (Revenue_t / Revenue_t-3)^(1/3) - 1 | Trend; >10% = strong growth |
| EPS CAGR (3yr) | (EPS_t / EPS_t-3)^(1/3) - 1 | >10% = strong earnings growth |
| Revenue CAGR (5yr) | (Revenue_t / Revenue_t-5)^(1/5) - 1 | Longer trend |
| EPS CAGR (5yr) | (EPS_t / EPS_t-5)^(1/5) - 1 | Longer earnings trend |

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_ratio-analysis_{affix}.md` . Example affixes: `profitability`, `liquidity-leverage`, `peer-comparison`.

## Output Structure

1. **Executive Summary** — top 3-5 ratios with interpretation, overall financial health assessment
2. **Profitability Analysis** — ROE, ROA, ROIC, margins table with trailing 4-quarter trend and industry comparison
3. **Liquidity Analysis** — current, quick, cash, operating CF ratios with short-term risk assessment
4. **Leverage Analysis** — D/E, interest coverage, debt/EBITDA with solvency assessment
5. **Efficiency Analysis** — asset turnover, inventory turnover, DSO, DIO with operational assessment
6. **Valuation Snapshot** — P/E (LTM+NTM), P/B, EV/EBITDA, P/S, PEG with sector peer comparison
7. **Growth Trends** — revenue/EPS CAGR (3yr + 5yr) with trend commentary
8. **Cross-Company Comparison** — peer ratio comparison table with mean/median/high/low (optional: --peers flag)
9. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec175/42)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root. See `contracts/agentii-md-schema.md`.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `get_realtime_quote` | Rate limit / unavailable | Use `search_earnings_calendar` for EPS estimates; flag valuation ratios as "price data unavailable" | "Real-time price unavailable; valuation ratios omitted" |
| `search_xbrl_facts` | Concept not found | Try alternative concept names via `list_xbrl_concepts` | "XBRL concept unavailable; used alternative" |
| `search_companies` | Sector undefined | Use SIC code from `get_company_profile` | "Peer identification via SIC code" |

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|-------------|-----------|--------|---------------------|
| Missing data | XBRL returns empty for key concepts | Widen date range and retry once | "No financial data available for {ticker} in requested window." |
| Non-USD currency | `unit` field is not USD | Annotate with ISO 4217 code | "⚠ {ticker} reports in {currency}. Ratios computed in reporting currency." |
| Peer data incomplete | <3 peers have comparable data | Reduce peer set; flag incomplete peers | "Cross-company comparison based on {n} of {m} peers with complete data." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
