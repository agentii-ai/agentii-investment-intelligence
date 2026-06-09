---
name: valuation-methods
description: Valuation methods analysis, DCF inputs, comparable multiples, P/E ratio, EV/EBITDA, price to book, valuation assumptions, relative valuation, intrinsic value, fair value estimate
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - search_documents
  - read_source_outline
  - read_source_pages
  - get_company_financials
  - search_earnings_calendar
  - get_company_profile
  - list_xbrl_concepts
  - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: initiating-coverage -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution (FR-082)**: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check (FR-094)**: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing (FR-106)**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze dim valuation methods
- run dim valuation methods analysis
- produce dim valuation methods report
- dim valuation methods breakdown
- dim valuation methods deep dive
- build a dim valuation methods
- assess dim valuation methods
- quantify dim valuation methods
- compare dim valuation methods across peers
- review dim valuation methods for
- generate dim valuation methods on
- dim valuation methods for investment decision

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

Follow the retrieval strategy decision tree in `retrieval.md`. This skill was upgraded from `structured_only` to `unstructured_document_search` scope per FR-084 (2026-06-03) to pull MD&A and risk-factor narrative context alongside XBRL multiples. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries spanning 10-K Item 1A risk factors (discount rate justification, beta/delta assumptions), MD&A forward-looking statements (growth rate validation, margin trajectory), and 8-K earnings press releases (valuation catalysts, guidance revisions).
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist (FR-078c)**: prefer `?secondary_label=financial_results_2_02` to anchor valuation against the most recent reported financials before Layer 2. For risk-factor analysis, also query `?secondary_label=other_events_8_01` to surface going-concern and impairment 8-Ks that may affect valuation assumptions.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Valuation methods: trailing 4 quarters for current multiples and DCF inputs

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 3 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter. **Sub-skill integrations**: for growth-adjusted valuation, invoke `peg-valuation` as sub-skill (FR-099). For probability-weighted analysis, use `--mode=scenario` which constructs Bear/Base/Bull cases across all modes (FR-104).

### Mode: analyst-valuation-methods-comparison

**Display name**: Analyst Valuation Methods Comparison

<!-- ported_from: references/prompts/8/8_1.yaml -->

### Objective

Extract and compare primary valuation methods used by Morgan Stanley and
Jefferies analysts to evaluate the target company, focusing on relative
valuation multiples and methodological approaches across forecast periods.

  - comparative_analysis
  - executive_summary
  - jefferies_analysis
  - morgan_stanley_analysis

### Mode: comprehensive-valuation-summary-analysis

**Display name**: Comprehensive Valuation Summary Analysis

<!-- ported_from: references/prompts/8/8_1_1.yaml -->

### Objective

Extract and summarize comprehensive valuation methodologies from Morgan Stanley
and Jefferies analysts, covering both relative valuation multiples and absolute
valuation models (DCF) with detailed parameter extraction and analysis.

  - comparative_valuation_analysis
  - executive_summary
  - jefferies_valuation
  - morgan_stanley_valuation

### Mode: valuation-assumptions-extraction

**Display name**: Valuation Assumptions Extraction

<!-- ported_from: references/prompts/8/8_1_2.yaml -->

### Objective

Extract and analyze detailed valuation assumptions used in absolute valuation
models (DCF, intrinsic value models) by Morgan Stanley and Jefferies analysts,
focusing on key financial modeling parameters and methodology drivers.

  - comparative_assumption_analysis
  - executive_summary
  - jefferies_assumptions
  - morgan_stanley_assumptions

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

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_valuation-methods_valuation-comparison.md` per FR-079.

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention (FR-079):

```
{ticker}/{YYYY-MM-DD_HHMM}_valuation-methods_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `multiples-and-models`, `dcf-walk`, `comps-table`, `sotp-summary`). Examples:

- `LLY/2026-05-25_1430_valuation-methods_multiples-and-models.md`
- `NVDA/2026-05-25_1545_valuation-methods_dcf-walk.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format (FR-081)**: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec175/42)`.

**agentii.md append (FR-087)**: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
