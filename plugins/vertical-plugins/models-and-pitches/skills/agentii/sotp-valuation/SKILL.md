---
name: sotp-valuation
multi_ticker_semantics: target_with_optional_peers
description: Sum of the Parts valuation, segment-based valuation, conglomerate valuation, business segment analysis, breakup value, segment sum valuation, parts worth more than whole, hidden asset value
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Latest segment data with up to 12 quarters for segment trend"
allowed_tools:
 - search_xbrl_facts
 - search_companies
 - get_realtime_quote
 - search_documents
 - read_source_outline
 - read_source_deep_outline
 - read_source_pages
 - get_statement_structure
retrieval_scope: unstructured_document_search
min_tool_diversity: 7
---

# Sum of the Parts (SOTP) Valuation

Values each business segment independently and sums for total enterprise value. Essential for conglomerates (GE, MMM, HON), multi-segment tech (AMZN: AWS + Retail + Ads, GOOG: Search + Cloud + YouTube), and holding companies. SOTP often reveals "hidden value" when the market undervalues individual segments.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- sum of the parts valuation {ticker}
- SOTP analysis {ticker}
- segment-based valuation {ticker}
- breakup value {ticker}
- conglomerate valuation {ticker}
- parts worth more than whole {ticker}
- segment sum of parts {ticker}
- business segment valuation {ticker}
- hidden asset value {ticker}
- SOTP {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| segment_discovery | statement_tree | Use get_statement_structure for segment identification |
| peer_multiples | sector | Apply sector-appropriate multiples per segment |
| include_corporate | true | Subtract corporate overhead, net debt |

## Methodology

### Retrieval Scope

`unstructured_document_search` — SOTP requires segment financials from XBRL (structured) AND segment narrative/business description from MD&A (unstructured) for appropriate multiple selection.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 12. The default balances recency against the trend window this analysis requires.

### Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `search_companies` — ticker resolution + company context (entity-alias fuzzy match)
- `get_realtime_quote` — latest market price for valuation cross-checks
- `search_documents` — Layer 1 document discovery (page-level silver records)
- `read_source_outline` — Layer 2 lightweight page map (description + keywords)
- `read_source_deep_outline` — Layer 2.5a deep page map (table_titles/drivers/metrics)
- `read_source_pages` — Layer 3 deep read of selected pages with table markers
- `get_statement_structure` — XBRL presentation tree (concept hierarchy)

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

## Deliverable Chain

**Inputs** → **Build** → **Validate** → **Output** → **Next**

1. **Inputs**: resolved ticker + structured facts (`search_xbrl_facts`, `get_company_financials`) and any filing pages from the three-layer protocol.
2. **Build**: write the `.md` sum-of-the-parts valuation (segment multiples, conglomerate-discount analysis) per `## Output Structure`.
3. **Validate**: run the `## Validation Gates` below.
4. **Output**: write the artifact path per `## Output File`.
5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_sotp-valuation_{affix}.md`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Validation Gates

1. **Segment coverage**: segment revenues must sum to ≥80% of total reported revenue. *If failed*: flag segments representing <80% of revenue; note "significant unallocated revenue."
2. **Valuation consistency**: segment multiples justified by at least one comparable company or sector norm per segment. *If failed*: flag segments with unsubstantiated multiples.
3. **SOTP bridge integrity**: Segment Sum - Corporate + Adjustments = Total Equity within 1%. *If failed*: refuse delivery; check bridge arithmetic.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

## Error Handling

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| No segment data | Company reports as single segment | "{ticker} reports as a single operating segment — SOTP not applicable. Use DCF or comps." |
| Missing segment financials | Proceed with available data; flag gaps | "Segment financials incomplete for {segment_names}; SOTP based on partial data." |
