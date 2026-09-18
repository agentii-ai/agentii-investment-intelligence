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
| yfinance | `~~macro_data`, `~~market_data` | none | — | Apache-2.0 | import | 30 (macro) / **90** (market) | unofficial Yahoo. **NEGATIVE CONTROL** as of 2026-09-18 — was priority 10, i.e. the default, while being the one market source measured as failing. See the egress-scope note below before reading anything into a 403. |
| **Nasdaq** (`api.nasdaq.com`) | `~~market_data` | none | — | unofficial | import | **30** | **KEYLESS PRIMARY** (T179). Daily OHLCV, no key and no signup. Measured OK 2026-09-17: AAPL 332.41, 3656 ms. |
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

## Egress scope — READ THIS BEFORE INTERPRETING A FAILURE (T183, Q104)

**Our users are in the US and the EU. The Chinese firewall is explicitly OUT OF
SCOPE and must not drive provider choice.** This is a stated product constraint,
not an inference.

It matters because the provider ordering was previously justified by the WRONG
axis. The comments this replaced read *"geo-blocked from CN"* and *"verified
reachable from CN"* — so Yahoo sat at priority 10 (the default) while being the
one market source measured as failing, and the keyless sources were ranked by
Chinese reachability rather than by whether they serve our users.

### Yahoo reports two different failures, and only one is ours

`live-data-provider.md` §1 separates them and says which is which:

| Failure | Cause | In scope? |
|---|---|---|
| **HTTP 403, 3369-byte block page** | Yahoo withdrew from mainland China on 2021-11-01; the block is applied at their edge by geolocation. `curl_cffi` impersonating chrome/safari/firefox all return it. It will never clear by retrying or tuning headers. | **NO** — a CN-egress artifact. This is the case the user said not to design around. |
| **HTTP 429, 19-byte body, persistent** | Via a US proxy (Spokane WA), `finance.yahoo.com` loads (200, 1.02 MB) but every API host throttles from a **US datacenter IP** — ~12 requests over 4+ minutes, all 429. | **YES** — not a geography problem, and it affects real users. |

The document's own words: *"Fixing the geography alone is not sufficient — this is
the single most important correction to the picture."* **A proxy is not a fix for
Yahoo**, and a future reader who sees "Yahoo 403" must not conclude Yahoo is
broken for the actual users.

### What follows from the scope

- **Provider choice is ordered by US/EU service quality**, measured — see
  `data-tools/_sources.py`, reordered 2026-09-18.
- **Yahoo stays, last, as a negative control** (T181). Its assertion is that it
  fails CLEANLY — a structured refusal, never a traceback. A source that is
  known-unreachable is still worth asserting, because an unstructured failure
  from it would corrupt the failover path for the sources that DO work.
- **A missing API key is SKIPPED, never a failure** (T180). Five of the nine
  declared market sources take no key at all, so on a machine with no keys the
  zero-key path is not a fallback — it is the whole path.


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
