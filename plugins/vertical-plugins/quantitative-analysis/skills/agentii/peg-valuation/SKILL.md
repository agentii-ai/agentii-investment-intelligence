---
name: peg-valuation
multi_ticker_semantics: target_with_optional_peers
description: PEG valuation, Price Earnings to Growth ratio, Peter Lynch PEG methodology, growth-adjusted valuation, earnings growth rate, PE ratio valuation, PEG sector comparison, undervalued growth stocks, fair value PEG
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Trailing 4 quarters for current PE; up to 12 for historical CAGR"
allowed_tools:
 - search_xbrl_facts
 - search_companies
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 4
---

# PEG Valuation

Peter Lynch PEG (Price/Earnings to Growth) methodology. PEG = P/E Ratio ÷ Earnings Growth Rate (%). Growth-adjusted valuation that answers: "Is this stock's growth justifying its multiple?"

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides.

**`get_realtime_quote` availability **: If `get_realtime_quote` is not yet deployed, prompt user for current stock price. PE numerator from `search_earnings_calendar` (NTM consensus EPS × current price = PE) as fallback.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- PEG valuation for {ticker}
- compute PEG ratio {ticker}
- Peter Lynch PEG {ticker}
- growth-adjusted valuation {ticker}
- is {ticker} undervalued by PEG
- PEG analysis {ticker}
- price earnings growth {ticker}
- compare PEG across peers
- {ticker} PEG vs sector
- growth at reasonable price {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| growth_source | consensus | consensus estimates preferred; fallback to historical CAGR |
| include_peers | true | Sector PEG comparison |
| lookback_years | 3 | Historical CAGR computation window |

## Methodology

### Retrieval Scope

`structured_only` — PEG uses XBRL earnings data + real-time price + earnings calendar for growth estimates.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts`.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_earnings_calendar`.

### Temporal Scope

Default: 4 fiscal quarters (max 12). PEG uses trailing 4 quarters for LTM P/E; up to 12 for historical EPS CAGR if consensus unavailable.

### Tool Allowlist

See frontmatter `allowed_tools` — 4 tools. `get_realtime_quote` for current price + PE (TTM). `search_earnings_calendar` for consensus EPS and long-term growth estimates. `search_xbrl_facts` for historical EPS to compute CAGR. `search_companies` for peer identification.

### Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Price data**: `get_realtime_quote(ticker)` → current stock price, PE (TTM), market cap, EPS (TTM).
3. **Consensus estimates**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest+1])` → consensus EPS (current year, next year), long-term growth rate estimate.
4. **Historical EPS (fallback)**: if consensus growth unavailable, `search_xbrl_facts(ticker, concept=["EarningsPerShareDiluted"], fiscal_year=[latest, latest-1, latest-2, latest-3, latest-4])` → compute 3yr and 5yr EPS CAGR.
5. **Compute PEG**:
 - PEG (LTM) = PE_TTM ÷ Consensus LTG (%)
 - PEG (NTM) = PE_NTM ÷ Consensus LTG (%)
 - PEG (Historical) = PE_TTM ÷ EPS CAGR_3yr (%)
6. **Peer PEG comparison**: `search_companies` for sector peers → get PE + growth for each → compute peer PEGs → mean/median/high/low comparison.
7. **Output**: per with YAML frontmatter .

### PEG Interpretation (Peter Lynch Framework)

| PEG Range | Rating | Investment Implication |
|-----------|--------|----------------------|
| < 0.5 | Deeply Undervalued | Growth vastly exceeds valuation; investigate for hidden risks |
| 0.5 – 1.0 | Undervalued | Classic Lynch buy zone; growth justifies the multiple |
| 1.0 – 1.5 | Fairly Valued | Growth and valuation in equilibrium |
| 1.5 – 2.0 | Premium | Market paying up for growth; needs above-consensus execution |
| > 2.0 | Overvalued | Growth insufficient to justify current multiple |
| Negative | N/A | Negative earnings — PEG not meaningful; use revenue-based metrics |

## Output File

Write to `{ticker}/{YYYY-MM-DD_HHMM}_peg-valuation_growth-adjusted.md` .

## Output Structure

1. **Executive Summary** — PEG (LTM + NTM), rating, 1-sentence investment implication
2. **PEG Computation** — P/E numerator breakdown (LTM, NTM), growth rate denominator (source: consensus or historical CAGR), PEG result
3. **Growth Rate Analysis** — consensus LTG vs historical CAGR, growth quality assessment (sustainable? accelerating? decelerating?)
4. **Sector PEG Comparison** — peer PEG table with mean/median/high/low, target's percentile rank
5. **Sensitivity** — PEG at varying growth rates (±5%, ±10%, ±20% from base case)
6. **Limitations** — PEG not meaningful for cyclical, negative earnings, or zero-growth companies
7. **Coverage Gaps & Citations** — data sources + citation index

**Citation density**: ≥1 citation per 200 words. **Citation link format **: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md`.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `search_earnings_calendar` | No consensus LTG | Use historical EPS CAGR from XBRL | "Consensus growth unavailable; using 3yr historical EPS CAGR" |
| `get_realtime_quote` | Rate limit | Use latest quarter EPS from XBRL + manual price input prompt | "Real-time price unavailable; prompt user for current price" |
| Negative earnings | PE < 0 | Flag "PEG not meaningful"; suggest EV/Revenue or P/S | "Negative earnings — PEG not applicable" |

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|-------------|-----------|--------|---------------------|
| Missing data | No consensus or historical EPS | Halt; cannot compute growth rate | "Insufficient earnings data to compute growth rate for {ticker}." |
| Negative earnings | PE (TTM) < 0 | Compute only revenue-based metrics; flag PEG as N/A | "PEG not applicable — {ticker} has negative earnings." |
| Zero growth | CAGR ≈ 0% | PEG = ∞; flag as "no growth" case | "Zero historical EPS growth — PEG effectively infinite." |
| MCP unreachable | Preflight probe fails | Halt | "agentii data plane unreachable; check connection." |
