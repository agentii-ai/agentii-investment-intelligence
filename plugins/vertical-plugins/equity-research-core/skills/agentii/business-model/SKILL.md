---
name: business-model
description: Business model classification, business model analysis, structural analysis of how a company makes money, product offering decomposition, distribution channel analysis, customer segment analysis, revenue model identification, market sizing TAM SAM SOM, competitive positioning, business unit performance, management team & leadership analysis, what does the company sell, how does the company go to market, business model type platform service product, channel mix direct vs indirect, revenue concentration risk, CEO CFO executive backgrounds and changes
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Business-model analysis is a structural snapshot. Default lookback is 1 fiscal quarter (the most recent disclosure). Max 8 quarters when analyzing channel mix evolution or management changes over a 2-year window."
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - search_sec_filings
 - read_source_outline
 - read_source_pages
 - search_keyword_in_source
 - get_company_financials
 - get_company_profile
 - get_company_fiscal_calendar
 - get_ticker_coverage
 - list_xbrl_concepts
retrieval_scope: unstructured_document_search
min_tool_diversity: 7
---

<!-- analog: equity-research-core/business-model -->
<!-- methodology source: references/prompts/1/ (1_1 through 1_5) -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze the business model of {ticker}
- run business model analysis on {ticker}
- decompose the business model of {ticker}
- what does {ticker} sell and how does it make money
- classify the business model type of {ticker}
- analyze {ticker} product offerings and distribution channels
- assess {ticker} revenue composition and concentration risk
- evaluate {ticker} TAM SAM SOM and market positioning
- analyze {ticker} management team and leadership changes
- review {ticker} go-to-market strategy
- breakdown {ticker} customer segments and distribution model
- structural analysis of {ticker}
- business unit performance analysis for {ticker}
- competitive positioning of {ticker}

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_quarters | 1 | Single most-recent quarter snapshot for structural analysis |
| include_management_changes | true | Whether to surface leadership-change analysis (mode 1_5) |
| include_market_sizing | true | Whether to surface TAM/SAM/SOM (mode 1_4) |
| peer_set | none | Business-model analysis is single-issuer by default; peers are added by `/agentii:competitive` |

## Production Grounding

The Neon production database and `api.agentii.ai` REST/MCP surfaces are LIVE and AUTHORITATIVE as of 2026-05-25. All retrieval planning MUST treat these as ground truth. Production scale: 4.17M `gold.xbrl_facts` (with `is_primary` partial index), 11,575 `pipeline.src_documents` (100% non-null `description`, GIN-indexed `secondary_labels`), 243K `pipeline.src_silver_pages` (covering ALL 5 SEC form types — 8-K/10-K/10-Q/6-K/20-F; `labels` JSONB with `general.description` + `general.keywords`), 4,653 `pipeline.earnings_calendar` rows, 79 `gold.launch_ticker_registry` tickers at 100% processing. Always call `get_ticker_coverage/{ticker}` before retrieval planning.

## Methodology

### 1. Retrieval Scope

This skill performs **unstructured document search at scale** (10-K, 10-Q, 8-K filings). The three-layer agent-use-ready retrieval protocol applies (Layer 1 → Layer 2 → Layer 3). For foreign issuers, use 20-F (annual) and 6-K (material events) instead of 10-K and 8-K respectively.

### 2. Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`:

- **Branch (a)** — `search_xbrl_facts` for revenue concentration, gross margin profile, segment-level P&L (concepts `Revenues`, `GrossProfit`, `OperatingIncomeLoss`, `SegmentReportingInformation`).
- **Branch (b)** — `search_cross_period` when analyzing channel-mix evolution over 2+ years (mode 1_2) or management-change continuity (mode 1_5).
- **Branch (c)** — single-period three-layer for the most recent 10-K/10-Q business-overview pages (modes 1_1, 1_3, 1_4).

**Layer 1 narrowing — `secondary_labels` filter **: For 8-K-driven business-model-relevant disclosures, prefer `?secondary_label=other_events_8_01` (item 8.01 covers business-strategy events) AND `?secondary_label=financial_results_2_02` (item 2.02 surfaces segment-level revenue commentary). The GIN-indexed filter on `pipeline.src_documents.secondary_labels` is the preferred narrowing axis BEFORE Layer 2.

**Layer 2 page-relevance signal**: Score pages using `labels->>'general'->>'description'` (~100-char LLM-generated page summary) AND `labels->>'general'->>'keywords'` (extracted entity terms). Both fields are populated on 96%+ of `pipeline.src_silver_pages` rows. For business-model analysis, prefer pages whose `keywords` contain entity terms like product names, segment names, geographies, channel partners, executive names.

### 3. Temporal Scope

Default: 1 fiscal quarter (max 8). Business-model analysis is a structural snapshot — historical lookback only when explicitly tracking channel-mix evolution (mode 1_2 default 12 quarters) or management changes (mode 1_5 default 4 quarters).

### 4. Tool Allowlist

See frontmatter `allowed_tools` — 12 tools declared:

- `search_companies`, `get_company_profile` — issuer resolution and sector classification.
- `search_xbrl_facts`, `list_xbrl_concepts`, `get_company_financials` — segment-level P&L and revenue concentration metrics.
- `search_documents`, `search_sec_filings` — Layer 1 document discovery (with `secondary_labels` filter).
- `read_source_outline`, `read_source_pages`, `search_keyword_in_source` — Layer 2/3 deep read for business-overview pages.
- `get_company_fiscal_calendar`, `get_ticker_coverage` — pre-flight (mandatory first step).

### 5. Protocol

1. ** Pre-flight (mandatory)**: call `get_company_fiscal_calendar/{ticker}` for fiscal orientation, then `get_ticker_coverage/{ticker}` to discover which data sources are populated. Route based on coverage: `sec_filings` populated → standard three-layer protocol; `xbrl_facts`-only → structural inferences from segment data only, flag `data_availability: degraded`.

2. **Layer 1 Document Discovery**: `search_documents(ticker={T}, form_type=["10-K","20-F"], limit=3)` to find the most recent annual report (richest business-overview content). Add `?secondary_labels=financial_results_2_02,other_events_8_01` to also surface relevant 8-Ks. Document identifiers returned in `citation_id` form (e.g., `sec135`) — pass these directly to Layer 2.

3. **Layer 2 Page Map**: `read_source_outline/{ticker}/{citation_id}` — scan `description` + `keywords` for each page. Identify pages covering: Business overview / Item 1 (mode 1_1), Distribution & sales channels (mode 1_2), Revenue by segment & geography (mode 1_3), Industry / market context (mode 1_4), Directors & executive officers (mode 1_5). Bare `page_no` integers are forbidden in LLM-facing output — always use `{ticker} {citation_id} page<N>` format (e.g., "LLY sec135 page12").

4. **Layer 3 Deep Read**: `read_source_pages/{ticker}/{citation_id}?row_numbers=page<N1>,page<N2>` — load full `page_content` for ONLY the 3-5 pages identified in Layer 2.

5. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss"], fiscal_year=[<latest>])` — returns `is_primary: true` rows by default ( superseded; `?include_all_sources=true` only for audit). The `source_authority` field (3=10-K, 2=10-Q, 1=8-K) is returned for fact-provenance transparency.

6. **Evidence-pack handoff**: produce `evidence-pack.json` + `evidence-digest.md` . All citations use the v1.0 frozen format with `{ticker} {citation_id} page<N>` references.

## Modes (5 — structural equity analysis)

This skill delivers analyst-grade output via 5 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: business-model-classification (1_1 — anchor)

**Display name**: Business Model & Offerings Classification

<!-- ported_from: references/prompts/1/1_1.md -->

**Objective**: Determine business-model type (product / service / platform), core offering, and market positioning (low-end / mid-tier / high-end) using the most recent quarter's disclosures, sell-side research, and media sentiment.

**Output structure**:

- **Business Model**: [Product / Service / Platform]
- **Core Offering**: [e.g., Connected Wearable, Diagnostic Consumables, SaaS Subscription, Drug Pipeline, Cloud Platform]
- **Positioning**: [Low-end / Mid-tier / High-end] + brief rationale (e.g., "High-end based on >70% gross margin and premium ARPU vs. peers")
- **Citation density**: ≥1 citation per 200 words, format `{ticker} {citation_id} page<N>`.

### Mode: distribution-channel-analysis (1_2)

**Display name**: Distribution Channels & Go-to-Market Analysis

<!-- ported_from: references/prompts/1/1_2.md -->

**Objective**: Assess primary distribution model (direct sales / channel partners / hybrid), channel mix evolution (3-year trailing), and strategic implications for pricing power and customer intimacy.

**Output structure**:

- **Distribution Model**: [Direct Sales / Channel Partners / Hybrid]
- **Distribution Partners**: [list disclosed channel types and representative partners]
- **Current Channel Mix**: Direct : Indirect = 1 : XX (latest available data)
- **Historical Channel Mix Trend (Trailing 3 Years)**:
 - Year -2: [Direct : Indirect = 1 : XX]
 - Year -1: [Direct : Indirect = 1 : XX]
 - Current: [Direct : Indirect = 1 : XX]
- **Strategic Implication**: e.g., "Shift toward direct sales has enhanced pricing control and customer intimacy but increased SG&A".

### Mode: revenue-composition-and-concentration (1_3)

**Display name**: Revenue Composition & Concentration Risk Analysis

<!-- ported_from: references/prompts/1/1_3.md -->

**Objective**: Decompose revenue by product line / customer type / geography / end market, identify concentration risk (any single product or client >20% of total revenue), and trace temporal mix evolution.

**Output structure**:

- **Latest Quarter Revenue Breakdown**:
 - By Product Line: top 3 contributors with %
 - By User Type (B2B vs. B2C): mix with %
 - By Geography (NA / EMEA / APAC): top 3 regions with %
 - By End Market: top 3 markets with %
- **Concentration Risk Matrix**: any product/client >20% flagged.
- **Temporal Comparison**: vs. prior quarter and YoY same-period.

### Mode: market-sizing-and-relative-growth (1_4)

**Display name**: Market Sizing (TAM/SAM/SOM) & Relative Growth

<!-- ported_from: references/prompts/1/1_4.md -->

**Objective**: Quantify TAM, SAM, SOM for key verticals, project 3-5 year CAGR, assess relative growth (company vs. addressable market) and historical SOM evolution.

**Output structure**:

- **Market Sizing & Growth**:
 - TAM (Current Year): $XXXB
 - SAM (Current Year): $XXXB
 - SOM (Current Year): XX%
 - TAM CAGR (Past 3 Years): XX%
 - TAM CAGR (Forward 3-5 Years): XX%
- **Relative Growth Table**: Company Revenue Growth vs. TAM CAGR for past 3Y and next 3Y.
- **Historical SOM Trajectory**: 3-year evolution with execution-strength assessment.

### Mode: management-and-leadership (1_5)

**Display name**: Management Team & Leadership Analysis

<!-- ported_from: references/prompts/1/1_5.md -->

**Objective**: Assess executive team backgrounds, track records, and recent leadership changes (CEO/CFO/COO/CMO) for strategic-execution implications.

**Output structure**:

- **Key Executives & Track Record**: [Name, Role, Tenure, Notable Prior Experience, Industry Expertise, Capital Allocation Record]
- **Recent Management Changes (Trailing 1-2 Quarters)**: [Name, Role, Effective Date, Reason, Successor Background]
- **Strategic Implications of Changes**: e.g., "New CFO brings strong M&A background, suggesting a shift toward inorganic growth".

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_deep_outline` | PROXY_ERROR / 404 | Use lightweight `read_source_outline` and flag `deep_outline_degraded: true` | "deep outline unavailable; used lightweight page map instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, GrossProfit, OperatingIncomeLoss) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_xbrl_facts` | Empty (concept not populated) | Fall back to narrative analysis from 10-K Item 1 (Business Overview) | "segment-level P&L not in XBRL; structural inference only" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output File

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_business-model_product-line-decomp.md` .

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_business-model_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `product-line-decomp`, `channel-mix`, `market-sizing`, `management-changes`). Examples:

- `LLY/2026-05-25_1430_business-model_product-line-decomp.md`
- `NVDA/2026-05-25_1545_business-model_platform-classification.md`

The deliverable file MUST contain (in order):

1. **Executive Summary** (≤200 words) — business-model classification + headline structural insights.
2. **Business Model Type** (mode 1_1) — Product / Service / Platform classification with rationale.
3. **Product Line Decomposition** (mode 1_3) — revenue breakdown by product, top-3 contributors, concentration risk.
4. **Distribution Channel Analysis** (mode 1_2) — direct vs. indirect mix, partners, 3-year evolution.
5. **Customer Segment Analysis** (mode 1_3) — B2B vs. B2C, geography, end markets, concentration risk.
6. **Revenue Model** — recurring vs. one-time, pricing power, unit economics, gross-margin profile.
7. **Business Unit Performance** — segment-level P&L where available (XBRL or narrative).
8. **Market Sizing & Competitive Positioning** (mode 1_4) — TAM/SAM/SOM, relative growth vs. market.
9. **Management & Leadership** (mode 1_5) — executive team, recent changes, strategic implications.
10. **Coverage Gaps & Citations** — list of dimensions not retrievable + full citation index in `{ticker} {citation_id} page<N>` format.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec175/42)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Foreign issuer | `form_type=["10-K"]` empty | Retry with `form_type=["20-F"]` for annual + `form_type=["6-K"]` for material events | "Foreign issuer; using 20-F + 6-K instead of 10-K + 8-K." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile (skip channel-mix evolution) | "Limited historical data; mode 1_2 channel-mix trend skipped." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
