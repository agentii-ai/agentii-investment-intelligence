# get_realtime_quote MCP Tool Contract

`get_realtime_quote` provides last-day trading data for US equities via Yahoo Finance v8 API (Tier 1, zero-auth) with a future path to centralized Alpaca Markets data (Tier 2).

## Tool Signature

```
get_realtime_quote(ticker: str) → QuoteResult
```

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `ticker` | Yes | string | Uppercase US equity ticker symbol |

## Response Shape

```json
{
 "ticker": "LLY",
 "last_close": 850.25,
 "volume": 3200000,
 "day_high": 855.50,
 "day_low": 845.00,
 "day_range": "845.00 - 855.50",
 "ma_50": 820.30,
 "ma_200": 780.15,
 "market_cap": 810500000000,
 "pe_ttm": 55.2,
 "eps_ttm": 15.40,
 "dividend_yield": 0.008,
 "beta": 0.42,
 "timestamp": "2026-06-05T16:00:00-04:00",
 "source": "yahoo_finance",
 "stale": false
}
```

## Field Descriptions

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `ticker` | string | — | Uppercase ticker symbol |
| `last_close` | float | USD | Most recent closing price |
| `volume` | int | shares | Last trading day volume |
| `day_high` | float | USD | Day's high price |
| `day_low` | float | USD | Day's low price |
| `day_range` | string | — | Human-readable day range |
| `ma_50` | float | USD | 50-day simple moving average |
| `ma_200` | float | USD | 200-day simple moving average |
| `market_cap` | int | USD | Market capitalization |
| `pe_ttm` | float | — | Trailing 12-month P/E ratio |
| `eps_ttm` | float | USD | Trailing 12-month earnings per share |
| `dividend_yield` | float | decimal | Dividend yield (0.008 = 0.8%) |
| `beta` | float | — | 5-year monthly beta vs S&P 500 |
| `timestamp` | ISO 8601 | — | Timestamp of last data refresh |
| `source` | string | — | Data source identifier |
| `stale` | boolean | — | True if data is from cache (not live) |

## Data Source Architecture

### Tier 1 — Distributed (Current)
- **Source**: Yahoo Finance v8 API
- **Authentication**: Zero-auth (crumb auto-managed per global-stock-data pattern)
- **Rate Limit**: ~2000 requests/hour per IP (distributed across users)
- **Coverage**: All US-listed equities (NYSE, NASDAQ)
- **Latency**: ~200-500ms per call

### Tier 2 — Centralized (Future)
- **Source**: Alpaca Markets Data API v2
- **Coverage**: 600-1000 tickers (curated universe) + options chains
- **Storage**: Daily OHLCV recorded in Neon PostgreSQL
- **Benefit**: No per-user rate limits, historical series available for backtesting
- **Fallback**: Tier 2 checks first → Tier 1 if unavailable

## Rate Limit Handling

1. First attempt: Yahoo Finance v8 API
2. On 429 (Too Many Requests): retry once after 2 seconds
3. Second failure: return cached data with `stale: true` flag
4. Third failure: return error with guidance message

```
Error response:
{
 "error": "RATE_LIMITED",
 "message": "Real-time quote temporarily unavailable. Retry in 60 seconds or upgrade to agentii.ai for centralized data access.",
 "retry_after_seconds": 60
}
```

## Skills That Use get_realtime_quote

| Skill | Vertical | What It Uses |
|-------|----------|-------------|
| `ratio-analysis` | quantitative-analysis | Current price for P/E, P/B, P/S, PEG ratios |
| `peg-valuation` | quantitative-analysis | Current price for PEG computation |
| `reverse-dcf` | quantitative-analysis | Current price as DCF target for implied growth solving |
| `ddm-valuation` | quantitative-analysis | Current price + dividend yield |
| `residual-income` | quantitative-analysis | Current price + beta for CAPM |
| `valuation-methods` | equity-research-core | Current price for multiples comparison (via sub-skill) |

## Yahoo Finance v8 Implementation Notes

Based on the global-stock-data pattern:
- Endpoint: `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1d`
- Crumb: auto-obtained from `https://query1.finance.yahoo.com/v1/test/getcrumb`
- Cookie: session cookie required alongside crumb
- The crumb+cookie pattern must be implemented in the MCP tool backend

## Cross-Reference

- ****: Two-tier real-time price data architecture
- ****: Financial ratio analysis skill (consumer)
- ****: PEG valuation skill (consumer)
- ****: This contract
- **global-stock-data**: Reference implementation for Yahoo Finance v8 zero-auth pattern
