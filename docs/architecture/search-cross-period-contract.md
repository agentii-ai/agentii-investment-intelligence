# Search Cross Period Contract (v1.0)

Documents `search_cross_period` partial failure semantics, internal sub-batching, and credit metering per the partial failure semantics contract and the concurrency limit/the concurrency limita.

## Endpoint Contract

`POST /v1/search_cross_period` ( the /v1/search_cross_period endpoint):

```json
{
 "ticker": "LLY",
 "query": "analyze management commentary on revenue growth drivers",
 "fiscal_periods": ["2025Q1", "2025Q2", "2025Q3", "2025Q4", "FY2024", "FY2023"],
 "source_types": ["sec_8k", "sec_6k", "sec_filing", "earnings_call_transcript"]
}
```

## Partial Failure Semantics

When some period sub-queries succeed and others fail, `search_cross_period` returns **partial success**:

- **Successful periods**: included with `"status": "ok"` and their full data payload.
- **Failed periods**: listed in the top-level `coverage_attestation.gaps[]` with:
 - `fiscal_period`: the period label (e.g., `"FY2023"`)
 - `failure_reason`: one of `no_filings_for_period`, `rate_limited`, `timeout`, `empty_xbrl_facts`
 - `attempted_actions`: what was tried before failing
- **Empty periods**: `"status": "ok"` with empty `data` array and `total_count: 0` — not an error.
- **HTTP status**: 200 regardless (partial success per the concurrency limit).

The retrieval-subagent then follows the existing the retrieval gaps failure policy:

1. Retry ONCE with broadened time window.
2. If gaps remain, proceed with `## Coverage Gaps` section in the output.
3. Never silently drop failed periods.

## Internal Sub-Batching

`search_cross_period` fans out period sub-queries concurrently, bounded by the Neon connection pool:

- **Max concurrent**: 8 ( the concurrency limit).
- **Max total periods**: 20.
- **Batching example**: 20 periods execute as 3 batches (8 + 8 + 4).
- **Transparency**: skills treat `search_cross_period` as a single blocking call regardless of batch count.
- **Latency**: scales with batch count (20 periods ≈ 3× single-batch latency).

The `temporal_scope.max_quarters` per-skill ceiling (the temporal scope contract) caps the `fiscal_periods` list length at the skill layer — independent of the Neon connection pool cap.

## Credit Metering

Follows `batch_search` precedent ( credit metering rules):

- Each successful per-period result consumes **1 credit**.
- Periods returning `DATA_NOT_AVAILABLE` consume **0 credits**.
- Periods returning empty results (status: ok, total_count: 0) consume **1 credit**.
- Example: 12 fiscal_periods where 10 succeed, 1 is empty, 1 is P2-unavailable = **11 credits** (10 successful + 1 empty).

## Common Failure Reasons

| Code | Meaning | Recovery |
|------|---------|----------|
| `no_filings_for_period` | No SEC filings in `pipeline.src_documents` for that period | Proceed with gap |
| `rate_limited` | Period sub-query hit API rate limit | Retry once after backoff |
| `timeout` | Period sub-query exceeded SC-008 latency budget | Retry once |
| `empty_xbrl_facts` | XBRL data not yet populated for that ticker+period | Use documents instead |

## Pre-Retrieval Step

Before calling `search_cross_period`, the retrieval-subagent MUST:

1. Call `get_company_fiscal_calendar/{ticker}` ( fiscal calendar endpoint) to resolve the company's fiscal period format (`"FY"` vs `"Q<N>"`).
2. Optionally call `search_earnings_calendar(ticker)` ( earnings calendar search endpoint) for exact report dates.
3. Construct the `fiscal_periods` list using the resolved format labels.
