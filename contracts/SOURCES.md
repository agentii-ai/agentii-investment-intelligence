# SOURCES — Part II Data Source Registry

**Status**: Active contract | **Spec**: spec 039 Part II | **Drives**: `data-tools/_sources.py` `~~category` resolution + `check.py` license-boundary sub-check

Per-source metadata for every provider behind a `~~category` placeholder. `priority` = lower is tried first; scrapers get the highest number (last resort, R7). `invoke` = `import` (in-process, permissive license only) or `subprocess|mcp` (copyleft / heavy dep, run out-of-process per Constitution VIII).

## License boundary (Constitution VIII)

The MIT core (`data-tools/*.py`) MUST NOT `import` any AGPL/GPL package. Sources flagged `invoke: subprocess|mcp` are reached only via a separate process. `check.py` enforces an import denylist (`COPYLEFT_DENYLIST`).

## Phase A (MVP) — macro / market / earnings

| Source | Category | Auth | Env vars | License | invoke | Priority | ToS note |
|--------|----------|------|----------|---------|--------|----------|----------|
| FRED (`fredapi`) | `~~macro_data` | free_key | `FRED_API_KEY` | MIT | import | 10 | 120 req/min, 6000/day |
| OpenBB | `~~macro_data` | none | — | **AGPL-3.0** | **subprocess\|mcp** | 20 | ECB/IMF/OECD/BLS bridge; never imported. Takes **no env var** — `OPENBB_PAT` does not exist in openbb-core 1.6.0 |
| yfinance | `~~macro_data`, `~~market_data` | none | — | Apache-2.0 | import | 30 (macro) / 10 (market) | unofficial Yahoo. **Geo-blocked from mainland China** (Yahoo policy 2021-11-01) — see `testing-plan.md` §E.3 |
| **Nasdaq** (`api.nasdaq.com`) | `~~market_data` | none | — | unofficial | import | 20 | keyless daily OHLCV; verified 2026-09-17 from a CN network |
| **Sina** (`hq.sinajs.cn`) | `~~market_data` | none | — | unofficial | import | 25 | GBK-encoded, requires `Referer`; realtime quote + history to 1984 |
| **Tencent** (`qt.gtimg.cn`) | `~~market_data` | none | — | unofficial | import | 30 | GBK-encoded; **quote endpoint only** — its kline is positional with close third |
| secfin | `~~market_data` | none | — | MIT | import | 35 | US financials from SEC. Small/new (v1.0.0, 2026-02) — unproven |
| investpy | `~~market_data` | none | — | MIT | import | 60 | ⚠️ **DEAD** — Investing.com added Cloudflare; returns 403. Retained only for registry honesty |
| Finnhub (`finnhub-python`) | `~~market_data`, `~~economic_calendar` | free_key | `FINNHUB_API_KEY` | Apache-2.0 | import | 40 | 60 req/min **quotes only** — free tier excludes US OHLC history; ToS forbids business use even internally |
| **Alpaca** (`alpaca-py`) | `~~market_data` | free_key | `ALPACA_API_KEY`, `ALPACA_SECRET_KEY` | Apache-2.0 | import | 15 | 200 req/min, no daily cap, **true one-call batching**, daily→1min from 2016, free paper key with no card |
| Tiingo | `~~market_data` | free_key | `TIINGO_API_KEY` | MIT | import | 45 | 1,000 req/day; billed per HTTP request, not per ticker |
| Polygon.io / **Massive** | `~~market_data` | free_key | `POLYGON_API_KEY` | MIT (client) | import | 50 | **Rebranded to Massive**; `api.polygon.io` still serves the same API. `grouped_daily` returns the whole US market in one call |
| defeatbeta-api | `~~earnings_data` | none | — | Apache-2.0 | import | 10 | transcripts + fundamentals, zero-key |
| FMP (`fmpsdk`) | `~~earnings_data` | free_key | `FMP_API_KEY` | MIT | import | 20 | 250 req/day; estimates, calendar |
| Earnings Whispers (scraper) | `~~earnings_data` | none | — | scraper | import | 90 | ToS/breakage risk; last-resort (R7) |

## Phase 2 (deferred)

| Source | Category | Auth | Env vars | License | invoke | Priority |
|--------|----------|------|----------|---------|--------|----------|
| World Bank (`wbdata`) | `~~macro_data` | none | — | GPL-2.0 | **subprocess\|mcp** | 40 |
| BaoStock | `~~global_market_data` | none | — | BSD | import | 10 |
| AKShare | `~~global_market_data` | none | — | MIT | import | 20 |
| edgartools | `~~alternative_data` | none | — | MIT | import | 10 |
| Equibles (self-hosted) | `~~alternative_data` | self_hosted | `EQUIBLES_URL` | AGPL | **subprocess\|mcp** | 20 |
| Adanos | `~~alternative_data` | free_key | `ADANOS_API_KEY` | proprietary API | import | 30 |
| finlight | `~~alternative_data` | free_key | `FINLIGHT_API_KEY` | proprietary API | import | 40 |
| Apify Economic Calendar | `~~economic_calendar` | token | `APIFY_TOKEN` | proprietary API | import | 30 |
| FRED Release Calendar | `~~economic_calendar` | free_key | `FRED_API_KEY` | MIT | import | 10 |
| Fool.com (scraper) | `~~alternative_data` | none | — | scraper | import | 90 |

## Copyleft denylist (enforced by check.py)

Import of these package roots into `data-tools/` fails CI (`AGPL`/`GPL` contamination of MIT core):

- `openbb`
- `wbdata`
- any package whose declared license contains `AGPL` or `GPL` (non-LGPL)
