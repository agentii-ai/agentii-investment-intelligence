---
name: turnaround
description: Turnaround analysis, stagnation detection, performance inflection, operational improvement, restructuring analysis, management change impact, cost cutting effectiveness, business transformation, recovery trajectory, operational metrics improvement
temporal_scope:
 default_quarters: 4
 max_quarters: 10
 description: "Typical lookback: 4 quarters, max: 10"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - search_sec_filings
 - get_company_financials
 - get_company_profile
 - list_coverage
 - read_source_outline
 - list_xbrl_concepts
 - read_source_pages
 - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: thesis-tracker -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
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

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_labels=results_of_operations_8_01,other_events_8_01` to surface restructuring, cost-action, and operational-inflection 8-Ks before Layer 2.

### Temporal Scope

Default: 8 fiscal quarters (max 16). Turnaround/stagnation: 8 quarters for operational trend detection and inflection-point analysis

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 9 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: performance-stagnation-detection-and-classification

**Display name**: performance-stagnation-detection-and-classification

<!-- ported_from: references/prompts/5/5_1.yaml -->

**Focus**: Identify and extract indicators of performance stagnation across four key dimensions using comprehensive financial and operational analysis.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: growth-catalyst-identification-and-assessment

**Display name**: growth-catalyst-identification-and-assessment

<!-- ported_from: references/prompts/5/5_2_1.yaml -->

**Focus**: Identify and extract announcements related to new products, services, or business initiatives that could serve as major catalysts to reaccelerate grow.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: growth-catalyst-execution-monitoring-and-progress-assessment

**Display name**: growth-catalyst-execution-monitoring-and-progress-assessment

<!-- ported_from: references/prompts/5/5_2_1_1.yaml -->

**Focus**: Monitor and assess the execution progress of identified growth catalyst initiatives through trackable metrics, market sentiment analysis, and mileston.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: leadership-change-impact-analysis

**Display name**: leadership-change-impact-analysis

<!-- ported_from: references/prompts/5/5_2_2.yaml -->

**Focus**: Identify and analyze senior leadership or key personnel changes that could materially shift company strategy, investor sentiment, or growth trajectory.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: strategic-leadership-impact-assessment-and-financial-projection

**Display name**: strategic-leadership-impact-assessment-and-financial-projection

<!-- ported_from: references/prompts/5/5_2_3.yaml -->

**Focus**: Analyze the speculated strategy or strategic shift tied to new executive appointments and assess the expected financial statement impacts based on the.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: strategic-initiative-execution-status-and-effectiveness-assessment

**Display name**: strategic-initiative-execution-status-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_2_3_1.yaml -->

**Focus**: Monitor and assess the execution status and effectiveness of strategic initiatives announced or underway, focusing on transformation levers that could.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: operational-execution-progress-and-effectiveness-assessment

**Display name**: operational-execution-progress-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_3.yaml -->

**Focus**: Identify and extract trackable metrics and qualitative signals that reflect the execution progress and early results of the company's turnaround strat.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: new-product-performance-evaluation-and-turnaround-contribution-assessment

**Display name**: new-product-performance-evaluation-and-turnaround-contribution-assessment

<!-- ported_from: references/prompts/5/5_4_1.yaml -->

**Focus**: Identify and extract trackable metrics and indicators that evaluate the execution, market feedback, and impact of new products/services launched as gr.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: financial-turnaround-metrics-and-performance-validation

**Display name**: financial-turnaround-metrics-and-performance-validation

<!-- ported_from: references/prompts/5/5_4_2.yaml -->

**Focus**: Identify and extract quantitative financial metrics and supporting commentary that assess the financial outcomes of strategic turnaround initiatives.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

<!-- END port-dimension-prompts methodology + modes -->

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_deep_outline` | PROXY_ERROR / 404 | Use lightweight `read_source_outline` and flag `deep_outline_degraded: true` | "deep outline unavailable; used lightweight page map instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output File

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_turnaround_turnaround-assessment.md` .

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_turnaround_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `turnaround-thesis`, `restructuring-progress`, `cost-action`, `inflection-signals`). Examples:

- `LLY/2026-05-25_1430_turnaround_turnaround-thesis.md`
- `NVDA/2026-05-25_1545_turnaround_restructuring-progress.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 8-K p.19](https://agentii.ai/v/LLY/sec129/19)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
