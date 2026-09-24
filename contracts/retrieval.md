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
  items): use `search_xbrl_facts`. `is_primary = true` is the default (dedup per
  namespace — dual-filers can have a primary per namespace, so pass
  `namespace=us-gaap` for US filers or `namespace=ifrs-full` for foreign);
  pass `?include_all_sources=true` only for audit-grade reconciliation.
  Use the `view` parameter for dimensional control:
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
  material events = `form_type=["8-K","6-K"]`, earnings calls =
  `form_type=["earnings_call_transcript"]` (citation prefix `ect<N>`; pages carry
  `section_type` prepared_remarks/qa/closing as session_title and guidance/
  forward_looking/analyst_questions in labels). Ownership signals: `search_institutional_holdings`
  (top-10 holders + whale portfolios per ticker, `direction=accumulating|reducing|new|exited`) and
  `search_insider_trades` (Form-4 officer/director/10% owner transactions with SEC filing URLs).
  Narrow with `?secondary_label=` when the disclosure-type axis is known.
- **Layer 2 — Page map**: `read_source_outline/{ticker}/{citation_id}` returns
  per-page `description` + `description_provenance` + `keywords` without `page_content`.
  **Cost is measured, not estimated: 72 tokens/page (spec 062 `T030`, 2026-09-23), so 200 pages
  is ~14,400 tokens** — and the map has **no filter and no pagination**, so a 2,000-page filing
  is ~136,264 tokens in one call. Budget for that before calling it on a long filing.
  **`description` is PLATFORM-GENERATED — never the filing's own words.** `description_provenance`
  says which kind: `platform_summary` (a model summarised the page) or
  `platform_metadata_placeholder` (no summary exists; the string is derived from the filing
  metadata and carries no content). **Never quote a `description` as the issuer's text**, and a
  placeholder is **not** a reason to skip a page — it is a reason to read it. Escalate to
  `read_source_deep_outline` (`table_titles`, `drivers`, `metrics`, `views`) when lightweight
  labels can't disambiguate (`unstructured_document_search` scope only; the escalation rate is
  **unmeasured** — 062's audit records the old "~5% of filings" as an assertion with no producer).
- **Layer 2.5 — Keyword filter**: `search_keyword_in_source` narrows >10-page candidate sets, and
  **its rows now carry `matched_span`** — the verbatim page text that satisfied the predicate, with
  the matched terms marked `<b>…</b>` (spec 062 `T037`). **Quote the `matched_span`, never the
  `description` beside it**: the predicate matches the issuer's text, and the description is the
  platform's summary of it. Citations written from the description are the measured fabrication
  population (19.18% HARD+leaning through this tool, against 0.54% through `read_source_pages` —
  062 `T031`, 1,422 citations). If a row's `matched_span` does not actually support the claim, the
  match was a stem-level coincidence and the page should not be cited for it.
- **Layer 3 — Deep read**: `read_source_pages/{ticker}/{citation_id}?pages=page<N1>,page<N2>`
  loads `page_content` for ONLY the Layer-2-selected pages. Page identifiers MUST
  use the `page<N>` format — bare integers are rejected. **This is the tool to quote from** — its
  text is the issuer's, and its citations are the ones that survive a check.

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
