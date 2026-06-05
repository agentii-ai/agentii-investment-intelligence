# Yahoo Finance Real-Time Price Data Setup

For Tier 1 distributed real-time US stock price data (FR-097). This is the local/development path. For production centralized data, see the Alpaca Markets upgrade path below.

## Overview

`get_realtime_quote` uses Yahoo Finance v8 API for last-day trading data. **Zero authentication required** — no API key signup, no account creation. The crumb authentication token is auto-managed by the tool.

## What You Get

| Field | Example (LLY) |
|-------|---------------|
| Last Close | $850.25 |
| Volume | 3,200,000 |
| Day Range | $845.00 - $855.50 |
| 50-Day MA | $820.30 |
| 200-Day MA | $780.15 |
| Market Cap | $810.5B |
| P/E (TTM) | 55.2x |
| EPS (TTM) | $15.40 |
| Dividend Yield | 0.8% |
| Beta (5yr) | 0.42 |

## Setup

**No setup required.** The tool is pre-configured for zero-auth access.

## Rate Limits

Yahoo Finance v8 API limits requests per IP address:
- ~2,000 requests per hour per IP
- ~50,000 requests per day per IP

For individual use (running 5-10 analyses per day), this is more than sufficient. If you're behind a corporate NAT or VPN sharing an IP with other users, rate limits may be shared. In that case, the tool falls back to cached data with a `stale: true` flag.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 429 "Too Many Requests" | Rate limit hit | Wait 60 seconds; tool auto-retries once after 2s |
| Stale data flag | Cached data served during rate limit | Check `timestamp` field for data age |
| No data for ticker | Ticker delisted or Yahoo symbol mismatch | Verify ticker on Yahoo Finance website |

## Upgrade Path: Alpaca Markets (Tier 2 — Future)

For production/professional use, agentii.ai will offer centralized Alpaca Markets data:
- **600-1000 US tickers** with daily OHLCV history
- **Options chains** with Greeks
- **No per-user rate limits**
- **Historical series** for backtesting and factor research

When available, `get_realtime_quote` automatically checks the centralized source first and falls back to Yahoo Finance. No configuration change needed.

## Cross-Reference

- **FR-097**: Two-tier real-time price data architecture
- **FR-105**: get_realtime_quote MCP tool contract
- **global-stock-data**: Reference implementation at `github.com/simonlin1212/global-stock-data`
