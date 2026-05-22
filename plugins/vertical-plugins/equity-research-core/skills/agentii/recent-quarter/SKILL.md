---
name: recent-quarter
description: Recent quarter performance analysis, quarterly earnings review, last quarter results, quarterly financial performance, analyze recent quarter, Q4 earnings, quarterly revenue breakdown, EPS this quarter, margin analysis recent quarter, sequential growth, quarterly performance review
temporal_scope:
  default_quarters: 1
  max_quarters: 4
  description: "Typical lookback: 1 quarters, max: 4"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - search_documents
  - search_sec_filings
  - get_company_financials
  - get_company_profile
  - list_coverage
  - search_earnings_calendar
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: earnings-preview/morning-note -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim recent quarter performance
- run dim recent quarter performance analysis
- produce dim recent quarter performance report
- dim recent quarter performance breakdown
- dim recent quarter performance deep dive
- build a dim recent quarter performance
- assess dim recent quarter performance
- quantify dim recent quarter performance
- compare dim recent quarter performance across peers
- review dim recent quarter performance for
- generate dim recent quarter performance on
- dim recent quarter performance for investment decision

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

### Temporal Scope

Default: 4 fiscal quarters (max 8). Recent quarter performance: trailing 4 quarters for YoY comparison + sequential momentum

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 5 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: business-model-offerings-analysis

**Display name**: Business Model & Offerings Analysis

<!-- ported_from: references/prompts/1/1_1.yaml -->

### Objective

Conduct comprehensive business model analysis using the most recent quarter's official disclosures,
sell-side research, and market intelligence to determine the company's fundamental business structure,
core offerings, and strategic market positioning.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_xbrl_facts`

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: structured_analysis
- **structure**:
  - detailed_analysis
  - executive_summary
  - risk_factors

## Mode: distribution-channels-go-to-market-analysis

**Display name**: Distribution Channels & Go-to-Market Analysis

<!-- ported_from: references/prompts/1/1_2.yaml -->

### Objective

Analyze the company's distribution strategy and channel evolution using comprehensive
source analysis to assess go-to-market effectiveness, channel mix trends, and
strategic implications for customer relationships and profitability.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_strategic_analysis
- **structure**:
  - current_state_analysis
  - executive_summary
  - historical_trend_analysis
  - risk_assessment
  - strategic_implications

## Mode: revenue-composition-concentration-risk-analysis

**Display name**: Revenue Composition & Concentration Risk Analysis

<!-- ported_from: references/prompts/1/1_3.yaml -->

### Objective

Conduct comprehensive revenue analysis across multiple dimensions to identify
composition patterns, concentration risks, and temporal trends that impact
business sustainability and growth predictability.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `search_xbrl_facts`

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_risk_analysis
- **structure**:
  - concentration_risk_analysis
  - executive_summary
  - latest_quarter_breakdown
  - risk_matrix
  - temporal_analysis

## Mode: market-sizing-growth-analysis

**Display name**: Market Sizing & Growth Analysis

<!-- ported_from: references/prompts/1/1_4.yaml -->

### Objective

Conduct comprehensive market opportunity analysis by quantifying Total Addressable
Market (TAM), Serviceable Available Market (SAM), and Share of Market (SOM),
evaluating growth trajectories, and assessing the company's competitive position
relative to market growth rates.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `search_xbrl_facts`

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_market_analysis
- **structure**:
  - competitive_positioning
  - executive_summary
  - growth_trajectory_analysis
  - market_sizing_analysis
  - strategic_implications

## Mode: management-team-leadership-analysis

**Display name**: Management Team & Leadership Analysis

<!-- ported_from: references/prompts/1/1_5.yaml -->

### Objective

Assess key management team composition, leadership backgrounds, track records,
and recent changes to evaluate management quality, strategic capability,
and potential impact on execution and performance.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `search_keyword_in_source`

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_leadership_analysis
- **structure**:
  - analyst_perspectives
  - current_leadership_team
  - executive_summary
  - recent_leadership_changes
  - strategic_implications

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

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
