# growth-strategy — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: growth-strategy-assessment

**Display name**: growth-strategy-assessment

<!-- ported_from: references/prompts/3/3_1.yaml -->

**Focus**: Systematically analyze company's growth strategy by evaluating multiple data sources.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

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
- {Example: Product development programs mentioned in Q2 earnings call [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})}

### Inorganic Growth Indicators
- {List identified inorganic initiatives with citations}
- {Example: M&A transaction announced in 8-K filing [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})}

**Data Sources Analyzed**:
- {List key documents reviewed: 10-K, earnings calls, analyst reports}

**Temporal Scope**: {Specify analysis period, e.g., "FY23 10-K plus Q1-Q2 2024 earnings materials"}

### Mode: organic-growth-drivers-analysis

**Display name**: organic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_2_1.yaml -->

**Focus**: Systematically identify and extract organic growth drivers across 6 dimensions.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`

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
| Product | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Market | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Customer Retention | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Pricing | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Sales & Channel | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Marketing | Yes/No/Nil | {Brief description of initiatives} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |

**Detailed Evidence**:

### Product
{If Presence=Yes, provide detailed description}
- Initiative 1: {Description} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Initiative 2: {Description} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

{Repeat for each dimension with Presence=Yes}

**Key Observations**:
- {Synthesize overall organic growth approach}
- {Note any patterns or emphasis across dimensions}

### Mode: organic-growth-driver-execution-assessment

**Display name**: organic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_2_2.yaml -->

**Focus**: Assess the execution progress of previously identified organic growth drivers.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

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
| Product | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Market | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Customer Retention | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Pricing | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Sales & Channel | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Marketing | On Track / Behind / Ahead | {Key progress points and evidence} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |

**Detailed Execution Evidence**:

### {Dimension Name}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Initiative** (from task 3_2_1):
{Brief recap of initiative identified previously}

**Current Progress**:
- Evidence Point 1: {Description with metrics} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Evidence Point 2: {Description with metrics} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Management Commentary: {Relevant quote or summary} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

**Status Rationale**:
{Explanation of why this status was assigned based on evidence}

{Repeat for each dimension with Presence=Yes}

**Overall Execution Assessment**:
- {Synthesize execution progress across all organic growth drivers}
- {Note any patterns: most initiatives on track, specific areas of concern, etc.}
- {Highlight any dimension showing particularly strong or weak execution}

### Mode: inorganic-growth-drivers-analysis

**Display name**: inorganic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_3_1.yaml -->

**Focus**: Systematically identify and extract inorganic growth drivers over the past 5 years.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

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
| M&A Transactions | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Equity Investments | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Asset Purchases | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Divestitures | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Strategic Alliances / JVs | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Licensing / Franchise Deals | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |

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
- **Sources**: [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}), [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

#### Transaction 2: {Name}
{Repeat structure for each transaction}

{Repeat for each category with Presence=Yes}

**Key Observations**:
- {Total count of inorganic activities across all categories}
- {Dominant inorganic growth approach: M&A, partnerships, etc.}
- {Evolution of strategy over 5 years: increasing/decreasing activity}
- {Current vs. historical impact: how much of growth is factored in}

### Mode: inorganic-growth-driver-execution-assessment

**Display name**: inorganic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_3_2.yaml -->

**Focus**: Assess the execution progress of previously identified inorganic growth drivers.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

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
| M&A Transactions | On Track / Behind / Ahead | {Key integration progress and synergy realization} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Equity Investments | On Track / Behind / Ahead | {Commercial benefits and strategic value realization} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Strategic Alliances / JVs | On Track / Behind / Ahead | {Operational progress and revenue contribution} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Licensing Agreements | On Track / Behind / Ahead | {Royalty realization and technology access} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Asset Purchases | On Track / Behind / Ahead | {Capacity ramp and revenue contribution} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |
| Divestitures | On Track / Behind / Ahead | {TSA completion and capital redeployment} | [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N}) |

**Detailed Execution Evidence**:

### {Transaction Name or Category}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Transaction** (from task 3_3_1):
{Brief recap: date, type, size, strategic rationale}

**Original Expectations**:
{Integration timeline, synergy targets, or other stated goals}

**Current Progress**:

#### Organizational Integration
- Evidence Point 1: {Leadership retention, employee metrics} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Evidence Point 2: {Organizational structure changes} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

#### Systems and Operations
- Evidence Point 1: {IT integration status, system cutover milestones} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Evidence Point 2: {Process harmonization progress} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

#### Commercial Integration
- Evidence Point 1: {Customer retention metrics} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Evidence Point 2: {Cross-sell or revenue synergy progress} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

#### Synergy Realization
- Revenue Synergies: {Quantified amount vs. target} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Cost Synergies: {Quantified amount vs. target} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Total Synergies: {$ realized YTD vs. full-year or cumulative target}

#### Financial Performance
- Revenue Contribution: {Acquired business revenue in quarter} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- Margin Impact: {Accretion/dilution to margins} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
- EPS Impact: {Accretive/dilutive vs. guidance} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

**Management Commentary**:
{Relevant quotes or summaries from earnings call} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

**Analyst Perspective** (if available):
{Sell-side view on integration execution} [📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})

**Status Rationale**:
{Explanation of why this status was assigned based on evidence across dimensions}

{Repeat for each On-going/Unclear transaction}

**Overall Execution Assessment**:
- {Synthesize execution progress across all inorganic activities}
- {Note any patterns: most deals on track, specific areas of concern}
- {Highlight exceptional execution or significant challenges}
- {Assess management's overall M&A and integration capabilities}

<!-- END port-dimension-prompts methodology + modes -->
