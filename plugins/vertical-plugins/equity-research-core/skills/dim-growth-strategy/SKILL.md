---
temporal_scope:
  default_quarters: 8
  max_quarters: 16
  description: 'Growth strategy: 8 quarters for organic/inorganic growth trend decomposition'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
name: dim-growth-strategy
multi_ticker_semantics: single_target
essentials_modes:
- growth-strategy-assessment
- organic-growth-drivers-analysis

---

<!-- analog: initiating-coverage -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim growth strategy
- run dim growth strategy analysis
- produce dim growth strategy report
- dim growth strategy breakdown
- dim growth strategy deep dive
- build a dim growth strategy
- assess dim growth strategy
- quantify dim growth strategy
- compare dim growth strategy across peers
- review dim growth strategy for
- generate dim growth strategy on
- dim growth strategy for investment decision

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

Default: 8 fiscal quarters (max 16). Growth strategy: 8 quarters for organic/inorganic growth trend decomposition

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 5 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

## Mode: growth-strategy-assessment

**Display name**: growth-strategy-assessment

<!-- ported_from: references/prompts/3/3_1.yaml -->

### Objective

Systematically analyze company's growth strategy by evaluating multiple data sources
to determine if growth is driven by:
- Organic initiatives (internal: product development, pricing, expansion)
- Inorganic initiatives (external: M&A, JVs, strategic investments)
- Mix (balanced combination of both approaches)

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

### Output structure (per-mode)

- **quality_standards**:
  - citations
  - clarity
  - conciseness
  - evidence_based
  - recency
- **structure**: ## Growth Strategy Assessment

**Growth Strategy Classification**: [Organic / Inorganic / Mix]

**Strategy Summary**:
{Concise explanation of the company's growth approach, 3-5 sentences}

**Supporting Evidence**:

### Organic Growth Indicators
- {List identified organic initiatives with citations}
- {Example: Product development programs mentioned in Q2 earnings call _(cite source filing in FR-050 format at runtime)_}

### Inorganic Growth Indicators
- {List identified inorganic initiatives with citations}
- {Example: M&A transaction announced in 8-K filing _(cite source filing in FR-050 format at runtime)_}

**Data Sources Analyzed**:
- {List key documents reviewed: 10-K, earnings calls, analyst reports}

**Temporal Scope**: {Specify analysis period, e.g., "FY23 10-K plus Q1-Q2 2024 earnings materials"}


## Mode: organic-growth-drivers-analysis

**Display name**: organic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_2_1.yaml -->

### Objective

Systematically identify and extract organic growth drivers across 6 dimensions
by analyzing issuer disclosures and sell-side research from the past two quarters.

For each dimension, determine:
- Presence: [Yes / No / Nil]
- Supporting Evidence: Specific initiatives and details
- Source Citations: Document references with proper format

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`

### Output structure (per-mode)

- **quality_standards**:
  - citation_discipline
  - evidence_requirements
  - presence_determination
  - temporal_accuracy
- **structure**: ## Organic Growth Drivers Analysis

**Analysis Period**: {Specify fiscal quarters analyzed, e.g., "2024 Q1-Q2"}

**Data Sources**:
- Most Recent 10-K: {Filing date}
- Quarterly Materials: {List earnings calls, 10-Qs analyzed}
- Sell-Side Research: {List analyst reports reviewed}

**Growth Driver Assessment**:

| Dimension | Presence | Summary of Evidence | Source(s) |
|:----------|:---------|:-------------------|:----------|
| Product | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Market | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Customer Retention | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Pricing | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Sales & Channel | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Marketing | Yes/No/Nil | {Brief description of initiatives} | {Citations} |

**Detailed Evidence**:

### Product
{If Presence=Yes, provide detailed description}
- Initiative 1: {Description} _(cite source filing in FR-050 format at runtime)_
- Initiative 2: {Description} _(cite source filing in FR-050 format at runtime)_

{Repeat for each dimension with Presence=Yes}

**Key Observations**:
- {Synthesize overall organic growth approach}
- {Note any patterns or emphasis across dimensions}


## Mode: organic-growth-driver-execution-assessment

**Display name**: organic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_2_2.yaml -->

### Objective

Assess the execution progress of previously identified organic growth drivers
by analyzing most recent issuer disclosures, sell-side research, and management commentary.

For each growth driver dimension with Presence=Yes from task 3_2_1, determine:
- Execution Status: [On Track / Behind Schedule / Ahead of Plan]
- Supporting Evidence: KPIs, milestones achieved, management commentary
- Source Citations: Document references with proper format

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

### Output structure (per-mode)

- **quality_standards**:
  - citation_discipline
  - evidence_requirements
  - status_determination
  - temporal_accuracy
- **structure**: ## Organic Growth Driver Execution Progress Assessment

**Assessment Period**: {Most recent fiscal quarter, e.g., "2024 Q2"}
**Assessment Date**: {Latest earnings date used for analysis}

**Data Sources**:
- Latest Earnings Call: {Date and quarter}
- Most Recent 10-Q: {Filing date}
- Sell-Side Research: {List recent analyst reports reviewed}

**Execution Status Summary**:

| Growth Driver | Execution Status | Summary of Progress / Commentary | Source(s) |
|:--------------|:-----------------|:--------------------------------|:----------|
| Product | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Market | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Customer Retention | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Pricing | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Sales & Channel | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Marketing | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |

**Detailed Execution Evidence**:

### {Dimension Name}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Initiative** (from task 3_2_1):
{Brief recap of initiative identified previously}

**Current Progress**:
- Evidence Point 1: {Description with metrics} _(cite source filing in FR-050 format at runtime)_
- Evidence Point 2: {Description with metrics} _(cite source filing in FR-050 format at runtime)_
- Management Commentary: {Relevant quote or summary} _(cite source filing in FR-050 format at runtime)_

**Status Rationale**:
{Explanation of why this status was assigned based on evidence}

{Repeat for each dimension with Presence=Yes}

**Overall Execution Assessment**:
- {Synthesize execution progress across all organic growth drivers}
- {Note any patterns: most initiatives on track, specific areas of concern, etc.}
- {Highlight any dimension showing particularly strong or weak execution}


## Mode: inorganic-growth-drivers-analysis

**Display name**: inorganic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_3_1.yaml -->

### Objective

Systematically identify and extract inorganic growth drivers over the past 5 years
by analyzing issuer disclosures and sell-side research.

For each inorganic activity category, determine:
- Presence: [Yes / No / Nil]
- Detailed Transaction/Activity Information: chronological listing with strategic rationale
- Impact Assessment: [Factor-in / On-going / Unclear]
- Source Citations: Document references with proper format

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

### Output structure (per-mode)

- **quality_standards**:
  - chronological_accuracy
  - citation_discipline
  - impact_assessment_rigor
  - presence_determination
  - transaction_completeness
- **structure**: ## Inorganic Growth Drivers Analysis

**Analysis Period**: {Specify 5-year period, e.g., "FY19-FY23 plus 2024 YTD"}

**Data Sources**:
- Annual Filings: {List 10-K years reviewed}
- Material Announcements: {Number of 8-Ks reviewed}
- Earnings Materials: {Recent earnings calls reviewed}

**Inorganic Activity Assessment**:

| Dimension | Presence | Summary of Evidence | Impact | Source(s) |
|:----------|:---------|:-------------------|:-------|:----------|
| M&A Transactions | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Equity Investments | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Asset Purchases | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Divestitures | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Strategic Alliances / JVs | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Licensing / Franchise Deals | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |

**Detailed Transaction Listings**:

### {Category Name}
**Presence**: Yes/No/Nil

{If Presence=Yes, provide chronological listing}

#### Transaction 1: {Acquired Company / Asset / Partner Name}
- **Date**: {Announcement date} | {Closing date}
- **Transaction Type**: {Acquisition / Investment / Alliance / etc.}
- **Description**: {Brief description of target and strategic rationale}
- **Financial Terms**: {Purchase price, structure, ownership %}
- **Strategic Rationale**: {Why this transaction supports growth strategy}
- **Impact Assessment**: Factor-in / On-going / Unclear
  - {Explanation of impact assessment}
  - {Revenue contribution, synergies, integration status}
- **Sources**: _(cite source filing in FR-050 format at runtime)_, _(cite source filing in FR-050 format at runtime)_

#### Transaction 2: {Name}
{Repeat structure for each transaction}

{Repeat for each category with Presence=Yes}

**Key Observations**:
- {Total count of inorganic activities across all categories}
- {Dominant inorganic growth approach: M&A, partnerships, etc.}
- {Evolution of strategy over 5 years: increasing/decreasing activity}
- {Current vs. historical impact: how much of growth is factored in}


## Mode: inorganic-growth-driver-execution-assessment

**Display name**: inorganic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_3_2.yaml -->

### Objective

Assess the execution progress of previously identified inorganic growth drivers
that are still in progress or have unclear impact.

For each inorganic activity with Impact=On-going or Unclear from task 3_3_1:
- Execution Status: [On Track / Behind Schedule / Ahead of Plan]
- Supporting Evidence: Integration milestones, synergy realization, management commentary
- Source Citations: Document references with proper format

Focus on:
- Integration progress (organizational, systems, customer retention)
- Synergy realization (revenue, cost, operational)
- Financial performance vs. expectations
- Timeline adherence to original plans

### Tool calls (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

### Output structure (per-mode)

- **quality_standards**:
  - citation_discipline
  - evidence_requirements
  - status_determination
  - temporal_accuracy
- **structure**: ## Inorganic Growth Driver Execution Progress Assessment

**Assessment Period**: {Most recent fiscal quarter, e.g., "2024 Q2"}
**Assessment Date**: {Latest earnings date used for analysis}

**Data Sources**:
- Latest Earnings Call: {Date and quarter}
- Most Recent 10-Q: {Filing date}
- Sell-Side Research: {List recent analyst reports reviewed}

**Execution Status Summary**:

| Growth Driver | Execution Status | Summary of Progress / Commentary | Source(s) |
|:--------------|:-----------------|:--------------------------------|:----------|
| M&A Transactions | On Track / Behind / Ahead | {Key integration progress and synergy realization} | {Citations} |
| Equity Investments | On Track / Behind / Ahead | {Commercial benefits and strategic value realization} | {Citations} |
| Strategic Alliances / JVs | On Track / Behind / Ahead | {Operational progress and revenue contribution} | {Citations} |
| Licensing Agreements | On Track / Behind / Ahead | {Royalty realization and technology access} | {Citations} |
| Asset Purchases | On Track / Behind / Ahead | {Capacity ramp and revenue contribution} | {Citations} |
| Divestitures | On Track / Behind / Ahead | {TSA completion and capital redeployment} | {Citations} |

**Detailed Execution Evidence**:

### {Transaction Name or Category}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Transaction** (from task 3_3_1):
{Brief recap: date, type, size, strategic rationale}

**Original Expectations**:
{Integration timeline, synergy targets, or other stated goals}

**Current Progress**:

#### Organizational Integration
- Evidence Point 1: {Leadership retention, employee metrics} _(cite source filing in FR-050 format at runtime)_
- Evidence Point 2: {Organizational structure changes} _(cite source filing in FR-050 format at runtime)_

#### Systems and Operations
- Evidence Point 1: {IT integration status, system cutover milestones} _(cite source filing in FR-050 format at runtime)_
- Evidence Point 2: {Process harmonization progress} _(cite source filing in FR-050 format at runtime)_

#### Commercial Integration
- Evidence Point 1: {Customer retention metrics} _(cite source filing in FR-050 format at runtime)_
- Evidence Point 2: {Cross-sell or revenue synergy progress} _(cite source filing in FR-050 format at runtime)_

#### Synergy Realization
- Revenue Synergies: {Quantified amount vs. target} _(cite source filing in FR-050 format at runtime)_
- Cost Synergies: {Quantified amount vs. target} _(cite source filing in FR-050 format at runtime)_
- Total Synergies: {$ realized YTD vs. full-year or cumulative target}

#### Financial Performance
- Revenue Contribution: {Acquired business revenue in quarter} _(cite source filing in FR-050 format at runtime)_
- Margin Impact: {Accretion/dilution to margins} _(cite source filing in FR-050 format at runtime)_
- EPS Impact: {Accretive/dilutive vs. guidance} _(cite source filing in FR-050 format at runtime)_

**Management Commentary**:
{Relevant quotes or summaries from earnings call} _(cite source filing in FR-050 format at runtime)_

**Analyst Perspective** (if available):
{Sell-side view on integration execution} _(cite source filing in FR-050 format at runtime)_

**Status Rationale**:
{Explanation of why this status was assigned based on evidence across dimensions}

{Repeat for each On-going/Unclear transaction}

**Overall Execution Assessment**:
- {Synthesize execution progress across all inorganic activities}
- {Note any patterns: most deals on track, specific areas of concern}
- {Highlight exceptional execution or significant challenges}
- {Assess management's overall M&A and integration capabilities}


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
