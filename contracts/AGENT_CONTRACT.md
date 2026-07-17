# AGENT_CONTRACT — Part II Tool Response Envelope

**Status**: Active contract | **Spec**: spec 039 Part II | **Applies to**: all `data-tools/*.py` + unified agentii MCP tools

> **Path note (spec 039 impl)**: Python data scripts live under `data-tools/` (the package's `tools/` directory is the shipped TypeScript MCP server). Every reference to `tools/*.py` in the spec maps to `data-tools/*.py` here.

Every Part II data tool — whether a local `data-tools/*.py` script or a unified-MCP tool — MUST return a single JSON object conforming to this envelope. This gives skills one uniform shape to parse across 20+ sources and 6 categories, and enables graceful degradation and per-category failover.

## Envelope

```json
{
  "status": "ok | degraded | error",
  "data": {},
  "source": "fred | yfinance | defeatbeta-api | fmp | openbb | ...",
  "cache_hit": false,
  "rate_limit_remaining": 118,
  "error": null
}
```

## Field semantics

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `status` | enum | yes | `ok` = full data; `degraded` = partial/fallback data (e.g., zero-key path, stale cache); `error` = no data |
| `data` | object\|array\|null | yes | Payload. Where it represents quotes/options/financials, it MUST map to the shared Pydantic types in `agentii/models/` (Constitution I). `null` iff `status=error` |
| `source` | string | yes (unless error) | Concrete provider actually used behind the `~~category` placeholder |
| `cache_hit` | bool | yes | `true` if served from `~/.agentii/cache` |
| `rate_limit_remaining` | int\|null | yes | Provider-reported remaining calls; `null` if unknown |
| `error` | string\|null | yes | Human-readable reason; present iff `status ∈ {degraded, error}` |

## Invariants

1. `status=ok` ⇒ `data != null`.
2. `status=error` ⇒ `data = null` AND `error != null`.
3. `status=degraded` ⇒ `data` may be partial AND `error` explains why (e.g., `"FRED key missing; used yfinance fallback"`).
4. `source` is always one of the category's registered sources in `_sources.py`.

## Category placeholders

Skills reference categories, never vendors:

| Placeholder | Script | Primary source (zero-key) |
|-------------|--------|---------------------------|
| `~~macro_data` | `data-tools/macro_data.py` | FRED (key) → OpenBB → zero-key fallback |
| `~~market_data` | `data-tools/market_data.py` | yfinance (zero-key) |
| `~~earnings_data` | `data-tools/earnings_data.py` | defeatbeta-api (zero-key) |
| `~~alternative_data` | `data-tools/alternative_data.py` (Phase 2) | edgartools (zero-key) |
| `~~economic_calendar` | `data-tools/economic_calendar.py` (Phase 2) | FRED release calendar |
| `~~global_market_data` | `data-tools/global_market_data.py` (Phase 2) | AKShare/BaoStock (zero-key) |

## Failover & caching

- On rate-limit or source error: exponential backoff, then failover to the next source (by `priority`) in the same category. The `source` field reports whichever succeeded.
- Cache is checked first; `cache_hit=true` short-circuits network calls when within the category TTL.

## Error taxonomy (in `error`)

- `API_KEY_MISSING` — no key; degraded path used or error.
- `RATE_LIMITED` — provider limit hit; failover attempted.
- `SOURCE_UNAVAILABLE` — network/endpoint failure.
- `NOT_FOUND` — query returned no data.
- `SCRAPER_BLOCKED` — scraper fallback blocked by ToS/anti-bot (R7).

## Machine-checkable schema

The normative JSON Schema lives at `contracts/envelope.schema.json`. CI validates every tool response against it (deterministic fixtures, R10).
