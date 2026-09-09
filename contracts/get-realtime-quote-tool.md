# get_realtime_quote MCP Tool Contract

`get_realtime_quote` provides market data for US equities via Yahoo Finance (Tier 1, zero-auth) with a future path to centralized Alpaca Markets data (Tier 2).

> **Reconciled 2026-09-08 (spec 046 T007)**: this contract previously promised 15 fields while the implementation delivered 3 — the Q71 divergence class (contract says 15, code delivers 3, `market_cap` returns float while the contract declares int). The field table below documents **delivered fields** with each growth step planned as its own task (spec 046 tasks T076). Reconciliation rule: shrink to reality, then grow — each new field lands with a test (Q44/R3).

## Tool Signature

```
get_realtime_quote(ticker: str) → QuoteResult
```

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `ticker` | Yes | string | Uppercase US equity ticker symbol |

## Response Shape (target — grows field by field, each with a test)

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
 "observed_at": "2026-06-05T16:00:00-04:00",
 "retrieved_at": "2026-06-05T16:01:12-04:00",
 "cache_age_seconds": 0,
 "data_class": "fast",
 "price_basis": "close",
 "source": "yahoo_finance",
 "stale": false
}
```

## Field Descriptions (delivery status)

| Field | Type | Unit | Status | Description |
|-------|------|------|--------|-------------|
| `ticker` | string | — | ✅ today | Uppercase ticker symbol |
| `last_close` | float | USD | ✅ today (as `price`) | Most recent closing price — the **pinnable** value. Sourced from `history()`'s daily close, NOT `fast_info.last_price` (spec 046 R3/Q71) |
| `market_cap` | int | USD | ✅ today (as float — int coercion in T076) | Market capitalization |
| `volume` | int | shares | 🔜 T076 (from `fast_info.lastVolume`) | Last trading day volume |
| `day_high` | float | USD | 🔜 T076 (`fast_info.dayHigh` exists now) | Day's high price |
| `day_low` | float | USD | 🔜 T076 (`fast_info.dayLow`) | Day's low price |
| `day_range` | string | — | 🔜 T076 (derived) | Human-readable day range |
| `ma_50` | float | USD | 🔜 T076 (`fiftyDayAverage` exists now) | 50-day simple moving average |
| `ma_200` | float | USD | 🔜 T076 (verify key name) | 200-day simple moving average |
| `pe_ttm` | float | — | 🔜 T076 (later batch) | Trailing 12-month P/E ratio |
| `eps_ttm` | float | USD | 🔜 T076 (later batch) | Trailing 12-month earnings per share |
| `dividend_yield` | float | decimal | 🔜 T076 (later batch) | Dividend yield (0.008 = 0.8%) |
| `beta` | float | — | 🔜 T076 (later batch) | 5-year monthly beta vs S&P 500 |
| `observed_at` | ISO 8601 | — | 🔜 T013 | **Exchange time of the quote itself** (Q71). From `history()`'s tz-aware `America/New_York` index. Missing ⇒ the quote may not be used in any pinned artifact (hard rule, Q71) |
| `retrieved_at` | ISO 8601 | — | 🔜 T013 | Our fetch/read time (Q71) — serves the Q20 restatement discriminator and Q44 TTL |
| `cache_age_seconds` | int | s | 🔜 T012 | Age of the served value on a cache hit (from the stored `stored_at`) |
| `data_class` | enum | — | 🔜 T015 | `slow` \| `fast` — market data is `fast` (never triggers rescan, Q72) |
| `price_basis` | enum | — | 🔜 T013 | `close` \| `intraday` — derived from `observed_at` ONLY (Q71). Interim: always `close` until a second quote source is wired (RISK-2) |
| `source` | string | — | ✅ today | Data source identifier |
| `stale` | boolean | — | ✅ today (cache semantics) | True when served from cache beyond TTL with the provider unreachable (Q44) |

## Data Source Architecture

### Tier 1 — Distributed (Current)
- **Source**: Yahoo Finance (yfinance `history()` for pinnable closes; `fast_info` for supplementary fields)
- **Authentication**: Zero-auth
- **Rate Limit**: ~2000 requests/hour per IP
- **Coverage**: All US-listed equities (NYSE, NASDAQ)
- **Cache**: `FileCache` category `market`, key `{category}:{data_type}:{ticker}:{period}:{interval}`; dual TTL by `data_type` — `quote` 15 min, `history` 24 h (Q44). All writes atomic (`tmp` + `os.replace`).

### Tier 2 — Centralized (Future)
- **Source**: Alpaca Markets Data API v2
- **Coverage**: 600-1000 tickers (curated universe) + options chains
- **Benefit**: No per-user rate limits; also the future home of `price_basis: intraday`

## Rate Limit Handling

1. First attempt: provider fetch
2. On 429: retry once after 2 seconds
3. Second failure: return cached data with `stale: true` + `cache_age_seconds`
4. No cache available: return structured error with guidance

## Freshness semantics

- TTL is a **performance parameter** (when to re-fetch); the 24 h ceiling is a **correctness gate** (when a price may no longer be used for a directional claim, Q41) — two independent layers.
- `stale: true` does **not** flip an artifact to `stale` (Q72: `data_class: fast` never triggers rescan); it only gates decision use via claim-level `stale_price`.

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

- Endpoint: `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1d` (`meta.regularMarketTime` is the `intraday`-capable `observed_at` source when the chart path is wired — RISK-2)
- The current `data-tools/market_data.py` uses the `yfinance` library path (`fast_info` + `history()`), not raw v8 calls; `observed_at` comes from `history()`'s index (T013)

## Cross-Reference

- **spec 046 tasks T012–T015, T076**: field delivery roadmap
- **get-price-history-tool.md**: the `early`-class counterpart (`get_price_history`)
- **global-stock-data**: Reference implementation for Yahoo Finance v8 zero-auth pattern
