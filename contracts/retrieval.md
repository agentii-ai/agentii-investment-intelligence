# Retrieval Strategy (canonical, skill-facing)

Canonical retrieval decision tree + three-layer document protocol that every
skill body references. Authoritative source: the retrieval subagent system
prompt at `managed-agent-cookbooks/agentii-equity-agent/subagents/system-prompts/retrieval.md`
(this file is the skill-facing distillation; keep the two in sync).

## Pre-Flight Step 0 — Ticker Resolution

Before any data-fetching call, resolve the user-supplied ticker via the
three-layer fallback against `gold.entity_aliases` (handled by `search_companies`):

1. **Exact match** — `search_companies(ticker=<input>)` against `gold.companies`.
2. **Fuzzy alias match** — share-class variants (GOOGL→GOOG, BRK.A→BRK.B), former
   names (FB→META, SQ→XYZ), Bloomberg/NYSE suffixes (`SQ.N` → strip `.N`/`.O`/`.K`).
3. **Share-class normalization** — multi-class tickers map to the primary ticker
   (most SEC filing history); the response carries `shares_outstanding` per class.

Output: `canonical_ticker`, `match_method` (`exact`|`alias`|`share_class`),
`confidence`. On total failure, surface the top-3 fuzzy suggestions. This adds
zero extra calls when `search_companies` is already in `allowed_tools`.

## Decision Tree — select ONE branch before the first tool call

**Batch rule (all branches)**: 3+ independent queries of the same tool type →
consolidate into one `batch_search` (≤8 sub-queries). Fall back to sequential on
`PROXY_ERROR`.

- **Branch (a) — Structured data** (Revenue, EPS, EBITDA, margins, BS/CF line
  items): use `search_xbrl_facts`. `is_primary = true` is the default (dedup
  across 8-K/10-Q/10-K); pass `?include_all_sources=true` only for audit-grade
  reconciliation. Use the `view` parameter for dimensional control:
  `view=standard` (default, consolidated totals), `view=detailed` (segment /
  product / geography members with `dimension_axes`), `view=summary` (totals
  only). Discover non-standard concepts via `list_xbrl_concepts`; standard
  US-GAAP concepts (`Revenues`, `NetIncomeLoss`, `OperatingIncomeLoss`,
  `GrossProfit`, `Assets`, `EarningsPerShareDiluted`, …) may be queried directly.
  Optionally call `get_statement_structure` for hierarchical concept navigation.
- **Branch (b) — Multi-period unstructured** (qualitative data spanning 2+ fiscal
  periods): `get_company_fiscal_calendar/{ticker}` → build `fiscal_periods` →
  ONE `search_cross_period(ticker, query, fiscal_periods)` call (server-side
  parallel dispatch across the full 10-K/10-Q/8-K/6-K/20-F surface) → verify
  cross-period consistency.
- **Branch (c) — Single period / single document**: direct `read_source_outline`
  (Layer 2) → `read_source_pages` (Layer 3). No parallel delegation.
- **Branch (d) — Simple lookup** (company name, sector, earnings date):
  `get_company_profile` / `search_earnings_calendar`. Zero document retrieval.

## Three-Layer Document Protocol

Apply whenever the candidate document set exceeds 1 filing / 50 pages and the
answer pages are not known in advance.

- **Layer 1 — Discovery**: `search_documents` (single canonical entry point;
  returns `citation_id`, `ticker`, `form_type`, `filing_date`, `secondary_labels`)
  / `search_sec_filings` (filing-metadata only) / `list_sources`. Always search
  both US and foreign forms: annual/quarterly = `form_type=["10-K","10-Q","20-F"]`,
  material events = `form_type=["8-K","6-K"]`. Narrow with `?secondary_label=` when
  the disclosure-type axis is known.
- **Layer 2 — Page map**: `read_source_outline/{ticker}/{citation_id}` returns
  per-page `description` + `keywords` without `page_content` (~5K tokens for a
  200-page filing). NULL `description` = not financially relevant — skip, never
  deep-read. Escalate to `read_source_deep_outline` (`table_titles`, `drivers`,
  `metrics`, `views`) only when lightweight labels can't disambiguate (~5% of
  filings; `unstructured_document_search` scope only). Optional
  `search_keyword_in_source` narrows >10-page candidate sets.
- **Layer 3 — Deep read**: `read_source_pages/{ticker}/{citation_id}?row_numbers=page<N1>,page<N2>`
  loads `page_content` for ONLY the Layer-2-selected pages. Page identifiers MUST
  use the `page<N>` format — bare integers are rejected.

**Degradation mode**: if both Layer 2 and Layer 3 are unavailable, downgrade to
Layer 1 metadata + `search_keyword_in_source`, flag
`document_access_degraded: true` and `three_layer_protocol: bypassed`, surface
the gap, and do NOT halt.

## Page References & Citations

Always use `{ticker} {citation_id} page<N>` (e.g., `LLY sec135 page12`) as the
citation label; bare `page_no` integers are forbidden in LLM-facing text. Every
citation MUST also carry the clickable `/v/` link — see
`contracts/citation-and-memory.md`.

## Fiscal Period Conventions

Annual = `FYxx` (e.g., `FY24`); quarterly = `yyyyQx` (e.g., `2025Q4`). For
multi-period search, call `get_company_fiscal_calendar/{ticker}` and
cross-validate the claimed FYE month against the most recent XBRL `period_end`;
trust the XBRL dates on mismatch and flag `fiscal_calendar_mismatch`. Skip for
`structured_only` / `simple_lookup` scopes.
