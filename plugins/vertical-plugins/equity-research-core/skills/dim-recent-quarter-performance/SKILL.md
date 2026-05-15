---
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: 'Recent quarter performance: trailing 4 quarters for YoY comparison
    + sequential momentum'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
name: dim-recent-quarter-performance
multi_ticker_semantics: single_target
essentials_modes:
- business-model-offerings-analysis
- distribution-channels-go-to-market-analysis

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
