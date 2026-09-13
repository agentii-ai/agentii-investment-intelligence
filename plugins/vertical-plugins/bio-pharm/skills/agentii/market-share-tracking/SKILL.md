---
name: market-share-tracking
description: Weekly product-level commercial tracking — TRx/NRx with current/4-wk/12-wk share and YoY, launch curves overlaid with same-class analogs plus a consensus-implied trajectory, LOE/biosimilar erosion series, GTN/net-price stress brackets, and per-row data-caveat discipline. Use to track any launched drug, biologic, device, or vaccine against its class and consensus.
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - commercial-tracking
  - launch-curves
  - loe-erosion
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Weekly rolling-window tracking default 4 quarters; up to 8 for launch-curve overlays."
allowed_tools:
  - search_commercial_track
  - search_companies
  - get_company_profile
  - get_statement
  - search_documents
  - search_sec_filings
  - list_sources
  - read_source_outline
  - read_source_pages
  - search_earnings_calendar
  - list_upcoming_earnings
  - search_investment_cases
  - search_by_analogue
  - search_knowledge_entries
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught commercial-tracking approaches; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| windows | current / 4-wk / 12-wk | Three-window share + growth lattice |
| growth_metric | TRx YoY | Weekly, 4-wk, and 12-wk YoY alongside share |
| analog_count | 2 | ≥2 named same-class analogs on the launch board |
| consensus_source | company-level | Product consensus via segment-share math [DEDUCTED] |
| caveats | per-row | A number without a caveat annotation is a defect |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before commercial-track queries.

## Triggers

- "Is [product] tracking above or below consensus?"
- "How is the [product] launch trending?"
- "Build the launch board for [product] with class analogs."
- "What is the consensus-implied trajectory for [product]?"
- "Show [product]'s TRx share and YoY for the last 12 weeks."
- "How fast is [biosimilar] eroding [branded product]?"
- "Stress-test [product]'s net price and GTN."
- "What are the caveats on [product]'s scripts?"
- "Track installed base and utilization for [device]."
- "How is ACIP-cohort uptake tracking for [vaccine]?"

## Production Grounding

- Three-window lattice: current / 4-wk / 12-wk share and YoY; previous values shown next to new values.
- Launch boards: actuals vs ≥2 named same-class analogs + consensus-implied trajectory (consensus sales ÷ net price ÷ script duration → required TRx → linear path); assumptions stated.
- LOE erosion: entrant share vs branded YoY decay with approval/launch dates.
- GTN/net-price stress: GTN brackets (50→80% flex), $/Rx = quarterly sales ÷ scripts, channel mix; half-of-sales-minus-volume net price is a stated judgment [VIEW].
- Modality vocabularies: scripts/share/erosion (drugs & biologics); installed base, placements/procedures, utilization, ASP (devices); doses/serials, procurement, ACIP-cohort uptake (vaccines); never a script number for a device or vaccine.
- Per-row caveats: restricted scripts, rounding, indication-mixed, IV invisibility, holiday weeks — every row carries its caveat or `coverage_gap`.
- Badges: `[FACT]`/`[DEDUCTED]`/`[VIEW]` with the summary table.

## Data Source Priority

1. `search_commercial_track` — weekly track rows with stored previous values.
2. Company-reported product sales: 10-K/Q XBRL (`get_statement`) and MD&A (`search_documents`).
3. Transcript commentary on scripts/share/persistence via `search_documents`.
4. Payer coverage/PA announcements and openFDA label events via `search_documents` + `list_sources`.
5. Consensus: `search_earnings_calendar` company-level only; licensed Rx panels never assumed.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve basket tickers via `search_companies`; map products to companies.
2. Pull weekly rows via `search_commercial_track` (previous values stored alongside).
3. Compute the three-window lattice from stored history; attach per-row caveats.
4. Build the launch board: ≥2 named analog curves + consensus-implied trajectory arithmetic.
5. LOE events: pair entrant share with branded YoY decay; date approval/launch.
6. Stress net price (GTN brackets, $/Rx, channel mix); label derived values `[DEDUCTED]`.
7. Ground in knowledge (sectors=med); cite /v/ records.

### Temporal Scope
See frontmatter temporal_scope block. Rolling windows recompute from stored history; holiday weeks are labeled.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Ticker + product resolution
2. Commercial-track pull (stored history)
3. Three-window lattice computation
4. Launch-board overlay + implied trajectory
5. LOE erosion series (when applicable)
6. GTN/net-price stress + caveat audit

## Modes

- **Drug / biologic** (default): scripts/share/erosion; LOE/biosimilar series.
- **Device**: installed base, placements/procedures, utilization, ASP; no script numbers.
- **Vaccine**: doses/serials, procurement, ACIP-cohort uptake; approval ≠ commercial availability.
- **Basket**: multi-ticker watchlist with per-name sections.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| search_commercial_track empty | Company-reported sales (`get_statement`/`search_documents`); annotate coverage_gap |
| Scripts restricted (IQVIA) | State the restriction verbatim; refuse a share number; use company-reported metrics |
| No product consensus | Segment share × company consensus [DEDUCTED]; else coverage_gap with required inputs |
| No analog series | Named-analog list with disclosed sales/scripts; flag degraded |
| One-quarter issuer / pre-revenue | Pipeline/cash-runway logic; no share arithmetic |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_market-share-tracking_{affix}.md` (basket: `watchlist/{YYYY-MM-DD_HHMM}_market-share-tracker_{affix}.md`)

## Output Structure

1. **Executive Summary** — actuals vs consensus-implied trajectory, 2-3 sentences
2. **Launch Board** — actuals vs ≥2 named analogs + consensus-implied path with stated arithmetic
3. **Share & YoY Lattice** — current/4-wk/12-wk share and YoY with previous values
4. **LOE / Erosion Series** — entrant share vs branded YoY decay with approval/launch dates
5. **Net-Price & GTN Stress** — $/Rx, GTN brackets, channel mix, [DEDUCTED] labels
6. **Caveat Register** — per-row annotations + coverage_gap list
7. **Coverage Gaps** — missing sources and degraded modes

## Error Handling

| Error | Fallback |
|-------|----------|
| No commercial-track rows | Company-reported sales only; annotate coverage_gap — never fabricate scripts |
| Product not in med universe | Resolve via product/company match; surface the classification gap |
| Consensus absent | coverage_gap with required inputs (sales, net price, script duration) |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `references/knowledge-frameworks.md`
