---
name: secular-trends
description: Secular technology trends, technology adoption cycle, disruption risk, AI impact analysis, digital transformation, industry 4.0 trends, technology moat, innovation trajectory, R&D effectiveness, tech competitive positioning
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
  - search_unified
  - read_source_outline
  - list_xbrl_concepts
  - read_source_pages
  - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 10
---

<!-- analog: idea-generation -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution (FR-082)**: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check (FR-094)**: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing (FR-106)**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
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

**Layer 1 `secondary_label` allowlist (FR-078c)**: prefer `?secondary_label=other_events_8_01` to surface trend-related 8-Ks (technology disruption, regulatory shifts, demographic events) before Layer 2.

### Temporal Scope

Default: 12 fiscal quarters (max 20). Secular tech trends: 12 quarters (3 fiscal years) for long-range technology adoption cycles

### Tool Allowlist

See frontmatter `allowed_tools` — 11 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 8 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: evaluate-company-s-exposure-to-major-secular-technology-trends

**Display name**: Evaluate company's exposure to major secular technology trends

<!-- ported_from: references/prompts/4/4_1_optimized.yaml -->

**Focus**: Evaluate the company's exposure to and alignment with major secular technology trends.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

  - relevance_assessment
  - summary_findings
  - trend_exposure_matrix
- **validation_requirements**:
  - quantitative_support
  - source_diversity
  - temporal_coverage

### Mode: deep-dive-ai-trend-assessment-for-companies-with-identified-ai-exposure

**Display name**: Deep dive AI trend assessment for companies with identified AI exposure

<!-- ported_from: references/prompts/4/4_2_1_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-data-value-trend-assessment-for-companies-with-identified-data-exposure

**Display name**: Deep dive data value trend assessment for companies with identified data exposure

<!-- ported_from: references/prompts/4/4_2_2_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-ev-trend-assessment-for-companies-with-identified-ev-exposure

**Display name**: Deep dive EV trend assessment for companies with identified EV exposure

<!-- ported_from: references/prompts/4/4_2_3_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-analysis-for-quantum-computing-renewable-energy-and-other-emerging-tech-trends

**Display name**: Deep dive analysis for quantum computing, renewable energy, and other emerging tech trends

<!-- ported_from: references/prompts/4/4_2_4_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: evaluate-company-s-strategic-position-within-identified-technology-trends

**Display name**: Evaluate company's strategic position within identified technology trends

<!-- ported_from: references/prompts/4/4_2_optimized.yaml -->

**Focus**: Build on the Key Trend Exposure assessment to evaluate the company's strategic position.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

  - supporting_evidence
  - trend_header
- **validation_framework**:
  - competitive_benchmarking
  - consistency_check
  - financial_validation

### Mode: evaluate-company-s-capacity-and-readiness-to-invest-in-technology-transformation

**Display name**: Evaluate company's capacity and readiness to invest in technology transformation

<!-- ported_from: references/prompts/4/4_3_optimized.yaml -->

**Focus**: Evaluate the company's readiness and capacity to invest in technology as a strategic lever.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

  - citation_format
  - citation_requirements
- **tabular_assessment**:
  - dimension_specifications
  - required_fields

### Mode: assess-the-significance-of-technology-trends-in-current-investment-debate-and-market-perception

**Display name**: Assess the significance of technology trends in current investment debate and market perception

<!-- ported_from: references/prompts/4/4_4_optimized.yaml -->

**Focus**: Determine to what extent AI or any other major technology trend (data, automation, EV,.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`

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

## Output File

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_secular-trends_tech-trends.md` per FR-079.

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention (FR-079):

```
{ticker}/{YYYY-MM-DD_HHMM}_secular-trends_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `trend-impact`, `tailwind-headwind`, `theme-exposure`, `secular-positioning`). Examples:

- `LLY/2026-05-25_1430_secular-trends_trend-impact.md`
- `NVDA/2026-05-25_1545_secular-trends_theme-exposure.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format (FR-081)**: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.55](https://agentii.ai/v/LLY/sec175/55)`.

**agentii.md append (FR-087)**: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
