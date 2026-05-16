---
temporal_scope:
  default_quarters: 8
  max_quarters: 16
  description: 'Turnaround/stagnation: 8 quarters for operational trend detection
    and inflection-point analysis'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
name: dim-turnaround-stagnation
multi_ticker_semantics: target_with_required_peers
essentials_modes:
- performance-stagnation-detection-and-classification
- operational-execution-progress-and-effectiveness-assessment
min_tool_diversity: 10
---

<!-- analog: thesis-tracker -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim turnaround stagnation
- run dim turnaround stagnation analysis
- produce dim turnaround stagnation report
- dim turnaround stagnation breakdown
- dim turnaround stagnation deep dive
- build a dim turnaround stagnation
- assess dim turnaround stagnation
- quantify dim turnaround stagnation
- compare dim turnaround stagnation across peers
- review dim turnaround stagnation for
- generate dim turnaround stagnation on
- dim turnaround stagnation for investment decision

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

Default: 8 fiscal quarters (max 16). Turnaround/stagnation: 8 quarters for operational trend detection and inflection-point analysis

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 9 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: performance-stagnation-detection-and-classification

**Display name**: performance-stagnation-detection-and-classification

<!-- ported_from: references/prompts/5/5_1.yaml -->

### Objective

Identify and extract indicators of performance stagnation across four key dimensions using comprehensive financial and operational analysis. Classify company performance status based on stagnation pattern severity to guide turnaround investment decisions.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

## Mode: growth-catalyst-identification-and-assessment

**Display name**: growth-catalyst-identification-and-assessment

<!-- ported_from: references/prompts/5/5_2_1.yaml -->

### Objective

Identify and extract announcements related to new products, services, or business initiatives that could serve as major catalysts to reaccelerate growth trajectory or shift market sentiment for companies previously classified as [stagnant] or [potential turnaround candidate].

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: growth-catalyst-execution-monitoring-and-progress-assessment

**Display name**: growth-catalyst-execution-monitoring-and-progress-assessment

<!-- ported_from: references/prompts/5/5_2_1_1.yaml -->

### Objective

Monitor and assess the execution progress of identified growth catalyst initiatives through trackable metrics, market sentiment analysis, and milestone evaluation to determine ramp-up effectiveness and future monitoring priorities.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: leadership-change-impact-analysis

**Display name**: leadership-change-impact-analysis

<!-- ported_from: references/prompts/5/5_2_2.yaml -->

### Objective

Identify and analyze senior leadership or key personnel changes that could materially shift company strategy, investor sentiment, or growth trajectory for companies previously classified as [stagnant] or [potential turnaround candidate].

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: strategic-leadership-impact-assessment-and-financial-projection

**Display name**: strategic-leadership-impact-assessment-and-financial-projection

<!-- ported_from: references/prompts/5/5_2_3.yaml -->

### Objective

Analyze the speculated strategy or strategic shift tied to new executive appointments and assess the expected financial statement impacts based on the executive's track record and stated strategic focus areas.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: strategic-initiative-execution-status-and-effectiveness-assessment

**Display name**: strategic-initiative-execution-status-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_2_3_1.yaml -->

### Objective

Monitor and assess the execution status and effectiveness of strategic initiatives announced or underway, focusing on transformation levers that could drive company repositioning and growth reset. Evaluate progress against stated timelines and measure impact through operational KPIs and market feedback.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: operational-execution-progress-and-effectiveness-assessment

**Display name**: operational-execution-progress-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_3.yaml -->

### Objective

Identify and extract trackable metrics and qualitative signals that reflect the execution progress and early results of the company's turnaround strategies across five operational dimensions. Assess performance effectiveness and strategic momentum through comprehensive operational analysis.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: new-product-performance-evaluation-and-turnaround-contribution-assessment

**Display name**: new-product-performance-evaluation-and-turnaround-contribution-assessment

<!-- ported_from: references/prompts/5/5_4_1.yaml -->

### Objective

Identify and extract trackable metrics and indicators that evaluate the execution, market feedback, and impact of new products/services launched as growth catalysts. Determine whether performance aligns with analyst expectations or management's stated turnaround goals through comprehensive market reception analysis.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

## Mode: financial-turnaround-metrics-and-performance-validation

**Display name**: financial-turnaround-metrics-and-performance-validation

<!-- ported_from: references/prompts/5/5_4_2.yaml -->

### Objective

Identify and extract quantitative financial metrics and supporting commentary that assess the financial outcomes of strategic turnaround initiatives. Determine whether financial performance metrics align with or outperform expectations from analyst models, consensus estimates, and management's stated turnaround goals.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

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
