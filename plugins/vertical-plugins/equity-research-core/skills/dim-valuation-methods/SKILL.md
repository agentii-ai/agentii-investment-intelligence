---
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: 'Valuation methods: trailing 4 quarters for current multiples and DCF
    inputs'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
name: dim-valuation-methods
multi_ticker_semantics: single_target
essentials_modes:
- analyst-valuation-methods-comparison

---

<!-- analog: initiating-coverage -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

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

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies per spec 023 FR-056.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Valuation methods: trailing 4 quarters for current multiples and DCF inputs

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 3 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: analyst-valuation-methods-comparison

**Display name**: Analyst Valuation Methods Comparison

<!-- ported_from: references/prompts/8/8_1.yaml -->

### Objective

Extract and compare primary valuation methods used by Morgan Stanley and
Jefferies analysts to evaluate the target company, focusing on relative
valuation multiples and methodological approaches across forecast periods.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: structured_comparison_analysis
- **structure**:
  - comparative_analysis
  - executive_summary
  - jefferies_analysis
  - morgan_stanley_analysis

## Mode: comprehensive-valuation-summary-analysis

**Display name**: Comprehensive Valuation Summary Analysis

<!-- ported_from: references/prompts/8/8_1_1.yaml -->

### Objective

Extract and summarize comprehensive valuation methodologies from Morgan Stanley
and Jefferies analysts, covering both relative valuation multiples and absolute
valuation models (DCF) with detailed parameter extraction and analysis.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_valuation_analysis
- **structure**:
  - comparative_valuation_analysis
  - executive_summary
  - jefferies_valuation
  - morgan_stanley_valuation

## Mode: valuation-assumptions-extraction

**Display name**: Valuation Assumptions Extraction

<!-- ported_from: references/prompts/8/8_1_2.yaml -->

### Objective

Extract and analyze detailed valuation assumptions used in absolute valuation
models (DCF, intrinsic value models) by Morgan Stanley and Jefferies analysts,
focusing on key financial modeling parameters and methodology drivers.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: detailed_assumption_analysis
- **structure**:
  - comparative_assumption_analysis
  - executive_summary
  - jefferies_assumptions
  - morgan_stanley_assumptions

<!-- END port-dimension-prompts methodology + modes -->

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include per FR-020a: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
