---
name: ddm-valuation
description: Dividend Discount Model, DDM valuation, multi-stage dividend model, Gordon Growth Model, dividend growth valuation, mature company valuation, income stock valuation, dividend yield analysis
temporal_scope:
 default_quarters: 4
 max_quarters: 20
 description: "Dividend history requires 5+ years; forecast up to 10 years"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Dividend Discount Model (DDM)

Multi-stage DDM for mature dividend-paying companies. Values a stock as the present value of all expected future dividends. Especially appropriate for financials (JPM, BAC), utilities (DUK, SO), consumer staples (PG, KO), and REITs — where dividends are the primary mechanism of shareholder returns.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution ** and **Workspace style.md override check ** apply. **`get_realtime_quote` availability **: If not deployed, prompt user for current price and dividend yield. Beta from industry average (Damodaran) as fallback.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- dividend discount model {ticker}
- DDM valuation {ticker}
- dividend growth valuation {ticker}
- Gordon Growth Model {ticker}
- multi-stage DDM {ticker}
- income stock valuation {ticker}
- dividend yield analysis {ticker}
- value {ticker} by dividends
- mature company valuation {ticker}
- dividend-based fair value {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| stages | 3 | Explicit → Transition → Maturity |
| explicit_years | 5 | Years of explicit dividend forecast |
| transition_years | 5 | Years of declining growth |
| terminal_growth | 2.5% | Long-term perpetual growth (GDP proxy) |

## Methodology

### Retrieval Scope

`structured_only` — DDM uses dividend history from XBRL + current price + earnings estimates.

### Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Applicability check**: `search_xbrl_facts(ticker, concept=["Dividends", "CommonStockDividendsPerShareDeclared"], fiscal_year=[latest, latest-1, latest-2, latest-3, latest-4])` and `get_realtime_quote(ticker)` for dividend_yield. If no dividend history: flag "DDM not applicable — company does not pay dividends. Use DCF or Residual Income instead."
3. **Dividend profile**: compute historical DPS growth rate (3yr/5yr CAGR), payout ratio (DPS / EPS), dividend coverage (EPS / DPS >1.5 = comfortable).
4. **Cost of equity**: CAPM — risk-free rate (10Y UST), equity risk premium (~5%), beta from `get_realtime_quote`. Ke = Rf + β × ERP.
5. **Multi-stage model**:
 - **Stage 1 (Explicit)**: forecast DPS for next 5 years using consensus EPS × payout ratio (from `search_earnings_calendar`).
 - **Stage 2 (Transition)**: DPS growth linearly declines from Stage 1 rate to terminal growth rate over 5 years.
 - **Stage 3 (Maturity)**: perpetual DPS growing at terminal rate (Gordon Growth: TV = DPS_terminal × (1+g) / (Ke - g).
6. **Fair value**: PV of Stage 1 dividends + PV of Stage 2 dividends + PV of terminal value = per-share fair value.
7. **Output**: per with YAML frontmatter .

## Output File

Write to `{ticker}/{YYYY-MM-DD_HHMM}_ddm-valuation_dividend-model.md` .

## Output Structure

1. **Executive Summary** — per-share fair value, premium/discount to current price, implied dividend yield
2. **Dividend Profile** — historical DPS, growth rate, payout ratio, coverage ratio, dividend consistency
3. **Cost of Equity** — CAPM decomposition: Rf, β, ERP → Ke
4. **Stage 1 — Explicit Forecast** — projected DPS per year with growth assumptions
5. **Stage 2 — Transition** — declining growth trajectory
6. **Stage 3 — Terminal Value** — Gordon Growth perpetuity
7. **Sensitivity** — fair value at varying Ke (±1%, ±2%) and terminal growth (±0.5%, ±1%)
8. **Applicability Note** — if dividends are irregular or newly initiated, flag model limitations
9. **Coverage Gaps & Citations**

**Citation density**: ≥1 citation per 200 words. **Citation link format ** and **agentii.md append ** apply.

## Validation Gates

1. **Dividend consistency**: DPS must be positive in ≥4 of last 5 years. *If failed*: flag "Dividend history insufficient for reliable DDM — consider Residual Income or DCF."
2. **Growth sustainability**: DPS growth rate must not exceed sustainable growth rate (ROE × (1 - Payout Ratio). *If failed*: flag "Dividend growth exceeds sustainable rate — imply future dilution or leverage increase."
3. **Terminal value reasonableness**: Terminal value must be <80% of total fair value. *If failed*: flag "Terminal value dominates (>80% of fair value) — model highly sensitive to terminal assumptions."

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_realtime_quote` | Beta unavailable | Use industry average beta or prompt user for manual input |
| `search_earnings_calendar` | No consensus EPS | Use historical EPS trend for payout projection |

## Error Handling

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| No dividend history | Halt; redirect to DCF or Residual Income | "{ticker} does not pay dividends — DDM not applicable. Use DCF or Residual Income." |
| Zero or negative beta | Prompt user for manual beta input | "Beta unavailable for {ticker}. Please provide beta estimate." |
