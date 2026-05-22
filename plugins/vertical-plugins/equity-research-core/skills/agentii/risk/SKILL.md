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
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: thesis-tracker -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

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

### Temporal Scope

Default: 4 fiscal quarters (max 8). Risk analysis: trailing 4 quarters for near-term risk exposure + forward indicators

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 4 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: general-risk-factors-identification-assessment

**Display name**: General Risk Factors Identification & Assessment

<!-- ported_from: references/prompts/6/6.yaml -->

### Objective

Conduct comprehensive risk factor identification and assessment using official issuer
disclosures to identify performance stagnation indicators and assess near-term and
long-term impact across standardized risk categories.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: comprehensive_risk_assessment
- **structure**:
  - executive_summary
  - long_term_risk_assessment
  - near_term_risk_assessment
  - novel_risk_factors
  - risk_identification
  - risk_trend_analysis

## Mode: technology-disruption-risk-analysis

**Display name**: Technology Disruption Risk Analysis

<!-- ported_from: references/prompts/6/6_1.yaml -->

### Objective

Assess technology disruption risk exposure by evaluating secular technology trend
impacts and emerging technology effects on the company's competitive positioning,
business model resilience, and long-term strategic viability.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: technology_risk_assessment
- **structure**:
  - emerging_technology_analysis
  - executive_summary
  - risk_factors
  - secular_trend_analysis
  - strategic_response_assessment

## Mode: regulatory-compliance-risk-assessment

**Display name**: Regulatory & Compliance Risk Assessment

<!-- ported_from: references/prompts/6/6_4.yaml -->

### Objective

Assess regulatory and compliance risk exposure by evaluating recent regulatory
developments and forward-looking policy risks that could materially impact
operations, earnings outlook, or strategic initiatives.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: regulatory_risk_assessment
- **structure**:
  - executive_summary
  - forward_policy_risk_analysis
  - recent_regulatory_developments
  - regulatory_preparedness
  - risk_mitigation

## Mode: external-shock-macro-risk-evaluation

**Display name**: External Shock & Macro Risk Evaluation

<!-- ported_from: references/prompts/6/6_5.yaml -->

### Objective

Assess external shock and macroeconomic risk exposure by evaluating recent
macro, geopolitical, and environmental events and analyzing financial
sensitivity to external volatility factors.

### Output structure (per-mode)

- **citation_required**: True
- **evidence_standard**: institutional_grade
- **format**: external_risk_assessment
- **structure**:
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
