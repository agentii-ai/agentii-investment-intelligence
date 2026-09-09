# get_price_history MCP Tool Contract

`get_price_history` returns daily OHLCV bars for technical-analysis skills (`market_data_stage: early`) — the PTM methodology needs 20/60/120/250-day series that `get_realtime_quote` cannot provide (spec 046 Q42). Source: yfinance `history()` (zero-auth, same provider as the quote tool).

## Tool Signature

```
get_price_history(ticker: str, period: str = "1y", interval: str = "1d") → PriceHistoryResult
```

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `ticker` | Yes | string | Uppercase US equity ticker symbol |
| `period` | No | string | yfinance period (`1mo`/`3mo`/`6mo`/`1y`/`2y`/`5y`/`max`); default `1y` |
| `interval` | No | string | yfinance interval; default `1d` |

## Response Shape

```json
{
  "ticker": "NVDA",
  "period": "1y",
  "interval": "1d",
  "bars": [
    {"date": "2026-06-01", "open": 128.5, "high": 131.2, "low": 127.1, "close": 130.4, "volume": 52000000}
  ],
  "observed_at": "2026-09-08T16:00:00-04:00",
  "retrieved_at": "2026-09-08T16:01:12-04:00",
  "source": "yahoo_finance",
  "stale": false
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | string | Uppercase ticker symbol |
| `period` / `interval` | string | Echoed request parameters (cache-key components) |
| `bars[]` | array | Daily OHLCV bars, **date ascending** |
| `bars[].date` | ISO 8601 date | Exchange date (tz-aware `America/New_York` index of `history()`) |
| `bars[].open/high/low/close` | float | **No None values** — rows with missing closes are dropped, never zero-filled (None-vs-0 semantics: a zero is a price, a None is an absence) |
| `bars[].volume` | int | Daily volume |
| `observed_at` | ISO 8601 | Last bar's exchange time — the quote-side Q71 rule applies |
| `retrieved_at` | ISO 8601 | Our fetch/read time |
| `source` | string | Data source identifier |
| `stale` | boolean | True when served from cache beyond TTL with the provider unreachable |

## Error semantics

| Condition | Error |
|---|---|
| Fewer than 20 bars for the requested period | `INSUFFICIENT_HISTORY` (Q42 — SMA(20) is the minimum computable window; refuse rather than compute) |
| Provider unavailable, no cache fallback | `SOURCE_UNAVAILABLE` (envelope convention) |
| No data for ticker | `NOT_FOUND` (envelope convention) |

## Access rules (Q41/Q42)

- `get_price_history` is **`early`-class only** — it is never in a `late` skill's `allowed_tools` (G1 enforces: `early` must include it; `late` must include `get_realtime_quote` and NOT this tool).
- Cache: `FileCache` category `market`, data_type `history`, TTL 24 h (Q44).
