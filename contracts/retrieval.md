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
  items): resolve the period first with `resolve_period`, then pass its
  `period_id` to `search_xbrl_facts`. `is_primary = true` is the default (dedup per
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
  periods): `resolve_period(ticker, expression, as_of?)` for each requested
  period → collect the fiscal `period_id`s → ONE
  `search_cross_period(ticker, query, period_ids=[...])` call (server-side
  parallel dispatch across the full 10-K/10-Q/8-K/6-K/20-F surface) → verify
  cross-period consistency. `get_company_fiscal_calendar` supplies declared
  periods and gaps, never a month-derived quarter.
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

## Context management (long conversations, long documents)

The provider evicts tool results when the context grows. This protocol fires **before** that
eviction, so the acting model chooses what survives instead of discovering afterwards what did not.

- **Trigger at ~100K tokens; warn at ~90K.** The warning must precede the eviction a harness actually
  performs — a warning at 90% of 128K (≈115K) fires *after* a provider that evicts at ~100K has already
  dropped the evidence. The 128K/90% pair is the harness-table figure, not the operative number.
- **Warn-before-evict.** When the answer is *which evidence is at risk*, write it to memory **first** —
  the figure, the period, and the citation (`{ticker} {citation_id} page<N>`) — then let the tool
  results go. An eviction you did not prepare for cannot be recovered by re-reading a page you can no
  longer name.
- **Keep cited evidence.** A tool result the answer already cites is not evictable; compress the ones
  that were read and not used.
- **The acting model chooses.** Eviction is the agent's decision, not a fixed policy: only it knows
  which document it is mid-way through.
- **Replacement, not deletion.** Evict in place with a recoverable archive — a summary that names the
  source, so the raw page can be re-read.
- **Immune:** user instructions and the assistant's own messages are never evicted.
- **No tool call is involved.** This is a wrapper protocol: it adds no `allowed_tools` entry and no API
  route (spec 062 `FR-049`, `FR-040a(iv)`).

## Page References & Citations

Always use `{ticker} {citation_id} page<N>` (e.g., `LLY sec135 page12`) as the
citation label; bare `page_no` integers are forbidden in LLM-facing text. Every
citation MUST also carry the clickable `/v/` link — see
`contracts/citation-and-memory.md`.

## Fiscal Period Conventions

Periods are issuer-defined intervals, never a month grid. When a request names a
period, call `resolve_period(ticker, expression, as_of?)` first. It returns the
fiscal and calendar readings — dates, `period_id`, `record_status`, `ambiguous`
and the temporal frame. Use the fiscal `period_id` as the key on every later
call; never derive a quarter from `get_company_fiscal_calendar`'s month or from
`period_end`.

- **Wire labels:** fiscal `FY2026 Q3`; natural quarter `CY2025 Q3`. A bare
  `YYYYQn` is not a served period label. A bare quarter in a *request* is
  accepted; when its fiscal and calendar readings differ, choose one explicitly.
  When their intervals are identical the response collapses to one reading.
- **`as_of` is the knowledge cutoff** (`known_by`): a fact or document whose
  `knowable_at` is after it must not appear. Use the user's decision date or the
  report date, never the wall clock.
- **Typed absence, not widening:** if the period is absent or ambiguous, return
  the typed absence and the coverage gap. Do not widen the date range and retry
  a different quarter.
- **Facts use their own context:** `search_xbrl_facts(period_id=...)` selects the
  resolved interval. `search_cross_period` takes `period_ids` (an array).
- **Calendar questions:** use `calendar_quarter=YYYYQn` on `search_documents` or
  `search_xbrl_facts`. A calendar quarter is a natural quarter, not a fiscal
  one; annual reports are queried by `FY`/`period_id`, never through the calendar
  door.
- Skip the whole block for `structured_only` / `simple_lookup` scopes only when
  the request names no period.

**`event_label` is an event view, not a fiscal period** (spec 068 `T217`, spec 062 `FR-043(v)`). A record
may carry an additive `event_label` — `label_kind`, `display_label`, `role`, `target_period_id`,
`observation_id`. Its `role` is `discussed`; it carries **no** `fiscal_quarter`, **no** `period_id`
authority, and it never substitutes for the disclosure tag rule (an 8-K/6-K carries a fiscal label only
when `secondary_labels` name results or guidance). Read `display_label` as context even when it looks like
`2025Q2`: treating it as a period prices an event filing into a quarter it does not report.
