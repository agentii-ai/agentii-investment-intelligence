---
name: risk
description: Risk analysis, regulatory risk assessment, competitive risk, macro risk, technology risk, litigation risk, financial risk assessment, enterprise risk, operational risk, geopolitical risk exposure
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

- analyze dim risk analysis
- run dim risk analysis analysis
- produce dim risk analysis report
- dim risk analysis breakdown
- dim risk analysis deep dive
- build a dim risk analysis
- assess dim risk analysis
- quantify dim risk analysis
- compare dim risk analysis across peers
- review dim risk analysis for
- generate dim risk analysis on
- dim risk analysis for investment decision

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

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_labels=other_events_8_01` to surface risk-event 8-Ks (litigation, regulatory action, cyber incidents) before Layer 2. Also score Layer 2 pages whose `labels.general.keywords` contain "risk factors" entity terms.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Risk analysis: trailing 4 quarters for near-term risk exposure + forward indicators

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 4 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: general-risk-factors-identification-assessment

**Display name**: General Risk Factors Identification & Assessment

<!-- ported_from: references/prompts/6/6.yaml -->

### Objective

Conduct comprehensive risk factor identification and assessment using official issuer
disclosures to identify performance stagnation indicators and assess near-term and
long-term impact across standardized risk categories.

 - executive_summary
 - long_term_risk_assessment
 - near_term_risk_assessment
 - novel_risk_factors
 - risk_identification
 - risk_trend_analysis

### Mode: technology-disruption-risk-analysis

**Display name**: Technology Disruption Risk Analysis

<!-- ported_from: references/prompts/6/6_1.yaml -->

### Objective

Assess technology disruption risk exposure by evaluating secular technology trend
impacts and emerging technology effects on the company's competitive positioning,
business model resilience, and long-term strategic viability.

 - emerging_technology_analysis
 - executive_summary
 - risk_factors
 - secular_trend_analysis
 - strategic_response_assessment

### Mode: regulatory-compliance-risk-assessment

**Display name**: Regulatory & Compliance Risk Assessment

<!-- ported_from: references/prompts/6/6_4.yaml -->

### Objective

Assess regulatory and compliance risk exposure by evaluating recent regulatory
developments and forward-looking policy risks that could materially impact
operations, earnings outlook, or strategic initiatives.

 - executive_summary
 - forward_policy_risk_analysis
 - recent_regulatory_developments
 - regulatory_preparedness
 - risk_mitigation

### Mode: external-shock-macro-risk-evaluation

**Display name**: External Shock & Macro Risk Evaluation

<!-- ported_from: references/prompts/6/6_5.yaml -->

### Objective

Assess external shock and macroeconomic risk exposure by evaluating recent
macro, geopolitical, and environmental events and analyzing financial
sensitivity to external volatility factors.

 - executive_summary
 - external_shock_analysis
 - financial_sensitivity_analysis
 - risk_management_assessment
 - vulnerability_analysis

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

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_risk_risk-assessment.md` .

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_risk_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `risk-matrix`, `regulatory-exposure`, `tech-disruption`, `macro-sensitivity`). Examples:

- `LLY/2026-05-25_1430_risk_risk-matrix.md`
- `NVDA/2026-05-25_1545_risk_tech-disruption.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.30](https://agentii.ai/v/LLY/sec175/30)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
