---
temporal_scope:
  default_quarters: 12
  max_quarters: 20
  description: 'Secular tech trends: 12 quarters (3 fiscal years) for long-range technology
    adoption cycles'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
- search_sec_filings
- get_entity_knowledge
- search_companies
name: dim-secular-tech-trends
multi_ticker_semantics: target_with_optional_peers
essentials_modes:
- evaluate-company-s-exposure-to-major-secular-technology-trends
- evaluate-company-s-strategic-position-within-identified-technology-trends
min_tool_diversity: 12
---

<!-- analog: idea-generation -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim secular tech trends
- run dim secular tech trends analysis
- produce dim secular tech trends report
- dim secular tech trends breakdown
- dim secular tech trends deep dive
- build a dim secular tech trends
- assess dim secular tech trends
- quantify dim secular tech trends
- compare dim secular tech trends across peers
- review dim secular tech trends for
- generate dim secular tech trends on
- dim secular tech trends for investment decision

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

Default: 12 fiscal quarters (max 20). Secular tech trends: 12 quarters (3 fiscal years) for long-range technology adoption cycles

### Tool Allowlist

See frontmatter `allowed_tools` — 11 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 8 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: evaluate-company-s-exposure-to-major-secular-technology-trends

**Display name**: Evaluate company's exposure to major secular technology trends

<!-- ported_from: references/prompts/4/4_1_optimized.yaml -->

### Objective

Evaluate the company's exposure to and alignment with major secular technology trends.
Focus on identifying how transformative technologies shape the business model and growth drivers.

### Key analytical questions

- Are the company's core earnings drivers materially shaped by transformative tech trends?
- Does the business model rely more on long-term tech adoption curves than traditional macro cycles?
- Is at least one major technology trend foundational to the company's strategic positioning and future growth?

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Output structure (per-mode)

- **structure**:
  - relevance_assessment
  - summary_findings
  - trend_exposure_matrix
- **validation_requirements**:
  - quantitative_support
  - source_diversity
  - temporal_coverage

## Mode: deep-dive-ai-trend-assessment-for-companies-with-identified-ai-exposure

**Display name**: Deep dive AI trend assessment for companies with identified AI exposure

<!-- ported_from: references/prompts/4/4_2_1_optimized.yaml -->

### Objective

_(no objective field in source YAML)_

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

## Mode: deep-dive-data-value-trend-assessment-for-companies-with-identified-data-exposure

**Display name**: Deep dive data value trend assessment for companies with identified data exposure

<!-- ported_from: references/prompts/4/4_2_2_optimized.yaml -->

### Objective

_(no objective field in source YAML)_

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

## Mode: deep-dive-ev-trend-assessment-for-companies-with-identified-ev-exposure

**Display name**: Deep dive EV trend assessment for companies with identified EV exposure

<!-- ported_from: references/prompts/4/4_2_3_optimized.yaml -->

### Objective

_(no objective field in source YAML)_

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

## Mode: deep-dive-analysis-for-quantum-computing-renewable-energy-and-other-emerging-tech-trends

**Display name**: Deep dive analysis for quantum computing, renewable energy, and other emerging tech trends

<!-- ported_from: references/prompts/4/4_2_4_optimized.yaml -->

### Objective

_(no objective field in source YAML)_

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

## Mode: evaluate-company-s-strategic-position-within-identified-technology-trends

**Display name**: Evaluate company's strategic position within identified technology trends

<!-- ported_from: references/prompts/4/4_2_optimized.yaml -->

### Objective

Build on the Key Trend Exposure assessment to evaluate the company's strategic position
within each identified trend. Determine whether the company is acting as an enabler,
adopter, laggard (at risk of disruption), or wildcard (uncertain role) in each case.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Output structure (per-mode)

- **trend_analysis_structure**:
  - supporting_evidence
  - trend_header
- **validation_framework**:
  - competitive_benchmarking
  - consistency_check
  - financial_validation

## Mode: evaluate-company-s-capacity-and-readiness-to-invest-in-technology-transformation

**Display name**: Evaluate company's capacity and readiness to invest in technology transformation

<!-- ported_from: references/prompts/4/4_3_optimized.yaml -->

### Objective

Evaluate the company's readiness and capacity to invest in technology as a strategic lever
by analyzing financial strength, organizational readiness, and investment commitment across
the most recent quarter and trailing periods.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Output structure (per-mode)

- **source_citation_standards**:
  - citation_format
  - citation_requirements
- **tabular_assessment**:
  - dimension_specifications
  - required_fields

## Mode: assess-the-significance-of-technology-trends-in-current-investment-debate-and-market-perception

**Display name**: Assess the significance of technology trends in current investment debate and market perception

<!-- ported_from: references/prompts/4/4_4_optimized.yaml -->

### Objective

Determine to what extent AI or any other major technology trend (data, automation, EV,
renewable energy, quantum computing) is significant, moderate, or insignificant in the
current investment debate and market perception of the stock.

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`

### Output structure (per-mode)

- **dimension_specifications**:
  - management_commentary
  - price_action_sentiment
  - sell_side_commentary
- **overall_summary_template**: [Technology Trend] is [Significant/Moderate/Insignificant] in the current investment
debate on [Company]. [2-3 sentences synthesizing evidence across sell-side commentary,
management emphasis, and market reaction. Explain why the technology trend matters or
doesn't matter to investors.]

- **structured_assessment**:
  - required_fields

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
