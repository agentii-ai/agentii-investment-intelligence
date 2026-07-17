# SOURCES — Part II Data Source Registry

**Status**: Active contract | **Spec**: spec 039 Part II | **Drives**: `data-tools/_sources.py` `~~category` resolution + `check.py` license-boundary sub-check

Per-source metadata for every provider behind a `~~category` placeholder. `priority` = lower is tried first; scrapers get the highest number (last resort, R7). `invoke` = `import` (in-process, permissive license only) or `subprocess|mcp` (copyleft / heavy dep, run out-of-process per Constitution VIII).

## License boundary (Constitution VIII)

The MIT core (`data-tools/*.py`) MUST NOT `import` any AGPL/GPL package. Sources flagged `invoke: subprocess|mcp` are reached only via a separate process. `check.py` enforces an import denylist (`COPYLEFT_DENYLIST`).

## Phase A (MVP) — macro / market / earnings

| Source | Category | Auth | Env vars | License | invoke | Priority | ToS note |
|--------|----------|------|----------|---------|--------|----------|----------|
| FRED (`fredapi`) | `~~macro_data` | free_key | `FRED_API_KEY` | MIT | import | 10 | 120 req/min, 6000/day |
| OpenBB | `~~macro_data` | free_key (per-provider) | `OPENBB_*` | **AGPL-3.0** | **subprocess\|mcp** | 20 | ECB/IMF/OECD/BLS bridge; never imported |
| yfinance | `~~macro_data`, `~~market_data` | none | — | Apache-2.0 | import | 30 (macro) / 10 (market) | unofficial Yahoo; zero-key fallback |
| secfin | `~~market_data` | none | — | MIT | import | 20 | US financials from SEC |
| investpy | `~~market_data` | none | — | MIT | import | 30 | 39,952 global stocks |
| Finnhub (`finnhub-python`) | `~~market_data`, `~~economic_calendar` | free_key | `FINNHUB_API_KEY` | Apache-2.0 | import | 40 | 60 req/min |
| Polygon.io | `~~market_data` | free_key | `POLYGON_API_KEY` | MIT (client) | import | 50 | real-time US |
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
