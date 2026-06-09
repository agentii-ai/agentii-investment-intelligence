---
name: reverse-dcf
description: Reverse DCF valuation, implied growth rate, market expectations analysis, reverse discounted cash flow, implied valuation assumptions, market-implied projections, DCF sanity check
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Current price input; historical data for comparison"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Reverse DCF — Market-Implied Expectations

Starts from the current stock price and solves backward: "What growth rate, margin, or WACC does the market currently price in?" Answers: "Is the market too optimistic or too pessimistic about {ticker}?" This is a sanity-check tool used by professional analysts to test whether consensus assumptions are already reflected in the stock price.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution ** and **Workspace style.md override check ** apply. **`get_realtime_quote` availability **: If not deployed, prompt user for current stock price — required input for reverse DCF.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- reverse DCF {ticker}
- implied growth rate {ticker}
- what does the market price in {ticker}
- market-implied valuation {ticker}
- reverse discounted cash flow {ticker}
- is {ticker} priced for perfection
- market expectations DCF {ticker}
- sanity check valuation {ticker}
- implied assumptions {ticker}
- DCF reverse engineer {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| projection_years | 5 | Explicit forecast period |
| solve_for | growth_rate | growth_rate, terminal_margin, or wacc |
| terminal_growth | 2.5% | Long-term GDP-like growth rate |
| compare_to | consensus | Compare implied to consensus estimates |

## Methodology

### Retrieval Scope

`structured_only` — Reverse DCF uses current price + XBRL financials + consensus estimates.

### Protocol

1. **Inputs**: current stock price from `get_realtime_quote(ticker)`. Shares outstanding and latest financials from `search_xbrl_facts`.
2. **Set up DCF model**: standard DCF with UFCF = EBIT × (1-T) + D&A - Capex - ΔWC. Terminal value via Gordon Growth Model.
3. **Solve for implied growth rate**: iterate growth rate until DCF fair value = current market price (within 1% tolerance).
4. **Solve for implied terminal margin**: if solving for margin, iterate terminal EBITDA/FCF margin instead.
5. **Solve for implied WACC**: if solving for WACC, iterate WACC until DCF = market price (reveals market-implied discount rate).
6. **Compare to benchmarks**:
 - Implied growth vs. consensus estimates (from `search_earnings_calendar`)
 - Implied growth vs. historical CAGR (from XBRL)
 - Implied margin vs. current margin + historical trend
 - Implied WACC vs. CAPM-derived WACC
7. **Assessment**: flag when market prices in >20% above consensus (potentially overvalued) or >20% below consensus (potentially undervalued).
8. **Output**: per with YAML frontmatter .

## Output File

Write to `{ticker}/{YYYY-MM-DD_HHMM}_reverse-dcf_implied-expectations.md` .

## Output Structure

1. **Executive Summary** — implied growth rate, comparison to consensus, market sentiment assessment
2. **Inputs** — current price, shares outstanding, current financials, WACC assumptions
3. **Implied Growth Rate** — solved growth rate, comparison to consensus LTG and historical CAGR
4. **Implied Terminal Margin** — solved terminal EBITDA/FCF margin vs. current and historical margins
5. **Market Expectation Assessment** — is the market pricing in aggressive (>20% above consensus), reasonable (within ±20%), or pessimistic (>20% below consensus) assumptions?
6. **Sensitivity** — implied growth at varying WACC (±1%, ±2%)
7. **Coverage Gaps & Citations**

**Citation density**: ≥1 citation per 200 words. **Citation link format ** and **agentii.md append ** apply.

## Validation Gates

1. **Convergence**: DCF must converge to market price within 1% within 50 iterations. *If failed*: flag "DCF does not converge — extreme assumptions required."
2. **Economic plausibility**: implied growth rate must be between -10% and +50%. *If failed*: flag "Implied growth outside economically plausible range — market may be pricing non-fundamental factors."

## Error Handling

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| No price data | Halt | "Current stock price unavailable for {ticker}." |
| Negative FCF | Flag — reverse DCF unreliable | "Negative free cash flow — reverse DCF may produce nonsensical results." |
| Non-convergence | Flag extreme assumptions required | "Reverse DCF did not converge within 50 iterations — market may be pricing extreme scenarios." |
