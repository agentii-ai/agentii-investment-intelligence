---
name: residual-income
multi_ticker_semantics: target_with_optional_peers
description: Residual Income valuation, EVA Economic Value Added, excess return valuation, book value plus economic profit, financial institution valuation, bank valuation, insurance company valuation
temporal_scope:
 default_quarters: 4
 max_quarters: 20
 description: "Trailing equity data; up to 20 quarters for projection"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Residual Income / Economic Value Added (EVA) Valuation

Values a company as: Book Value + Present Value of Future Economic Profit. Economic profit = earnings ABOVE the required return on equity. Especially valuable for financial institutions (banks, insurers) where DCF is problematic due to the nature of debt (it's inventory, not capital) and for capital-intensive firms. Also known as the Edwards-Bell-Ohlson (EBO) model in academic literature.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution ** and **Workspace style.md override check ** apply. **`get_realtime_quote` availability **: If not deployed, use industry beta (Damodaran) for CAPM. Current price not critical for RI model (book-value based).


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- residual income valuation {ticker}
- EVA valuation {ticker}
- economic value added {ticker}
- excess return model {ticker}
- book value plus economic profit {ticker}
- EBO model {ticker}
- bank valuation model {ticker}
- financial institution valuation {ticker}
- value {ticker} residual income
- RI valuation {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| projection_years | 5 | Years of explicit residual income forecast |
| terminal_growth | 2.5% | Perpetual RI growth (should be conservative) |
| cost_of_equity | CAPM | Ke = Rf + β × ERP, or manual input |

## Methodology

### Retrieval Scope

`structured_only` — Residual Income uses book value from XBRL + earnings estimates + current price.

### Retrieval Strategy

Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

### Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 20. The default balances recency against the trend window this analysis requires.

### Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `get_realtime_quote` — latest market price for valuation cross-checks
- `search_earnings_calendar` — EPS actual/estimate/surprise + report dates

### Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Book value**: `search_xbrl_facts(ticker, concept=["Equity", "StockholdersEquity"], fiscal_year=[latest])` — latest book value of equity.
3. **Earnings**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest+1, latest+2])` for consensus EPS estimates.
4. **Cost of equity (Ke)**: CAPM — Rf (10Y UST) + β × ERP (5%). β from `get_realtime_quote`.
5. **Forecast residual income**:
 - For each forecast year: RI_t = Net Income_t - (Ke × Beginning Book Value_t-1)
 - Book Value_t = Book Value_t-1 + Net Income_t - Dividends_t
 - Dividends_t = Net Income_t × Payout Ratio (historical average or zero if no dividend)
6. **Terminal value**: TV = RI_terminal × (1+g) / (Ke - g), where g is perpetuity growth (typically 0% or GDP-like rate for RI).
7. **Fair value**: BV_0 + PV(RI_1) + PV(RI_2) + ... + PV(RI_terminal) + PV(TV) = per-share equity value.
8. **Output**: per with YAML frontmatter .

### When to Use Residual Income vs. DCF

| Company Type | Preferred Model | Why |
|-------------|----------------|-----|
| Banks, Insurers | Residual Income | Debt is inventory, not capital — DCF doesn't work |
| Capital-Intensive Industrials | Residual Income | Asset-heavy; book value is meaningful |
| Asset Managers | Residual Income | AUM-based; book value + fee earnings |
| Tech, SaaS, Pharma | DCF | Asset-light; cash flow focus |
| Mature Dividend Payers | DDM | Dividends are the primary return mechanism |
| High-Growth, No Earnings | Revenue-based DCF | No earnings or book value to anchor |

## Output File

Write to `{ticker}/{YYYY-MM-DD_HHMM}_residual-income_eva-model.md` .

## Output Structure

1. **Executive Summary** — per-share fair value, premium/discount to current price, implied P/B vs current P/B
2. **Book Value Analysis** — current BV per share, historical BV growth, ROE trend
3. **Cost of Equity** — CAPM decomposition: Rf, β, ERP → Ke
4. **Residual Income Projection** — year-by-year RI forecast with NI, BV, Dividends, RI per year
5. **Terminal Value** — perpetuity of residual income beyond forecast horizon
6. **Fair Value Bridge** — BV_0 + PV(RI_1..5) + PV(TV) = per-share value
7. **Implied P/B** — fair value P/B vs. current P/B; if <1.0, market prices below book (distress signal or value opportunity)
8. **Sensitivity** — fair value at varying Ke (±1%, ±2%) and terminal RI growth (±1%)
9. **Coverage Gaps & Citations**

**Citation density**: ≥1 citation per 200 words. **Citation link format ** and **agentii.md append ** apply.

## Validation Gates

1. **RI convergence**: residual income must not grow perpetually above Ke. *If failed*: terminal growth g must be < Ke by at least 2%.
2. **Book value consistency**: BV_t = BV_t-1 + NI_t - D_t must hold for all forecast years. *If failed*: refuse delivery; check arithmetic.
3. **Economic plausibility**: fair value P/B between 0.1x and 10x. *If failed*: flag extreme assumptions.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_realtime_quote` | Beta unavailable | Use industry average beta from Damodaran data |
| `search_earnings_calendar` | No consensus | Use historical EPS trend + manual ROE forecast |

## Error Handling

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| Negative book value | Halt | "Book value is negative — Residual Income model not applicable. Use DCF." |
| No earnings data | Halt | "Insufficient earnings data for {ticker}." |
