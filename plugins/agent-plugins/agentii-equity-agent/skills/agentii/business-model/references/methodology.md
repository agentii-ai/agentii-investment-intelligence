# business-model — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`:

- **Branch (a)** — `search_xbrl_facts` for revenue concentration, gross margin profile, segment-level P&L (concepts `Revenues`, `GrossProfit`, `OperatingIncomeLoss`, `SegmentReportingInformation`).
- **Branch (b)** — `search_cross_period` when analyzing channel-mix evolution over 2+ years (mode 1_2) or management-change continuity (mode 1_5).
- **Branch (c)** — single-period three-layer for the most recent 10-K/10-Q business-overview pages (modes 1_1, 1_3, 1_4).

**Layer 1 narrowing — `secondary_labels` filter **: For 8-K-driven business-model-relevant disclosures, prefer `?secondary_label=other_events_8_01` (item 8.01 covers business-strategy events) AND `?secondary_label=financial_results_2_02` (item 2.02 surfaces segment-level revenue commentary). The GIN-indexed filter on `pipeline.src_documents.secondary_labels` is the preferred narrowing axis BEFORE Layer 2.

**Layer 2 page-relevance signal**: Score pages using `labels->>'general'->>'description'` (~100-char LLM-generated page summary) AND `labels->>'general'->>'keywords'` (extracted entity terms). Both fields are populated on 96%+ of `pipeline.src_silver_pages` rows. For business-model analysis, prefer pages whose `keywords` contain entity terms like product names, segment names, geographies, channel partners, executive names.

## Protocol

1. ** Pre-flight (mandatory)**: call `get_company_fiscal_calendar/{ticker}` for fiscal orientation, then `get_ticker_coverage/{ticker}` to discover which data sources are populated. Route based on coverage: `sec_filings` populated → standard three-layer protocol; `xbrl_facts`-only → structural inferences from segment data only, flag `data_availability: degraded`.

2. **XBRL retrieval FIRST (grounding truth)**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","SegmentReportingInformation"], fiscal_year=[<latest>])` for segment/product/geography/channel revenue & margin breakdowns BEFORE any document discovery — returns `is_primary: true` rows by default (superseded rows hidden; `?include_all_sources=true` only for audit). The `source_authority` field (3=10-K, 2=10-Q, 1=8-K) is returned for fact-provenance transparency. This is the structural backbone of the analysis.

3. **Layer 1 Document Discovery**: `search_documents(ticker={T}, form_type=["10-K","10-Q","20-F"], limit=3)` to find the most recent annual report (richest business-overview content) plus trailing 10-Qs. For foreign issuers route to `form_type=["20-F","6-K"]`. Add `?secondary_labels=financial_results_2_02,other_events_8_01` to also surface relevant 8-Ks. Document identifiers returned in `citation_id` form (e.g., `sec135`) — pass these directly to Layer 2.

4. **Layer 2 Page Map**: `read_source_outline/{ticker}/{citation_id}` — scan `description` + `keywords` for each page. Identify pages covering: Business overview / Item 1 (mode 1_1), Distribution & sales channels (mode 1_2), Revenue by segment & geography (mode 1_3), Industry / market context (mode 1_4), Directors & executive officers (mode 1_5). Bare `page_no` integers are forbidden in LLM-facing output — always use `{ticker} {citation_id} page<N>` format (e.g., "LLY sec135 page12").

5. **Layer 3 Deep Read**: `read_source_pages/{ticker}/{citation_id}?row_numbers=page<N1>,page<N2>` — load full `page_content` for ONLY the 3-5 pages identified in Layer 2 to enrich the XBRL backbone with narrative.

6. **Cross-period (when applicable)**: use `search_cross_period` / `batch_search` for channel-mix evolution (mode 1_2) or management-change continuity (mode 1_5).

7. **Evidence-pack handoff**: produce `evidence-pack.json` + `evidence-digest.md` . All citations use the v1.0 frozen format with `{ticker} {citation_id} page<N>` references.

## Production Grounding

The Neon production database and `api.agentii.ai` REST/MCP surfaces are LIVE and AUTHORITATIVE as of 2026-05-25. All retrieval planning MUST treat these as ground truth. Production scale: 4.17M `gold.xbrl_facts` (with `is_primary` partial index), 11,575 `pipeline.src_documents` (100% non-null `description`, GIN-indexed `secondary_labels`), 243K `pipeline.src_silver_pages` (covering ALL 5 SEC form types — 8-K/10-K/10-Q/6-K/20-F; `labels` JSONB with `general.description` + `general.keywords`), 4,653 `pipeline.earnings_calendar` rows, 79 `gold.launch_ticker_registry` tickers at 100% processing. Always call `get_ticker_coverage/{ticker}` before retrieval planning.
