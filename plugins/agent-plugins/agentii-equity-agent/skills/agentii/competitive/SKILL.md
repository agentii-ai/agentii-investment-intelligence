---
name: competitive
description: Competitive landscape analysis, competitor comparison, peer positioning, market share dynamics, competitive moat assessment, Porter five forces, industry competition, competitive advantage analysis, market positioning, strategic group mapping, compare competitors
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Typical lookback: 4 quarters, max: 12"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - search_documents
  - search_sec_filings
  - get_company_financials
  - list_coverage
  - search_earnings_calendar
  - get_company_profile
  - batch_search
retrieval_scope: unstructured_document_search
min_tool_diversity: 10
---

<!-- analog: sector-overview -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution (FR-082)**: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

## Triggers

- analyze dim competitive landscape
- run dim competitive landscape analysis
- produce dim competitive landscape report
- dim competitive landscape breakdown
- dim competitive landscape deep dive
- build a dim competitive landscape
- assess dim competitive landscape
- quantify dim competitive landscape
- compare dim competitive landscape across peers
- review dim competitive landscape for
- generate dim competitive landscape on
- dim competitive landscape for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

<!-- BEGIN port-dimension-prompts methodology + modes -->

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist (FR-078c)**: prefer `?secondary_labels=material_definitive_agreement_1_01,other_events_8_01` to surface M&A / partnership / strategic-action 8-Ks before Layer 2.

### Temporal Scope

Default: 8 fiscal quarters (max 16). Competitive landscape: 8 quarters for market-share trajectories and positioning shifts

### Tool Allowlist

See frontmatter `allowed_tools` — 11 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 8 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: direct-competitor-identification-and-analysis

**Display name**: direct-competitor-identification-and-analysis

<!-- ported_from: references/prompts/2/2_1_1.yaml -->

**Focus**: Leverage multiple sources to identify and evaluate the company's major competitors across products, geographies, and development stages, providing a c.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `search_keyword_in_source`

### Mode: market-share-dynamics-analysis

**Display name**: market-share-dynamics-analysis

<!-- ported_from: references/prompts/2/2_1_2.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share dynamics over the past 2 years, using trackable operating metrics d.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `read_source_outline`
- `search_xbrl_facts`

### Mode: market-share-evolution-and-competitive-benchmarking

**Display name**: market-share-evolution-and-competitive-benchmarking

<!-- ported_from: references/prompts/2/2_1_3.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share trends over the past 12 quarters, using trackable operating metrics.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: forward-looking-market-share-outlook-and-strategic-assessment

**Display name**: forward-looking-market-share-outlook-and-strategic-assessment

<!-- ported_from: references/prompts/2/2_1_4.yaml -->

**Focus**: Leverage multiple data sources to evaluate the company's forward-looking market share outlook over the next 1-2 years, using operating metrics and qua.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `search_keyword_in_source`

### Mode: market-concentration-and-competitive-positioning-analysis

**Display name**: market-concentration-and-competitive-positioning-analysis

<!-- ported_from: references/prompts/2/2_1_5.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share dynamics and competitive positioning over the past 12 quarters, usi.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: market-share-growth-drivers-and-retention-risk-analysis

**Display name**: market-share-growth-drivers-and-retention-risk-analysis

<!-- ported_from: references/prompts/2/2_1_6.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share growth drivers and retention risks over the most recent 12 quarters.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: market-share-capture-efficiency-and-execution-analysis

**Display name**: market-share-capture-efficiency-and-execution-analysis

<!-- ported_from: references/prompts/2/2_1_7.yaml -->

**Focus**: Leverage multiple data sources to evaluate the company's capability to capture market share and execute against market opportunities, using operating .
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: indirect-competition-and-substitution-threat-analysis

**Display name**: indirect-competition-and-substitution-threat-analysis

<!-- ported_from: references/prompts/2/2_2.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the indirect competitive landscape facing the company, including substitutes, adjacent market .
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `read_source_outline`
- `search_keyword_in_source`

<!-- END port-dimension-prompts methodology + modes -->

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output File

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_competitive_peer-positioning.md` per FR-079.

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention (FR-079):

```
{ticker}/{YYYY-MM-DD_HHMM}_competitive_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `peer-positioning`, `moat-analysis`, `share-shift`, `competitive-dynamics`). Examples:

- `LLY/2026-05-25_1430_competitive_peer-positioning.md`
- `NVDA/2026-05-25_1545_competitive_moat-analysis.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format (FR-081)**: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://www.agentii.ai/view?ticker={ticker}&citation_id={citation_id}&page_no={page<N>})`. Example: `[📄 LLY 10-K p.42](https://www.agentii.ai/view?ticker=LLY&citation_id=sec175&page_no=page42)`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
